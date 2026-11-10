const menu = document.querySelector('.menu');
const nav = document.querySelector('#navigation');
menu?.addEventListener('click', () => {
  const open = menu.getAttribute('aria-expanded') !== 'true';
  menu.setAttribute('aria-expanded', String(open));
  nav.classList.toggle('open', open);
});
nav?.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
  menu?.setAttribute('aria-expanded', 'false');
  nav.classList.remove('open');
}));
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && nav?.classList.contains('open')) {
    nav.classList.remove('open');
    menu.setAttribute('aria-expanded', 'false');
    menu.focus();
  }
});
document.querySelectorAll('[data-filter]').forEach((button) => button.addEventListener('click', () => {
  document.querySelectorAll('[data-filter]').forEach((item) => {
    const selected = item === button;
    item.classList.toggle('selected', selected);
    item.setAttribute('aria-pressed', String(selected));
  });
  document.querySelectorAll('#sequences tbody tr').forEach((row) => {
    row.hidden = button.dataset.filter !== 'all' && row.dataset.site !== button.dataset.filter;
  });
}));

const slideshow = document.querySelector('[data-slideshow]');
if (slideshow) {
  const slides = Array.from(slideshow.querySelectorAll('[data-slide]'));
  const playButton = slideshow.querySelector('[data-slide-play]');
  const counter = slideshow.querySelector('[data-slide-count]');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let current = 0;
  let timer = null;
  let playing = !reducedMotion;
  let touchStartX = null;

  const schedule = () => {
    window.clearTimeout(timer);
    if (playing) timer = window.setTimeout(() => show(current + 1), 5000);
  };

  const show = (index, resetTimer = true) => {
    current = (index + slides.length) % slides.length;
    slides.forEach((slide, position) => {
      const active = position === current;
      slide.classList.toggle('is-active', active);
      slide.setAttribute('aria-hidden', String(!active));
      const video = slide.querySelector('video');
      if (!active) video.pause();
    });
    const activeVideo = slides[current].querySelector('video');
    if (playing) {
      if (activeVideo.readyState > 0) activeVideo.currentTime = 0;
      activeVideo.play().catch(() => {});
    }
    counter.textContent = `${String(current + 1).padStart(2, '0')} / ${String(slides.length).padStart(2, '0')}`;
    if (resetTimer) schedule();
  };

  const setPlaying = (value) => {
    playing = value;
    playButton.textContent = playing ? 'Pause' : 'Play';
    playButton.setAttribute('aria-label', playing ? 'Pause slideshow' : 'Play slideshow');
    if (playing) show(current, false);
    else slides[current].querySelector('video').pause();
    schedule();
  };

  slideshow.querySelector('[data-slide-prev]').addEventListener('click', () => show(current - 1));
  slideshow.querySelector('[data-slide-next]').addEventListener('click', () => show(current + 1));
  playButton.addEventListener('click', () => setPlaying(!playing));
  slideshow.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft') {
      event.preventDefault();
      show(current - 1);
    }
    if (event.key === 'ArrowRight') {
      event.preventDefault();
      show(current + 1);
    }
  });
  slideshow.addEventListener('pointerdown', (event) => {
    touchStartX = event.clientX;
  });
  slideshow.addEventListener('pointerup', (event) => {
    if (touchStartX === null) return;
    const distance = event.clientX - touchStartX;
    touchStartX = null;
    if (Math.abs(distance) > 45) show(current + (distance < 0 ? 1 : -1));
  });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) slides[current].querySelector('video').pause();
    else if (playing) show(current);
  });

  show(0, false);
  setPlaying(playing);
}
