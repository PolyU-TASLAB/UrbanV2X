(() => {
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const reel = document.querySelector('.hero-reel');
  const slides = [...document.querySelectorAll('[data-hero-slide]')];
  const dots = [...document.querySelectorAll('[data-hero-index]')];
  const pauseButton = document.querySelector('#reel-pause');
  let current = 0, timer = null, running = !reducedMotion.matches, reelVisible = false;

  function loadPoster(video) {
    if (video.dataset.poster && !video.getAttribute('poster')) video.poster = video.dataset.poster;
  }
  function load(video) {
    loadPoster(video);
    if (!video.getAttribute('src')) {
      video.src = video.dataset.src;
      video.load();
    }
  }
  function play(video, stillWanted) {
    load(video);
    video.play().then(() => {
      if (!stillWanted()) video.pause();
    }).catch(() => {});
  }
  const reelShouldPlay = () => running && reelVisible && !document.hidden;
  function schedule() {
    clearTimeout(timer);
    if (!reelShouldPlay()) return;
    const video = slides[current].querySelector('video');
    const delay = Math.max(6000, Number.isFinite(video.duration) ? video.duration * 1000 : 6000);
    timer = setTimeout(() => show((current + 1) % slides.length), delay);
  }
  function updateReel() {
    clearTimeout(timer);
    slides.forEach((slide, index) => {
      const video = slide.querySelector('video');
      if (index === current && reelShouldPlay()) {
        play(video, () => index === current && reelShouldPlay());
      } else {
        video.pause();
      }
    });
    schedule();
  }
  function show(index) {
    current = index;
    slides.forEach((slide, position) => {
      const active = position === index;
      slide.classList.toggle('is-active', active);
      slide.setAttribute('aria-hidden', String(!active));
      if (active) loadPoster(slide.querySelector('video'));
    });
    dots.forEach((dot, position) => dot.setAttribute('aria-pressed', String(position === index)));
    document.querySelector('#reel-label').textContent = slides[index].dataset.label;
    document.querySelector('#reel-count').textContent = `${String(index + 1).padStart(2, '0')} / ${String(slides.length).padStart(2, '0')}`;
    updateReel();
  }
  function updatePauseButton() {
    pauseButton.textContent = running ? 'Pause Ⅱ' : 'Resume ↻';
    pauseButton.setAttribute('aria-label', running ? 'Pause automatic previews' : 'Resume automatic previews');
  }
  if (reel && slides.length) {
    slides.forEach(slide => slide.querySelector('video').addEventListener('loadedmetadata', () => {
      if (slide === slides[current]) schedule();
    }));
    dots.forEach((dot, index) => dot.addEventListener('click', () => show(index)));
    pauseButton.addEventListener('click', () => {
      running = !running;
      updatePauseButton();
      updateReel();
    });
    new IntersectionObserver(([entry]) => {
      reelVisible = entry.isIntersecting && entry.intersectionRatio >= 0.15;
      updateReel();
    }, { threshold: [0, 0.15], rootMargin: '-80px 0px 0px 0px' }).observe(reel.querySelector('.reel-screen'));
    show(0);
    updatePauseButton();
  }

  // Posters load near the viewport; video bytes load only when playback is needed.
  const posters = new IntersectionObserver(entries => {
    entries.forEach(({ target, isIntersecting }) => {
      if (isIntersecting) {
        loadPoster(target);
        posters.unobserve(target);
      }
    });
  }, { rootMargin: '300px' });
  const players = [...document.querySelectorAll('video[data-preview], #full-film')].map(video => {
    let visible = false, userPaused = false, pendingAutomaticPauses = 0;
    const threshold = video.id === 'full-film' ? 0.35 : 0.15;
    const shouldPlay = () => visible && !document.hidden && !reducedMotion.matches && !userPaused;
    function pauseAutomatically() {
      if (!video.paused) {
        pendingAutomaticPauses++;
        video.pause();
      }
    }
    function update() {
      if (shouldPlay()) {
        play(video, shouldPlay);
      } else {
        pauseAutomatically();
      }
    }
    if (video.controls) {
      video.addEventListener('pause', () => {
        if (pendingAutomaticPauses) pendingAutomaticPauses--;
        else if (visible && !document.hidden && !video.ended) userPaused = true;
      });
      video.addEventListener('play', () => { userPaused = false; });
      video.addEventListener('pointerdown', () => load(video), { once: true });
      video.addEventListener('keydown', () => load(video), { once: true });
    }
    new IntersectionObserver(([entry]) => {
      const nextVisible = entry.isIntersecting && entry.intersectionRatio >= threshold;
      if (nextVisible && !visible) userPaused = false;
      visible = nextVisible;
      update();
    }, { threshold: [0, threshold], rootMargin: '-80px 0px 0px 0px' }).observe(video);
    posters.observe(video);
    return { update };
  });

  document.addEventListener('visibilitychange', () => {
    if (reel) updateReel();
    players.forEach(player => player.update());
  });
  reducedMotion.addEventListener('change', () => {
    if (reducedMotion.matches && reel) {
      running = false;
      updatePauseButton();
      updateReel();
    }
    players.forEach(player => player.update());
  });
})();
