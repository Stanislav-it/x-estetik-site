(function () {
  // ---------------- Search filter on product list pages ----------------
  const input = document.getElementById('searchInput');
  const grid = document.getElementById('productsGrid');
  const count = document.getElementById('resultsCount');
  const noResults = document.getElementById('noResults');

  function filter() {
    if (!input || !grid) return;
    const q = (input.value || '').trim().toLowerCase();
    const cards = Array.from(grid.querySelectorAll('.product-card'));
    let shown = 0;

    cards.forEach((c) => {
      const name = (c.getAttribute('data-name') || '').toLowerCase();
      const ok = !q || name.includes(q);
      c.classList.toggle('hidden', !ok);
      if (ok) shown += 1;
    });

    if (count) count.textContent = String(shown);
    if (noResults) noResults.classList.toggle('hidden', shown !== 0);
  }

  if (input && grid) {
    input.addEventListener('input', filter);
    filter();
  }

  
  // ---------------- Mobile menu (mm-*) ----------------
  const mmRoot = document.getElementById('mobileMenuRoot');
  const mmBtn = document.getElementById('mobileMenuBtn');
  const mmClose = document.getElementById('mobileMenuClose');
  const mmBackdrop = document.getElementById('mobileMenuBackdrop');
  const mmPanel = document.getElementById('mobileMenu');

  function mmOpen() {
    if (!mmRoot) return;
    mmRoot.classList.add('open');
    mmRoot.setAttribute('aria-hidden', 'false');
    if (mmBtn) mmBtn.setAttribute('aria-expanded', 'true');
    document.documentElement.style.overflow = 'hidden';
    document.body.style.overflow = 'hidden';
  }
  function mmCloseFn() {
    if (!mmRoot) return;
    mmRoot.classList.remove('open');
    mmRoot.setAttribute('aria-hidden', 'true');
    if (mmBtn) mmBtn.setAttribute('aria-expanded', 'false');
    document.documentElement.style.overflow = '';
    document.body.style.overflow = '';
  }

  if (mmBtn) mmBtn.addEventListener('click', mmOpen);
  if (mmClose) mmClose.addEventListener('click', mmCloseFn);
  if (mmBackdrop) mmBackdrop.addEventListener('click', mmCloseFn);
  if (mmPanel) {
    mmPanel.addEventListener('click', (e) => {
      const a = e.target && e.target.closest ? e.target.closest('a') : null;
      if (a) mmCloseFn();
    });
  }

// ---------------- Simple lightbox for gallery images ----------------
  const lb = {
    root: null,
    img: null,
    closeBtn: null,
    open(src, alt) {
      if (!this.root) this.init();
      this.img.src = src;
      this.img.alt = alt || '';
      this.root.classList.remove('hidden');
      document.documentElement.style.overflow = 'hidden';
      document.body.style.overflow = 'hidden';
    },
    close() {
      if (!this.root) return;
      this.root.classList.add('hidden');
      this.img.src = '';
      document.documentElement.style.overflow = '';
      document.body.style.overflow = '';
    },
    init() {
      const root = document.createElement('div');
      root.className = 'fixed inset-0 z-[100000] hidden';
      root.innerHTML = `
        <div class="absolute inset-0 bg-black/80"></div>
        <div class="absolute inset-0 p-4 md:p-10 flex items-center justify-center">
          <div class="relative max-w-6xl w-full h-full flex items-center justify-center">
            <img id="lbImg" class="max-h-full max-w-full rounded-2xl shadow-soft bg-white" alt="">
            <button id="lbClose" class="absolute top-0 right-0 -translate-y-2 translate-x-2 md:translate-x-4 md:-translate-y-4 h-11 w-11 rounded-2xl border border-white/20 bg-white/10 text-white backdrop-blur hover:bg-white/20" aria-label="Zamknij">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 6L6 18" /><path d="M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      `;
      document.body.appendChild(root);

      this.root = root;
      this.img = root.querySelector('#lbImg');
      this.closeBtn = root.querySelector('#lbClose');

      root.addEventListener('click', (e) => {
        if (e.target === root || e.target.classList.contains('bg-black/80')) this.close();
      });
      this.closeBtn.addEventListener('click', () => this.close());
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') this.close();
      });
    }
  };

  document.addEventListener('click', (e) => {
    const a = e.target && e.target.closest ? e.target.closest('[data-lightbox]') : null;
    if (!a) return;
    const href = a.getAttribute('href') || '';
    const img = a.querySelector('img');
    if (!href) return;
    e.preventDefault();
    lb.open(href, img ? img.getAttribute('alt') : '');
  });
})();

(function () {
  // ---------------- Typewriter (once, when visible) ----------------
  const els = Array.from(document.querySelectorAll('.js-typeonce'));
  if (!els.length) return;

  function typeOnce(el) {
    if (!el) return;
    if (el.dataset.typed === '1') return;

    const full = el.dataset.text || '';
    const speed = parseInt(el.dataset.speed || '26', 10);

    el.dataset.typed = '1';
    el.textContent = '';

    let i = 0;
    const tick = () => {
      i += 1;
      el.textContent = full.slice(0, i);
      if (i < full.length) window.setTimeout(tick, isNaN(speed) ? 26 : speed);
    };
    tick();
  }

  if (!('IntersectionObserver' in window)) {
    els.forEach(typeOnce);
    return;
  }

  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          typeOnce(e.target);
          io.unobserve(e.target);
        }
      });
    },
    { threshold: 0.6 }
  );

  els.forEach((el) => io.observe(el));
})();

(function () {
  // ---------------- Header (transparent on hero, solid after scroll) ----------------
  const header = document.getElementById('siteHeader');
  const hasHero = document.body && document.body.dataset && document.body.dataset.hasHero === '1';
  const hero = document.getElementById('hero');

  if (header && hasHero && hero) {
    const setTransparent = (on) => {
      header.classList.toggle('is-transparent', !!on);
      header.classList.toggle('is-solid', !on);
    };

    // Initial state
    setTransparent(true);

    // IntersectionObserver gives the cleanest "switch at hero end"
    try {
      const io = new IntersectionObserver((entries) => {
        const entry = entries[0];
        setTransparent(entry && entry.isIntersecting);
      }, { root: null, threshold: 0.1 });

      io.observe(hero);
    } catch (e) {
      // Fallback
      window.addEventListener('scroll', () => {
        const y = window.scrollY || 0;
        setTransparent(y < 40);
      }, { passive: true });
    }
  }

  // ---------------- Showcase carousel (video + progress bars + arrows) ----------------
  const videoEl = document.getElementById('showcaseVideo');
  const titleEl = document.getElementById('showcaseTitle');
  const descEl = document.getElementById('showcaseDesc');
  const prevBtn = document.getElementById('showcasePrev');
  const nextBtn = document.getElementById('showcaseNext');
  const soundBtn = document.getElementById('showcaseSoundBtn');
  const soundIcon = document.getElementById('showcaseSoundIcon');
  const soundText = document.getElementById('showcaseSoundText');
  const progressEl = document.getElementById('showcaseProgress');

  const slides = Array.isArray(window.X_SHOWCASE) ? window.X_SHOWCASE : [];

  if (videoEl && progressEl && slides.length) {
    // Build progress buttons dynamically (one per clip)
    progressEl.innerHTML = '';
    const tabs = slides.map((_, i) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'showcase-tab';
      btn.setAttribute('data-index', String(i));
      btn.setAttribute('aria-label', `Klip ${i + 1}`);
      const bar = document.createElement('span');
      bar.className = 'showcase-bar';
      btn.appendChild(bar);
      progressEl.appendChild(btn);
      return btn;
    });

    let idx = 0;
    let soundEnabled = false;
    let srcCandidates = [];
    let srcCandidateIdx = 0;

    const syncSoundUI = () => {
      if (!soundBtn) return;
      soundBtn.setAttribute('aria-pressed', soundEnabled ? 'true' : 'false');
      if (soundIcon) soundIcon.textContent = soundEnabled ? '🔊' : '🔇';
      if (soundText) soundText.textContent = soundEnabled ? 'Wyłącz dźwięk' : 'Włącz dźwięk';
    };

    const setMeta = (s) => {
      if (titleEl) titleEl.textContent = s && s.title ? String(s.title) : '';
      if (descEl) {
        const d = s && s.desc ? String(s.desc) : '';
        // keep height stable even if empty
        descEl.textContent = d || '\u00A0';
      }
    };

    const apply = (i) => {
      idx = (i + slides.length) % slides.length;
      const s = slides[idx] || {};

      // Meta
      setMeta(s);

      // Tabs
      tabs.forEach((t, ti) => t.classList.toggle('is-active', ti === idx));

      // Video
      srcCandidates = Array.isArray(s.srcs) && s.srcs.length ? s.srcs.filter(Boolean) : (s.src ? [s.src] : []);
      srcCandidateIdx = 0;
      const src = srcCandidates[0];

      if (src) {
        // Set attributes defensively (autoplay on mobile requires muted + playsinline)
        videoEl.setAttribute('playsinline', '');
        videoEl.loop = true;
        videoEl.muted = !soundEnabled;

        if (videoEl.src !== src) {
          videoEl.src = src;
        }

        try { videoEl.load(); } catch (e) {}
        const p = videoEl.play();
        if (p && typeof p.catch === 'function') p.catch(() => {});
      }

      syncSoundUI();
    };

    const next = () => apply(idx + 1);
    const prev = () => apply(idx - 1);

    if (nextBtn) nextBtn.addEventListener('click', next);
    if (prevBtn) prevBtn.addEventListener('click', prev);

    tabs.forEach((t) => {
      t.addEventListener('click', () => {
        const n = parseInt(t.getAttribute('data-index') || '0', 10);
        apply(isNaN(n) ? 0 : n);
      });
    });

    if (soundBtn) {
      soundBtn.addEventListener('click', () => {
        soundEnabled = !soundEnabled;
        videoEl.muted = !soundEnabled;
        if (soundEnabled) {
          videoEl.volume = 1;
          const p = videoEl.play();
          if (p && typeof p.catch === 'function') p.catch(() => {});
        }
        syncSoundUI();
      });
      syncSoundUI();
    }

    // If decoding fails or the URL is not a real video, try the next candidate.
    videoEl.addEventListener('error', () => {
      if (srcCandidates && srcCandidateIdx + 1 < srcCandidates.length) {
        srcCandidateIdx += 1;
        const nextSrc = srcCandidates[srcCandidateIdx];
        if (nextSrc) {
          videoEl.src = nextSrc;
          try { videoEl.load(); } catch (e) {}
          const p = videoEl.play();
          if (p && typeof p.catch === 'function') p.catch(() => {});
          return;
        }
      }
      if (!descEl) return;
      descEl.textContent = 'Nie można odtworzyć wideo w tej przeglądarce (sprawdź kodek / H.264).';
    });

    // Keyboard support (left/right) when the video is visible
    document.addEventListener('keydown', (e) => {
      if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
      const rect = videoEl.getBoundingClientRect();
      const visible = rect.top < window.innerHeight && rect.bottom > 0;
      if (!visible) return;
      if (e.key === 'ArrowRight') next();
      else prev();
    });

    apply(0);
  }
})();


(function () {
  // ---------------- Hero (single clip + sound toggle) ----------------
  const btn = document.getElementById('heroSoundBtn');
  const video = document.getElementById('heroVideo');
  if (!btn || !video) return;

  let soundEnabled = false;

  const sync = () => {
    btn.setAttribute('aria-pressed', soundEnabled ? 'true' : 'false');
    const lab = btn.querySelector('.sound-label');
    if (lab) lab.textContent = soundEnabled ? 'Wyłącz dźwięk' : 'Włącz dźwięk';
  };

  const setSound = (on) => {
    soundEnabled = !!on;
    video.loop = true;
    video.muted = !soundEnabled;

    if (soundEnabled) {
      video.volume = 1;
      const p = video.play();
      if (p && typeof p.catch === 'function') p.catch(() => {});
    }
    sync();
  };

  btn.addEventListener('click', () => setSound(!soundEnabled));
  setSound(false);
})();


;
