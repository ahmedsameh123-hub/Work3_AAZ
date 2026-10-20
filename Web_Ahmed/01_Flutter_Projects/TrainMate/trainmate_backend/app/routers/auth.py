from datetime import datetime, timedelta, timezone

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.email_delivery import send_password_reset_email, send_verification_email
from app.models import User, UserProfile
from app.rate_limit import enforce_rate_limit
from app.schemas import (
    ForgotPasswordRequest,
    ResendVerificationRequest,
    ResetPasswordRequest,
    Token,
    UserLogin,
    UserOut,
    UserRegister,
    UserRegisterOut,
    VerifyEmailRequest,
    VerifyEmailResponse,
)
from app.security import (
    create_access_token,
    hash_password,
    verify_email_code,
    verify_password,
)
from app.verification import (
    enforce_password_reset_cooldown,
    enforce_resend_cooldown,
    find_user_by_delivered_email,
    issue_password_reset_code,
    issue_verification_code,
)

router = APIRouter(prefix="/auth", tags=["auth"])
_log = logging.getLogger("uvicorn.error")

_AUTH_FAIL = "Invalid email or password"
_VERIFY_FAIL = "Invalid code or email"


def _user_out(u: User) -> UserOut:
    return UserOut(
        id=u.id,
        email=u.email,
        name=u.name,
        email_verified=u.email_verified,
        phone=u.phone,
        pending_email=u.pending_email,
    )


def _dev_verification_response(code: str) -> dict:
    out: dict = {"status": "sent", "delivery": "in_app"}
    if settings.expose_verification_codes:
        out["verification_code"] = code
    return out


@router.post("/register", response_model=UserRegisterOut, status_code=status.HTTP_201_CREATED)
def register(body: UserRegister, request: Request, db: Session = Depends(get_db)):
    enforce_rate_limit(request, scope="register", max_attempts=8, window_seconds=900)
    em = body.email.lower().strip()
    exists = db.scalar(select(User).where(User.email == em))
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=em,
        hashed_password=hash_password(body.password),
        name=body.name.strip() if body.name else None,
        email_verified=False,
    )
    db.add(user)
    db.flush()

    profile = UserProfile(user_id=user.id)
    db.add(profile)

    code = issue_verification_code(user, db)
    try:
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create account",
        )

    if not settings.email_delivery_ready and not settings.expose_verification_codes:
        db.delete(user)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email delivery not configured. Set RESEND/SMTP or EXPOSE_VERIFICATION_CODES=true.",
        )

    try:
        delivered = send_verification_email(em, code)
    except Exception as exc:
        u2 = db.get(User, user.id)
        if u2 is not None:
            db.delete(u2)
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not send verification email. Try again later.",
        ) from exc

    if delivered:
        return UserRegisterOut(
            **{**_user_out(user).model_dump(), "verification_code": None, "access_token": None}
        )

    if not settings.expose_verification_codes:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not send verification email. Try again later.",
        )

    _log.warning("Email NOT delivered for %s — verification code available in app (dev mode).", em)
    return UserRegisterOut(
        **{
            **_user_out(user).model_dump(),
            "verification_code": code,
            "access_token": None,
        }
    )


@router.post("/login", response_model=Token)
def login(body: UserLogin, request: Request, db: Session = Depends(get_db)):
    enforce_rate_limit(request, scope="login", max_attempts=12, window_seconds=900)
    em = body.email.lower().strip()
    user = db.scalar(select(User).where(User.email == em))
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_AUTH_FAIL,
        )
    if not user.email_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="EMAIL_NOT_VERIFIED")

    token = create_access_token(subject=user.email, user_id=user.id)
    return Token(access_token=token)


@router.post("/verify-email", response_model=VerifyEmailResponse)
def verify_email(body: VerifyEmailRequest, request: Request, db: Session = Depends(get_db)):
    enforce_rate_limit(request, scope="verify-email", max_attempts=20, window_seconds=900)
    em = body.email.lower().strip()
    user = find_user_by_delivered_email(db, em)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_VERIFY_FAIL)

    if user.verification_code_hash is None or user.verification_expires_at is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_VERIFY_FAIL)

    exp = user.verification_expires_at
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > exp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification code expired")

    if not verify_email_code(body.code, user.verification_code_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_VERIFY_FAIL)

    if user.pending_email == em:
        conflict = db.scalar(select(User).where(User.email == em, User.id != user.id))
        if conflict:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        user.email = em
        user.pending_email = None
    elif user.email == em and not user.email_verified:
        pass
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_VERIFY_FAIL)

    user.email_verified = True
    user.verification_code_hash = None
    user.verification_expires_at = None

    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.email, user_id=user.id)
    return VerifyEmailResponse(access_token=token, user=_user_out(user))


@router.post("/resend-verification", status_code=status.HTTP_202_ACCEPTED)
def resend_verification(body: ResendVerificationRequest, request: Request, db: Session = Depends(get_db)):
    enforce_rate_limit(request, scope="resend-verification", max_attempts=10, window_seconds=900)
    em = body.email.lower().strip()
    user = find_user_by_delivered_email(db, em)
    if user is None:
        return {"status": "sent", "delivery": "email"}

    if user.email == em and user.email_verified and not user.pending_email:
        return {"status": "sent", "delivery": "email"}

    if user.pending_email == em:
        target = em
    elif user.email == em and not user.email_verified:
        target = em
    else:
        return {"status": "sent", "delivery": "email"}

    try:
        enforce_resend_cooldown(user)
    except HTTPException:
        return {"status": "sent", "delivery": "email"}

    code = issue_verification_code(user, db)
    db.commit()
    try:
        delivered = send_verification_email(target, code)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not send verification email. Try again later.",
        ) from exc

    if delivered:
        return {"status": "sent", "delivery": "email"}
    _log.warning("Resend email NOT delivered for %s — dev in-app delivery.", target)
    return _dev_verification_response(code)


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
def forgot_password(body: ForgotPasswordRequest, request: Request, db: Session = Depends(get_db)):
    """
    Sends a 6-digit reset code to the email (if the account exists).
    Response is always generic so emails cannot be enumerated.
    """
    enforce_rate_limit(request, scope="forgot-password", max_attempts=10, window_seconds=900)
    em = body.email.lower().strip()
    user = db.scalar(select(User).where(User.email == em))
    if user is None:
        return {"status": "accepted"}

    try:
        enforce_password_reset_cooldown(user)
        code = issue_password_reset_code(user, db)
        db.commit()
    except HTTPException:
        db.rollback()
        return {"status": "accepted"}
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not start password reset. Try again later.",
        ) from None

    try:
        delivered = send_password_reset_email(em, code)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not send reset email. Configure SMTP or check server logs.",
        ) from exc

    out: dict = {"status": "accepted"}
    if not delivered and settings.expose_verification_codes:
        out["password_reset_code"] = code
        _log.warning("Password reset NOT delivered for %s — dev in-app delivery.", em)
    return out


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(body: ResetPasswordRequest, request: Request, db: Session = Depends(get_db)):
    enforce_rate_limit(request, scope="reset-password", max_attempts=20, window_seconds=900)
    em = body.email.lower().strip()
    user = db.scalar(select(User).where(User.email == em))
    if user is None or not user.password_reset_code_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_VERIFY_FAIL,
        )

    exp = user.password_reset_expires_at
    if exp is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_VERIFY_FAIL)
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > exp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset code expired")

    if not verify_email_code(body.code, user.password_reset_code_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_VERIFY_FAIL)

    user.hashed_password = hash_password(body.new_password)
    user.password_reset_code_hash = None
    user.password_reset_expires_at = None
    db.commit()
    return {"status": "ok"}
