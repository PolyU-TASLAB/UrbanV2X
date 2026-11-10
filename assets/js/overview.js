const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const reel=document.querySelector('.hero-reel'),slides=[...document.querySelectorAll('[data-hero-slide]')],dots=[...document.querySelectorAll('[data-hero-index]')];
let current=0,timer=null,running=!reduced,inView=true;
function loadPoster(video){if(video.dataset.poster&&!video.getAttribute('poster'))video.poster=video.dataset.poster;}
function load(video){loadPoster(video);if(!video.getAttribute('src')){video.src=video.dataset.src;video.load();}}
function play(video){load(video);video.muted=true;video.play().catch(()=>{});}
function schedule(){clearTimeout(timer);if(running&&inView&&!document.hidden){const v=slides[current].querySelector('video');const delay=Math.max(6000,Number.isFinite(v.duration)?v.duration*1000:6000);timer=setTimeout(()=>show((current+1)%slides.length),delay);}}
function show(index){current=index;slides.forEach((slide,i)=>{const active=i===index;slide.classList.toggle('is-active',active);slide.setAttribute('aria-hidden',String(!active));const v=slide.querySelector('video');if(active){load(v);if(running&&inView&&!document.hidden)play(v);}else setTimeout(()=>{if(!slide.classList.contains('is-active'))v.pause();},850);});dots.forEach((dot,i)=>dot.setAttribute('aria-pressed',String(i===index)));const slide=slides[index];document.querySelector('#reel-label').textContent=slide.dataset.label;document.querySelector('#reel-count').textContent=`${String(index+1).padStart(2,'0')} / 05`;schedule();}
slides.forEach(s=>s.querySelector('video').addEventListener('loadedmetadata',()=>{if(s.classList.contains('is-active'))schedule();}));
dots.forEach(d=>d.addEventListener('click',()=>show(Number(d.dataset.heroIndex))));
const pause=document.querySelector('#reel-pause');function updatePause(){pause.textContent=running?'Pause Ⅱ':'Resume ↻';pause.setAttribute('aria-label',running?'Pause automatic previews':'Resume automatic previews');}
pause.onclick=()=>{running=!running;updatePause();if(running)show(current);else{clearTimeout(timer);slides[current].querySelector('video').pause();}};
new IntersectionObserver(es=>{inView=es[0].isIntersecting;if(inView)show(current);else{clearTimeout(timer);slides.forEach(s=>s.querySelector('video').pause());}},{threshold:.15}).observe(reel);
document.addEventListener('visibilitychange',()=>{if(document.hidden){clearTimeout(timer);document.querySelectorAll('video').forEach(v=>v.pause());}else if(inView)show(current);});
show(0);updatePause();
// Small looping previews start on entry, without a play-button workflow.
const posters=new IntersectionObserver(entries=>{entries.forEach(({target,isIntersecting})=>{if(isIntersecting){loadPoster(target);posters.unobserve(target);}});},{rootMargin:'300px'});
document.querySelectorAll('video[data-preview], #full-film').forEach(v=>posters.observe(v));
const previews=new IntersectionObserver(entries=>{entries.forEach(({target,isIntersecting})=>{if(isIntersecting&&!reduced&&!document.hidden)play(target);else target.pause();});},{threshold:.15});
document.querySelectorAll('video[data-preview]').forEach(v=>previews.observe(v));
// The complete film is the only large video. Fetch it when it is actually viewed.
const film=document.querySelector('#full-film');let filmStarted=false;
new IntersectionObserver(entries=>{entries.forEach(({isIntersecting})=>{if(isIntersecting&&!filmStarted&&!reduced){filmStarted=true;play(film);}else if(!isIntersecting)film.pause();});},{threshold:.35}).observe(film);
film.addEventListener('pointerdown',()=>load(film),{once:true});film.addEventListener('keydown',()=>load(film),{once:true});
