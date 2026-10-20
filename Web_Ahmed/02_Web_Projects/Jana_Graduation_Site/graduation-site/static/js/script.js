/* ==========================================================
   Graduation site - script.js
   Fetches /api/site (texts + photos) and builds the page.
   ========================================================== */
(() => {
  'use strict';

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const rand = (a, b) => a + Math.random() * (b - a);
  const hasArabic = (s) => /[\u0600-\u06FF]/.test(s || '');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const list = (x) => (Array.isArray(x) ? x : []);

  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
  window.scrollTo(0, 0);

  let DATA = null; // response from /api/site
  let CFG = null;  // config with {placeholders} filled
  let isRTL = true;
  let opened = false;

  /* ---------------------------------------------------------
     Helpers
     --------------------------------------------------------- */
  function make(tag, className, text) {
    const n = document.createElement(tag);
    if (className) n.className = className;
    if (text != null) n.textContent = text;
    return n;
  }

  function setText(sel, text) {
    const n = $(sel);
    if (n) n.textContent = text == null ? '' : text;
    return n;
  }

  // Replace {name} {from} {year} {university} {major} everywhere in the config
  function format(value, vars) {
    if (typeof value === 'string') return value.replace(/\{(\w+)\}/g, (m, k) => (k in vars ? vars[k] : m));
    if (Array.isArray(value)) return value.map((v) => format(v, vars));
    if (value && typeof value === 'object') {
      const out = {};
      for (const k in value) out[k] = format(value[k], vars);
      return out;
    }
    return value;
  }

  // one shared, rAF-throttled scroll handler
  const scrollFns = [];
  let scrollTicking = false;
  const onScroll = (fn) => scrollFns.push(fn);
  const runScroll = () => scrollFns.forEach((f) => f());
  window.addEventListener('scroll', () => {
    if (scrollTicking) return;
    scrollTicking = true;
    requestAnimationFrame(() => { runScroll(); scrollTicking = false; });
  }, { passive: true });
  window.addEventListener('resize', runScroll);

  /* ---------------------------------------------------------
     FX: confetti + tossed graduation caps (canvas)
     --------------------------------------------------------- */
  const FX = (() => {
    const canvas = $('#fx');
    const ctx = canvas.getContext('2d');
    const COLORS = ['#f7e5ae', '#e6bf6a', '#f2b5c4', '#d8688a', '#ffffff', '#9fb0ff'];
    let w = 0, h = 0, dpr = 1;
    let parts = [];
    let running = false;
    let last = 0;
    let rainUntil = 0;

    function resize() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = window.innerWidth; h = window.innerHeight;
      canvas.width = w * dpr; canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    window.addEventListener('resize', resize);
    resize();

    function start() {
      if (running) return;
      running = true;
      last = performance.now();
      requestAnimationFrame(tick);
    }

    function confettiPiece(x, y, vx, vy, decay) {
      return {
        type: Math.random() < 0.28 ? 'dot' : 'rect',
        x, y, vx, vy,
        w: rand(6, 11), h: rand(4, 7),
        rot: rand(0, 6.28), vr: rand(-0.25, 0.25),
        wob: rand(0, 6.28), wobSpeed: rand(0.05, 0.2),
        color: COLORS[(Math.random() * COLORS.length) | 0],
        life: 1, decay, drag: 0.985, g: 0.18,
      };
    }

    function burst(x, y, n = 110, spread = 2.4) {
      if (reduceMotion) return;
      for (let i = 0; i < n; i++) {
        const a = -Math.PI / 2 + (Math.random() - 0.5) * spread;
        const s = rand(5, 13);
        parts.push(confettiPiece(x, y, Math.cos(a) * s, Math.sin(a) * s, rand(0.004, 0.009)));
      }
      start();
    }

    function capToss(n = 12) {
      if (reduceMotion) return;
      for (let i = 0; i < n; i++) {
        const g = 0.2;
        const apex = h * rand(0.5, 0.88);
        parts.push({
          type: 'cap',
          x: rand(w * 0.06, w * 0.94), y: h + 50,
          vx: rand(-2.2, 2.2), vy: -Math.sqrt(2 * g * apex),
          size: rand(38, 62), rot: rand(-0.6, 0.6), vr: rand(-0.07, 0.07),
          rose: Math.random() < 0.35,
          life: 1, decay: 0, drag: 1, g,
          delay: rand(0, 380),
        });
      }
      start();
    }

    function rain(ms = 3500) {
      if (reduceMotion) return;
      rainUntil = performance.now() + ms;
      start();
    }

    function celebrate() {
      capToss(10);
      burst(w * 0.15, h * 0.95, 90, 1.5);
      burst(w * 0.85, h * 0.95, 90, 1.5);
      burst(w * 0.5, h * 0.7, 80, 2.8);
      rain(3200);
    }

    function drawCap(p) {
      const s = p.size;
      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.rotate(p.rot);
      ctx.scale(s, s);
      const hi = p.rose ? '#f8d4de' : '#f7e5ae';
      const mid = p.rose ? '#d8688a' : '#b8893a';
      // skull cap (under the board)
      ctx.fillStyle = mid;
      ctx.beginPath();
      ctx.moveTo(-0.3, 0.04); ctx.lineTo(-0.3, 0.22);
      ctx.quadraticCurveTo(0, 0.4, 0.3, 0.22); ctx.lineTo(0.3, 0.04); ctx.closePath();
      ctx.fill();
      // board
      ctx.fillStyle = hi;
      ctx.beginPath();
      ctx.moveTo(0, -0.26); ctx.lineTo(0.62, 0.02); ctx.lineTo(0, 0.3); ctx.lineTo(-0.62, 0.02); ctx.closePath();
      ctx.fill();
      // tassel
      ctx.strokeStyle = mid; ctx.lineWidth = 0.03; ctx.lineCap = 'round';
      ctx.beginPath(); ctx.moveTo(0, 0.02); ctx.lineTo(0.46, 0.13); ctx.lineTo(0.46, 0.4); ctx.stroke();
      ctx.fillStyle = mid; ctx.fillRect(0.43, 0.38, 0.06, 0.12);
      ctx.restore();
    }

    function drawConfetti(p) {
      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.rotate(p.rot);
      ctx.globalAlpha = clamp(p.life * 1.6, 0, 1);
      ctx.fillStyle = p.color;
      if (p.type === 'dot') {
        ctx.beginPath(); ctx.arc(0, 0, p.w * 0.35, 0, 6.283); ctx.fill();
      } else {
        const flutter = 0.35 + 0.65 * Math.abs(Math.cos(p.wob));
        ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h * flutter);
      }
      ctx.restore();
    }

    function tick(now) {
      const dt = Math.min(40, now - last);
      last = now;
      const k = dt / 16.667;
      ctx.clearRect(0, 0, w, h);

      if (now < rainUntil) {
        const n = Math.ceil(2 * k);
        for (let i = 0; i < n; i++) {
          parts.push(confettiPiece(rand(0, w), -12, rand(-1.2, 1.2), rand(1, 3.2), rand(0.0015, 0.003)));
        }
      }

      for (const p of parts) {
        if (p.delay > 0) { p.delay -= dt; continue; }
        p.vx *= Math.pow(p.drag, k);
        p.vy = p.vy * Math.pow(p.drag, k) + p.g * k;
        p.x += p.vx * k; p.y += p.vy * k;
        p.rot += p.vr * k;
        if (p.wob !== undefined) p.wob += p.wobSpeed * k;
        p.life -= p.decay * k;
        if (p.type === 'cap') drawCap(p); else drawConfetti(p);
      }

      parts = parts.filter((p) => {
        if (p.type === 'cap') return !(p.y > h + 90 && p.vy > 0);
        return p.life > 0 && p.y < h + 40;
      });

      if (parts.length || now < rainUntil) requestAnimationFrame(tick);
      else { running = false; ctx.clearRect(0, 0, w, h); }
    }

    return { burst, capToss, rain, celebrate };
  })();

  /* ---------------------------------------------------------
     Ambient sparkles (very light, behind the content)
     --------------------------------------------------------- */
  function startSparkles() {
    if (reduceMotion) return;
    const c = $('#sparkles');
    const ctx = c.getContext('2d');
    let w = 0, h = 0, dpr = 1, parts = [];

    const spawn = (anywhere) => ({
      x: Math.random() * w, y: anywhere ? Math.random() * h : h + 10,
      r: rand(0.4, 1.9), vy: -rand(0.04, 0.2), vx: rand(-0.05, 0.05),
      ph: rand(0, 6.28), sp: rand(0.0006, 0.002), gold: Math.random() < 0.7,
    });
    const resize = () => {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = window.innerWidth; h = window.innerHeight;
      c.width = w * dpr; c.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const n = clamp(Math.round((w * h) / 26000), 16, 44);
      parts = Array.from({ length: n }, () => spawn(true));
    };
    window.addEventListener('resize', resize);
    resize();

    const loop = (t) => {
      ctx.clearRect(0, 0, w, h);
      for (let i = 0; i < parts.length; i++) {
        const p = parts[i];
        p.x += p.vx; p.y += p.vy;
        if (p.y < -10) parts[i] = spawn(false);
        ctx.globalAlpha = 0.22 + 0.45 * (0.5 + 0.5 * Math.sin(t * p.sp + p.ph));
        ctx.fillStyle = p.gold ? '#f7e5ae' : '#f2b5c4';
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 6.283); ctx.fill();
      }
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  }

  /* ---------------------------------------------------------
     Render sections from config
     --------------------------------------------------------- */
  function renderIntro() {
    setText('#intro-line', CFG.intro?.line);
    setText('#open-btn-text', CFG.intro?.button);
  }

  function renderHero() {
    const kicker = setText('#hero-kicker', CFG.hero?.kicker);
    if (kicker && !hasArabic(kicker.textContent)) kicker.classList.add('tracked');

    const title = setText('#hero-title', CFG.hero?.title);
    if (title) title.classList.add('gold-text');
    setText('#hero-name', CFG.her_name);
    setText('#hero-sub', CFG.hero?.subtitle);
    setText('#chip-uni', CFG.university);
    setText('#chip-major', CFG.major);
    setText('#scroll-hint-text', CFG.hero?.scroll_hint);

    const img = $('#hero-img');
    if (DATA.hero_url) {
      img.style.backgroundImage = `url("${DATA.hero_url}")`;
      img.style.backgroundPosition = CFG.hero?.photo_focus || '50% 30%';
    } else {
      img.classList.add('is-empty');
      img.textContent = [...(CFG.her_name || '')][0] || '\u2605';
      console.info('[hero] No hero photo found. Put one at static/images/hero.jpg');
    }
    $('#hero-frame').setAttribute('aria-label', CFG.her_name || '');

    $('#hero-frame').addEventListener('click', (e) => FX.burst(e.clientX, e.clientY, 70, 3.2));
  }

  function countUp(el, target, dur = 1600) {
    if (reduceMotion) { el.textContent = target; return; }
    const t0 = performance.now();
    const step = (now) => {
      const p = clamp((now - t0) / dur, 0, 1);
      el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  function renderJourney() {
    const j = CFG.journey || {};
    setText('#journey-title', j.title);
    setText('#journey-sub', j.subtitle);

    // stats (count up once when visible)
    const stats = $('#stats');
    stats.textContent = '';
    const nums = [];
    list(j.stats).forEach((s) => {
      const box = make('div', 'stat');
      const num = make('span', 'stat__num gold-text', '0');
      nums.push([num, Number(s.value) || 0]);
      box.append(num, make('span', 'stat__label', s.label));
      stats.append(box);
    });
    if (nums.length) {
      const io = new IntersectionObserver((entries) => {
        if (entries.some((e) => e.isIntersecting)) {
          nums.forEach(([el, v]) => countUp(el, v));
          io.disconnect();
        }
      }, { threshold: 0.4 });
      io.observe(stats);
    }

    // timeline (line fills as you scroll)
    const tl = $('#timeline');
    tl.textContent = '';
    const fill = make('div', 'timeline__fill');
    tl.append(fill);
    list(j.items).forEach((it) => {
      const li = make('li', 'tl-item');
      li.append(make('span', 'tl-dot'), make('div', 'tl-year', it.year), make('h3', 'tl-title', it.title), make('p', 'tl-text', it.text));
      tl.append(li);
    });
    const items = $$('.tl-item', tl);
    onScroll(() => {
      const mid = window.innerHeight * 0.58;
      const rect = tl.getBoundingClientRect();
      fill.style.height = clamp(mid - rect.top - 8, 0, Math.max(0, rect.height - 8)) + 'px';
      items.forEach((li) => {
        const d = $('.tl-dot', li).getBoundingClientRect();
        li.classList.toggle('is-reached', d.top + 12 < mid);
      });
    });
  }

  /* ----- gallery + lightbox ----- */
  const lb = {
    el: $('#lightbox'), img: $('#lb-img'), cap: $('#lb-caption'), count: $('#lb-count'),
    i: 0, isOpen: false, tx: 0,
  };
  const captionOf = (item) => (CFG.gallery?.captions || {})[item.name] || '';

  function lbShow(i) {
    const items = DATA.gallery;
    if (!items.length) return;
    lb.i = (i + items.length) % items.length;
    const it = items[lb.i];
    const c = captionOf(it);
    lb.img.src = it.src;
    lb.img.alt = c;
    lb.cap.textContent = c;
    lb.count.textContent = `${lb.i + 1} / ${items.length}`;
  }
  function lbOpen(i) {
    lb.el.hidden = false; lb.isOpen = true;
    document.body.classList.add('is-locked');
    lbShow(i);
    $('.lb__close').focus({ preventScroll: true });
  }
  function lbClose() {
    lb.el.hidden = true; lb.isOpen = false;
    document.body.classList.remove('is-locked');
  }
  // left button = "next" in RTL, "previous" in LTR (and the opposite on the right)
  const lbLeft = () => lbShow(lb.i + (isRTL ? 1 : -1));
  const lbRight = () => lbShow(lb.i + (isRTL ? -1 : 1));

  function setupLightbox() {
    $('.lb__close').addEventListener('click', lbClose);
    $('.lb__prev').addEventListener('click', lbLeft);
    $('.lb__next').addEventListener('click', lbRight);
    lb.el.addEventListener('click', (e) => { if (e.target === lb.el) lbClose(); });
    document.addEventListener('keydown', (e) => {
      if (!lb.isOpen) return;
      if (e.key === 'Escape') lbClose();
      else if (e.key === 'ArrowLeft') lbLeft();
      else if (e.key === 'ArrowRight') lbRight();
    });
    lb.el.addEventListener('touchstart', (e) => { lb.tx = e.changedTouches[0].clientX; }, { passive: true });
    lb.el.addEventListener('touchend', (e) => {
      const dx = e.changedTouches[0].clientX - lb.tx;
      if (Math.abs(dx) < 50) return;
      if (dx < 0) lbRight(); else lbLeft(); // swipe left = what the right button does
    }, { passive: true });
  }

  function renderGallery() {
    setText('#gallery-title', CFG.gallery?.title);
    setText('#gallery-sub', CFG.gallery?.subtitle);
    const grid = $('#gallery-grid');
    grid.textContent = '';
    const items = DATA.gallery;

    if (!items.length) {
      console.info('[gallery] No photos found. Put photos in static/images/gallery/');
      [4 / 5, 1, 3 / 4, 5 / 4, 4 / 5, 1].forEach((r) => {
        const d = make('div', 'g-item g-item--empty', '\u2726');
        d.style.aspectRatio = String(r);
        grid.append(d);
      });
      return;
    }

    items.forEach((it, i) => {
      const cap = captionOf(it);
      const fig = make('figure', 'g-item');
      fig.tabIndex = 0;
      fig.setAttribute('role', 'button');
      fig.setAttribute('aria-label', cap || `${i + 1}`);
      if (it.width && it.height) fig.style.aspectRatio = `${it.width} / ${it.height}`;

      const img = new Image();
      img.loading = 'lazy';
      img.decoding = 'async';
      img.alt = cap;
      const done = () => fig.classList.add('is-loaded');
      img.addEventListener('load', done);
      img.addEventListener('error', done);
      img.src = it.src;
      if (img.complete && img.naturalWidth) done();

      fig.append(img);
      if (cap) fig.append(make('figcaption', '', cap));
      fig.addEventListener('click', () => lbOpen(i));
      fig.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); lbOpen(i); } });
      grid.append(fig);
    });
  }

  function renderReasons() {
    const r = CFG.reasons || {};
    setText('#reasons-title', r.title);
    setText('#reasons-sub', r.subtitle);
    const grid = $('#reasons-grid');
    grid.textContent = '';
    list(r.items).forEach((it) => {
      const card = make('div', 'flip');
      card.tabIndex = 0;
      card.setAttribute('role', 'button');
      card.setAttribute('aria-pressed', 'false');
      const inner = make('div', 'flip__inner');
      const front = make('div', 'flip__face flip__front');
      front.append(make('div', 'flip__icon', it.icon), make('div', 'flip__title', it.title));
      const back = make('div', 'flip__face flip__back');
      back.append(make('p', '', it.text));
      inner.append(front, back);
      card.append(inner);
      const toggle = () => {
        const on = card.classList.toggle('is-flipped');
        card.setAttribute('aria-pressed', String(on));
      };
      card.addEventListener('click', toggle);
      card.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); } });
      grid.append(card);
    });
  }

  function renderLetter() {
    const l = CFG.letter || {};
    setText('#letter-title', l.title);
    setText('#letter-greeting', l.greeting);
    const body = $('#letter-body');
    body.textContent = '';
    list(l.paragraphs).forEach((p) => body.append(make('p', '', p)));
    setText('#letter-closing', l.closing);
    setText('#letter-signature', l.signature);
    setText('#wax-letter', [...(CFG.from_name || '')][0] || '\u2665');
  }

  function renderFinale() {
    const f = CFG.finale || {};
    const title = setText('#finale-title', f.title);
    if (title) title.classList.add('gold-text');
    setText('#finale-text', f.text);
    setText('#celebrate-text', f.button);
    setText('#footer', CFG.footer);

    $('#celebrate-btn').addEventListener('click', () => FX.celebrate());

    // one automatic celebration the first time she reaches the end
    const io = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) {
        FX.rain(3600);
        FX.capToss(8);
        io.disconnect();
      }
    }, { threshold: 0.6 });
    io.observe($('#finale-title'));
  }

  /* ---------------------------------------------------------
     Progress bar
     --------------------------------------------------------- */
  function setupProgress() {
    const bar = $('#progress');
    onScroll(() => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.transform = `scaleX(${max > 0 ? clamp(window.scrollY / max, 0, 1) : 0})`;
    });
  }

  /* ---------------------------------------------------------
     Music + opening
     --------------------------------------------------------- */
  let audio = null;
  function setupMusic() {
    if (!DATA.music_url) return;
    audio = new Audio(DATA.music_url);
    audio.loop = true;
    audio.volume = 0.6;
    audio.preload = 'auto';
    const btn = $('#music-toggle');
    const sync = () => {
      const playing = !audio.paused;
      btn.classList.toggle('is-playing', playing);
      btn.setAttribute('aria-pressed', String(playing));
    };
    audio.addEventListener('play', sync);
    audio.addEventListener('pause', sync);
    btn.addEventListener('click', () => { if (audio.paused) audio.play().catch(() => {}); else audio.pause(); });
  }

  function openSurprise() {
    if (opened) return;
    opened = true;
    $('#intro').classList.add('is-open');
    document.body.classList.remove('is-locked');
    document.body.classList.add('is-ready');
    window.scrollTo(0, 0);

    if (audio) {
      audio.play().catch(() => {});
      $('#music-toggle').hidden = false;
    }
    setTimeout(() => {
      FX.capToss(14);
      FX.burst(window.innerWidth / 2, window.innerHeight * 0.6, 120, 2.6);
    }, 450);
    setTimeout(() => { $('#intro').hidden = true; runScroll(); }, 1800);
  }

  /* ---------------------------------------------------------
     Boot
     --------------------------------------------------------- */
  function showError(msg) {
    const box = $('#load-error');
    box.hidden = false;
    box.textContent = msg;
    $('#open-btn').hidden = true;
    $('#intro-line').textContent = '';
  }

  async function boot() {
    try {
      const res = await fetch('/api/site', { cache: 'no-store' });
      const json = await res.json();
      if (!res.ok) throw new Error(json.error || 'Server error');
      DATA = json;
    } catch (err) {
      showError(err.message || String(err));
      return;
    }

    const raw = DATA.config;
    CFG = format(raw, {
      name: raw.her_name || '', from: raw.from_name || '', year: raw.graduation_year || '',
      university: raw.university || '', major: raw.major || '',
    });

    document.documentElement.lang = CFG.lang || 'ar';
    document.documentElement.dir = CFG.dir || 'rtl';
    isRTL = document.documentElement.dir === 'rtl';
    document.title = CFG.page_title || document.title;

    renderIntro();
    renderHero();
    renderJourney();
    renderGallery();
    renderReasons();
    renderLetter();
    renderFinale();
    setupLightbox();
    setupProgress();
    setupMusic();
    startSparkles();
    runScroll();

    $('#open-btn').addEventListener('click', openSurprise);
    $('#open-btn').focus({ preventScroll: true });
  }

  boot();
})();
