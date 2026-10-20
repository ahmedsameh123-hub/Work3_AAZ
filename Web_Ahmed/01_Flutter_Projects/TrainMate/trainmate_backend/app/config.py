from pydantic_settings import BaseSettings, SettingsConfigDict

_DEV_JWT_SECRET = "dev-change-me"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    jwt_secret_key: str = _DEV_JWT_SECRET
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    # Comma-separated origins for browser clients; mobile apps ignore CORS.
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    database_url: str = "sqlite:///./trainmate.db"

    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    # llm_provider: auto | groq | openrouter
    llm_provider: str = "auto"
    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-4o-mini"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Keras weights directory (optional).
    ml_models_dir: str = ""

    app_name: str = "TrainMate"

    # SMTP — required for real inbox delivery. If smtp_host is empty, codes only appear in server logs.
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_use_tls: bool = True
    # Use True + port 465 for providers that need implicit SSL (some hosts); Gmail usually uses 587 + TLS above.
    smtp_use_ssl: bool = False

    # Resend (HTTPS API) — alternative to SMTP; free tier at https://resend.com
    # Use onboarding@resend.dev as "from" until you verify your own domain in Resend.
    resend_api_key: str = ""
    resend_from: str = "TrainMate <onboarding@resend.dev>"

    @property
    def smtp_ready(self) -> bool:
        return bool(
            (self.smtp_host or "").strip()
            and (self.smtp_user or "").strip()
            and (self.smtp_password or "").strip()
        )

    @property
    def resend_ready(self) -> bool:
        return bool((self.resend_api_key or "").strip())

    @property
    def email_delivery_ready(self) -> bool:
        return self.resend_ready or self.smtp_ready

    # When True, signup/resend may return verification_code in JSON for local dev without inbox.
    # Set EXPOSE_VERIFICATION_CODES=true in .env for local development only.
    expose_verification_codes: bool = False

    @property
    def cors_origin_list(self) -> list[str]:
        raw = (self.cors_origins or "").strip()
        if not raw or raw == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]

    @property
    def uses_dev_jwt_secret(self) -> bool:
        return self.jwt_secret_key == _DEV_JWT_SECRET


settings = Settings()
