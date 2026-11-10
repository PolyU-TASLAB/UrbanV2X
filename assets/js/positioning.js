/* Interactive demo: recorded observations, GT motion, no edits to source data. */
(() => {
  const canvas = document.querySelector('#positioning-canvas');
  if (!canvas) return;
  const scriptURL = document.querySelector('script[src$="positioning.js"]').src;
  const status = document.querySelector('#scene-status');
  let started = false;
  const loader = new IntersectionObserver(entries => {
    if (started || !entries.some(entry => entry.isIntersecting)) return;
    started = true;
    loader.disconnect();
    initialize().catch(error => {
      console.error(error);
      status.hidden = false;
      status.textContent = 'The scene could not load. Please reload to try again.';
    });
  }, { rootMargin: '400px' });
  loader.observe(canvas);

  async function initialize() {
    const root = new URL('../data/', scriptURL);
    const [data, map] = await Promise.all(['positioning-timeline', 'hkstp-map'].map(async name => {
      const response = await fetch(new URL(name + '.json', root));
      if (!response.ok) throw new Error(name);
      return response.json();
    }));
    const ctx = canvas.getContext('2d');
    if (!ctx) throw new Error('Canvas unavailable');
    const tail = document.createElement('canvas');
    const tailContext = tail.getContext('2d');
    const frames = data.frames;
    const start = Math.min(225, frames.length - 1), end = frames.length - 1;
    const origin = [114.21355, 22.42474];
    const enu = (p, z = 0) => [(p[0] - origin[0]) * 102900, (p[1] - origin[1]) * 111320, z];
    const points = frames.map(frame => enu(frame.position, 2));
    const anchors = (data.anchors || [data.anchor]).map(anchor => ({
      point: enu([anchor.longitude, anchor.latitude], 3),
      column: data.uwb_ids.indexOf(anchor.id)
    }));
    const features = map.features.map(feature => ({ ...feature, points: feature.points.map(p => enu(p)) }));
    const roads = features.filter(feature => feature.kind === 'road');
    const faces = [];
    for (const feature of features.filter(f => f.kind === 'building')) {
      for (let i = 0; i < feature.points.length - 1; i++) {
        const a = feature.points[i], b = feature.points[i + 1];
        faces.push({ points: [a, b, [b[0], b[1], feature.height], [a[0], a[1], feature.height]], color: '#2b4455' });
      }
      faces.push({ points: feature.points.map(p => [p[0], p[1], feature.height]), color: '#506779' });
    }
    faces.forEach(face => face.center = face.points.reduce((sum, p) => sum.map((v, k) => v + p[k] / face.points.length), [0, 0, 0]));

    const slider = document.querySelector('#timeline');
    const playButton = document.querySelector('#scene-play');
    const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
    let head = start, yaw = -.32, pitch = .63, zoom = 1;
    let playing = !reducedMotion.matches, visible = false, mix = 1, previousTime = null;
    let pointer = null, width = 0, height = 0, dpr = 1;
    slider.min = start; slider.max = end; slider.disabled = false;
    const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
    const clock = seconds => `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;

    function draw(target, position) {
      const index = Math.floor(position), next = Math.min(index + 1, end), fraction = position - index;
      const frame = frames[index];
      const vehicle = enu(frame.position.map((v, k) => v + (frames[next].position[k] - v) * fraction), 3);
      target.setTransform(dpr, 0, 0, dpr, 0, 0);
      target.globalAlpha = 1;
      target.fillStyle = '#091b29'; target.fillRect(0, 0, width, height);
      const scale = Math.min(width / 680, height / 490) * zoom;
      const project = p => {
        const x = p[0] * Math.cos(yaw) - p[1] * Math.sin(yaw);
        const y = p[0] * Math.sin(yaw) + p[1] * Math.cos(yaw);
        return [width * .5 + x * scale, height * .73 + (y * Math.sin(pitch) - p[2] * Math.cos(pitch)) * scale, y * Math.cos(pitch) + p[2] * Math.sin(pitch)];
      };
      function line(path, color, thickness = 1, dash = []) {
        if (path.length < 2) return;
        target.beginPath();
        path.forEach((p, i) => { const q = project(p); i ? target.lineTo(q[0], q[1]) : target.moveTo(q[0], q[1]); });
        target.strokeStyle = color; target.lineWidth = thickness; target.setLineDash(dash); target.stroke(); target.setLineDash([]);
      }
      function polygon(path, color) {
        target.beginPath();
        path.forEach((p, i) => { const q = project(p); i ? target.lineTo(q[0], q[1]) : target.moveTo(q[0], q[1]); });
        target.closePath(); target.fillStyle = color; target.fill(); target.strokeStyle = '#70849555'; target.lineWidth = .5; target.stroke();
      }
      for (let n = -350; n <= 350; n += 50) {
        line([[n, -350, 0], [n, 350, 0]], '#203b4b', .5);
        line([[-350, n, 0], [350, n, 0]], '#203b4b', .5);
      }
      roads.forEach(road => line(road.points, '#405766', 2));
      [...faces].sort((a, b) => project(b.center)[2] - project(a.center)[2]).forEach(face => polygon(face.points, face.color));
      line([...points.slice(0, index + 1), [vehicle[0], vehicle[1], 2]], '#44e1dd', 3);
      for (const anchor of anchors) {
        const [ax, ay] = project(anchor.point);
        target.fillStyle = '#b7f493'; target.fillRect(ax - 4, ay - 4, 8, 8);
        const range = frame.ranges[anchor.column];
        if (Number.isFinite(range) && range > 0) line([vehicle, anchor.point], '#b7f493', 2);
      }
      for (const satellite of frame.satellites) {
        const az = satellite.az * Math.PI / 180, el = satellite.el * Math.PI / 180;
        const p = [vehicle[0] + 285 * Math.sin(az) * Math.cos(el), vehicle[1] + 285 * Math.cos(az) * Math.cos(el), 285 * Math.sin(el)];
        const red = satellite.nlos_candidate;
        line([vehicle, p], red ? '#ff6e6980' : '#8ac8f036', red ? 1.3 : .8, red ? [4, 4] : []);
        const [x, y] = project(p);
        target.fillStyle = red ? '#ff6e69' : '#91c6e9'; target.fillRect(x - 3, y - 4, 6, 8);
        target.fillStyle = red ? '#bd514e' : '#496e8e'; target.fillRect(x - 12, y - 3, 7, 6); target.fillRect(x + 5, y - 3, 7, 6);
      }
      const [x, y] = project(vehicle);
      target.shadowColor = '#44e1dd'; target.shadowBlur = 12; target.fillStyle = '#44e1dd';
      target.beginPath(); target.arc(x, y, 5, 0, 7); target.fill(); target.shadowBlur = 0;
    }
    function render(position = head) {
      head = clamp(position, start, end);
      width = canvas.clientWidth; height = canvas.clientHeight; dpr = Math.min(devicePixelRatio || 1, 2);
      if (!width || !height) return;
      if (canvas.width !== Math.round(width * dpr) || canvas.height !== Math.round(height * dpr)) {
        canvas.width = tail.width = Math.round(width * dpr);
        canvas.height = tail.height = Math.round(height * dpr);
      }
      draw(ctx, head);
      if (mix < 1) {
        draw(tailContext, end);
        ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.globalAlpha = 1 - mix * mix * (3 - 2 * mix);
        ctx.drawImage(tail, 0, 0); ctx.restore();
      }
      slider.value = head;
      slider.setAttribute('aria-valuetext', `${clock(head - start)} of ${clock(end - start)}`);
      document.querySelector('#scene-time').textContent = `${clock(head - start)} / ${clock(end - start)}`;
    }
    function updatePlayback() {
      playButton.textContent = playing ? 'Ⅱ' : '▶';
      playButton.setAttribute('aria-label', playing ? 'Pause trajectory' : 'Play trajectory');
      playButton.title = playing ? 'Pause trajectory' : 'Play trajectory';
      previousTime = null;
    }
    playButton.onclick = () => { playing = !playing; updatePlayback(); };
    slider.oninput = () => { playing = false; mix = 1; updatePlayback(); render(Number(slider.value)); };
    function turn(deltaYaw, deltaPitch = 0) { yaw += deltaYaw; pitch = clamp(pitch + deltaPitch, .2, 1.15); render(); }
    function magnify(factor) { zoom = clamp(zoom * factor, .6, 2.5); render(); }
    function reset() { yaw = -.32; pitch = .63; zoom = 1; render(); }
    document.querySelector('#scene-left').onclick = () => turn(-.15);
    document.querySelector('#scene-right').onclick = () => turn(.15);
    document.querySelector('#scene-zoom-in').onclick = () => magnify(1.15);
    document.querySelector('#scene-zoom-out').onclick = () => magnify(1 / 1.15);
    document.querySelector('#scene-reset').onclick = reset;
    canvas.addEventListener('pointerdown', event => {
      if (event.button !== 0 || pointer) return;
      pointer = { id: event.pointerId, x: event.clientX, y: event.clientY };
      canvas.setPointerCapture(event.pointerId); canvas.classList.add('dragging');
    });
    canvas.addEventListener('pointermove', event => {
      if (!pointer || pointer.id !== event.pointerId) return;
      turn((event.clientX - pointer.x) * .006, event.pointerType === 'touch' ? 0 : (event.clientY - pointer.y) * .003);
      pointer.x = event.clientX; pointer.y = event.clientY;
    });
    const endDrag = () => { pointer = null; canvas.classList.remove('dragging'); };
    ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(type => canvas.addEventListener(type, endDrag));
    canvas.addEventListener('wheel', event => {
      if (!event.ctrlKey && !event.metaKey) return;
      event.preventDefault(); magnify(Math.exp(-event.deltaY * .002));
    }, { passive: false });
    canvas.addEventListener('keydown', event => {
      const actions = { ArrowLeft: () => turn(-.12), ArrowRight: () => turn(.12), ArrowUp: () => turn(0, -.08), ArrowDown: () => turn(0, .08), '+': () => magnify(1.15), '-': () => magnify(1 / 1.15), '0': reset };
      if (actions[event.key]) { event.preventDefault(); actions[event.key](); }
    });
    new ResizeObserver(() => render()).observe(canvas);
    new IntersectionObserver(entries => { visible = entries[0].isIntersecting; previousTime = null; }, { threshold: .05 }).observe(canvas);
    document.addEventListener('visibilitychange', () => { previousTime = null; });
    reducedMotion.addEventListener('change', () => { if (reducedMotion.matches) { playing = false; updatePlayback(); } });
    window.positioningScene = {
      render: position => { mix = 1; render(position); },
      stop: () => { playing = false; updatePlayback(); },
      setYaw: value => { yaw = value; render(); },
      getState: () => ({ index: head, yaw, pitch, zoom, playing, visible, loopMix: mix })
    };
    status.hidden = true; updatePlayback(); render();
    function tick(time) {
      requestAnimationFrame(tick);
      if (!playing || !visible || document.hidden) { previousTime = null; return; }
      if (previousTime === null) { previousTime = time; return; }
      const elapsed = (time - previousTime) / 1000;
      if (elapsed < 1 / 30) return;
      previousTime = time;
      const delta = Math.min(elapsed, .1);
      head += delta * 6.25;
      if (head > end) { head = start + head - end; mix = 0; }
      else mix = Math.min(1, mix + delta / .8);
      render();
    }
    requestAnimationFrame(tick);
  }
})();
