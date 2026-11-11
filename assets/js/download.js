(() => {
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const previews = [...document.querySelectorAll('[data-download-preview]')];
  const visible = new Set();
  const shouldPlay = preview => visible.has(preview) && !reducedMotion.matches && !document.hidden;
  const update = preview => {
    if (shouldPlay(preview)) {
      if (!preview.getAttribute('src')) preview.src = preview.dataset.src;
      preview.play().then(() => {
        if (!shouldPlay(preview)) preview.pause();
      }).catch(() => {});
    } else {
      preview.pause();
    }
  };
  const observer = new IntersectionObserver(entries => {
    entries.forEach(({target, isIntersecting, intersectionRatio}) => {
      if (isIntersecting && intersectionRatio >= 0.15) visible.add(target);
      else visible.delete(target);
      update(target);
    });
  }, {rootMargin: '-80px 0px 0px', threshold: [0, 0.15]});
  previews.forEach(preview => observer.observe(preview));
  reducedMotion.addEventListener('change', () => previews.forEach(update));
  document.addEventListener('visibilitychange', () => previews.forEach(update));
})();
