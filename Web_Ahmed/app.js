// ==========================================================================
// Ahmed Sameh — Portfolio & Showcase Portal Logic
// Interactive Filtering, Lightbox Modal, Flutter Mockup Switcher & Dark Mode
// ==========================================================================

// TrainMate 16 App Screenshots List
const trainmateScreens = [
  { src: '05_Screenshots_and_Media/Mobile_Flutter_Previews/03_home.png', title: 'الشاشة الرئيسية اليومية (Home Hub)' },
  { src: '05_Screenshots_and_Media/Mobile_Flutter_Previews/04_workout_hub.png', title: 'مركز البرامج التدريبية (Workout Hub)' },
  { src: '05_Screenshots_and_Media/Mobile_Flutter_Previews/06_exercise_coaching.png', title: 'توجيهات وإرشادات الأداء الصحيح' },
  { src: '05_Screenshots_and_Media/Mobile_Flutter_Previews/07_exercise_live.png', title: 'البث الحي وتتبع نقاط الهيكل العظمي (Live Pose)' },
  { src: '05_Screenshots_and_Media/Mobile_Flutter_Previews/08_exercise_hud.png', title: 'واجهة العدادات المباشرة (Live HUD & Reps)' },
  { src: '05_Screenshots_and_Media/Mobile_Flutter_Previews/01_login.png', title: 'شاشة تسجيل الدخول والتوثيق (Auth)' },
  { src: '05_Screenshots_and_Media/Mobile_Flutter_Previews/05_exercise_setup.png', title: 'تهيئة الكاميرا وبدء الجلسة' },
  { src: '05_Screenshots_and_Media/Mobile_Flutter_Previews/09_profile.png', title: 'الملف الشخصي وإحصائيات التقدم' },
  { src: '05_Screenshots_and_Media/Mobile_Flutter_Previews/10_settings.png', title: 'إعدادات الحساب والتنبيهات' },
  { src: '05_Screenshots_and_Media/Mobile_Flutter_Previews/11_plan_settings.png', title: 'تخصيص الخطة الرياضية' },
  { src: '05_Screenshots_and_Media/Mobile_Flutter_Previews/12_plan_form.png', title: 'إضافة وتعديل جدول التمارين' },
  { src: '05_Screenshots_and_Media/Mobile_Flutter_Previews/13_app_settings.png', title: 'خيارات التطبيق والوضع الليلي' },
  { src: '05_Screenshots_and_Media/Mobile_Flutter_Previews/14_arabic.png', title: 'الدعم الكامل للغة العربية والـ RTL' },
  { src: '05_Screenshots_and_Media/Mobile_Flutter_Previews/15_chatbot.png', title: 'المدرب الذكي (AI Fitness Chatbot)' },
  { src: '05_Screenshots_and_Media/Mobile_Flutter_Previews/17_chat_response.png', title: 'إجابات وتحليلات المدرب الذكي' },
  { src: '05_Screenshots_and_Media/Mobile_Flutter_Previews/Screenshot_1781528690.png', title: 'واجهة إضافية للتطبيق' }
];

let currentMockupIndex = 0;
let modalGallery = [];
let currentModalIndex = 0;

document.addEventListener('DOMContentLoaded', () => {
  initFilters();
  initTheme();
  initKeyboardNav();
  initStats();
});

// --------------------------------------------------------------------------
// 1. Projects Category Filtering
// --------------------------------------------------------------------------
function initFilters() {
  const filterBtns = document.querySelectorAll('.filter-btn');
  const cards = document.querySelectorAll('.project-card');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filter = btn.getAttribute('data-filter');

      cards.forEach(card => {
        const category = card.getAttribute('data-category');
        if (filter === 'all' || category === filter) {
          card.style.display = 'flex';
          setTimeout(() => { card.style.opacity = '1'; card.style.transform = 'translateY(0)'; }, 20);
        } else {
          card.style.opacity = '0';
          card.style.transform = 'translateY(15px)';
          setTimeout(() => { card.style.display = 'none'; }, 200);
        }
      });
    });
  });
}

// --------------------------------------------------------------------------
// 2. Phone Mockup Interactive Switcher
// --------------------------------------------------------------------------
function nextMockupScreen() {
  currentMockupIndex = (currentMockupIndex + 1) % trainmateScreens.length;
  const mockupImg = document.getElementById('mockupScreen');
  if (mockupImg) {
    mockupImg.style.opacity = '0.3';
    setTimeout(() => {
      mockupImg.src = trainmateScreens[currentMockupIndex].src;
      mockupImg.alt = trainmateScreens[currentMockupIndex].title;
      mockupImg.style.opacity = '1';
    }, 150);
  }
}

// Auto change mockup screen every 4 seconds
setInterval(() => {
  const modal = document.getElementById('screenshotModal');
  if (!modal || !modal.classList.contains('open')) {
    nextMockupScreen();
  }
}, 4500);

// --------------------------------------------------------------------------
// 3. Lightbox Screenshot Modal
// --------------------------------------------------------------------------
function openScreenshotModal(imgSrc, title) {
  modalGallery = [{ src: imgSrc, title: title }];
  currentModalIndex = 0;
  displayModalImage();
}

function openFeaturedGallery() {
  modalGallery = [...trainmateScreens];
  currentModalIndex = 0;
  displayModalImage();
}

function displayModalImage() {
  const modal = document.getElementById('screenshotModal');
  const modalImg = document.getElementById('modalImg');
  const modalTitle = document.getElementById('modalTitle');
  const modalCounter = document.getElementById('modalCounter');
  const prevBtn = document.getElementById('modalPrev');
  const nextBtn = document.getElementById('modalNext');

  if (!modal || modalGallery.length === 0) return;

  const current = modalGallery[currentModalIndex];
  modalImg.src = current.src;
  modalTitle.textContent = current.title;
  modalCounter.textContent = `${currentModalIndex + 1} / ${modalGallery.length}`;

  if (modalGallery.length > 1) {
    prevBtn.style.display = 'inline-block';
    nextBtn.style.display = 'inline-block';
    modalCounter.style.display = 'inline-block';
  } else {
    prevBtn.style.display = 'none';
    nextBtn.style.display = 'none';
    modalCounter.style.display = 'none';
  }

  modal.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeScreenshotModal(event) {
  if (event.target.id === 'screenshotModal') {
    closeScreenshotModalDirect();
  }
}

function closeScreenshotModalDirect() {
  const modal = document.getElementById('screenshotModal');
  if (modal) {
    modal.classList.remove('open');
    document.body.style.overflow = 'auto';
  }
}

function prevModalImg() {
  if (modalGallery.length <= 1) return;
  currentModalIndex = (currentModalIndex - 1 + modalGallery.length) % modalGallery.length;
  displayModalImage();
}

function nextModalImg() {
  if (modalGallery.length <= 1) return;
  currentModalIndex = (currentModalIndex + 1) % modalGallery.length;
  displayModalImage();
}

function initKeyboardNav() {
  document.addEventListener('keydown', (e) => {
    const modal = document.getElementById('screenshotModal');
    if (modal && modal.classList.contains('open')) {
      if (e.key === 'Escape') closeScreenshotModalDirect();
      if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
        if (e.key === 'ArrowRight') prevModalImg();
        else nextModalImg();
      }
    }
  });
}

// --------------------------------------------------------------------------
// 4. Dark / Light Theme Toggle
// --------------------------------------------------------------------------
function initTheme() {
  const themeToggle = document.getElementById('themeToggle');
  const savedTheme = localStorage.getItem('ahmed_theme');

  if (savedTheme === 'light') {
    document.body.classList.add('light-mode');
    if (themeToggle) themeToggle.textContent = '☀️';
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      document.body.classList.toggle('light-mode');
      const isLight = document.body.classList.contains('light-mode');
      themeToggle.textContent = isLight ? '☀️' : '🌙';
      localStorage.setItem('ahmed_theme', isLight ? 'light' : 'dark');
    });
  }
}

// --------------------------------------------------------------------------
// 5. Dynamic Stats Counter
// --------------------------------------------------------------------------
function initStats() {
  const statWeb = document.getElementById('statWeb');
  const webCards = document.querySelectorAll('.project-card[data-category="web"]');
  if (statWeb && webCards.length > 0) {
    statWeb.textContent = `${webCards.length}+`;
  }
}
