(() => {
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const previews = [...document.querySelectorAll('[data-download-preview]')];
  const visible = new Set();
  const update = video => {
    if (visible.has(video) && !reducedMotion.matches && !document.hidden) {
      if (!video.getAttribute('src')) video.src = video.dataset.src;
      video.play().catch(() => {});
    } else {
      video.pause();
    }
  };
  const observer = new IntersectionObserver(entries => {
    entries.forEach(({target, isIntersecting}) => {
      if (isIntersecting) visible.add(target);
      else visible.delete(target);
      update(target);
    });
  }, {threshold: 0.05});
  previews.forEach(video => observer.observe(video));
  reducedMotion.addEventListener('change', () => previews.forEach(update));
  document.addEventListener('visibilitychange', () => previews.forEach(update));
})();
