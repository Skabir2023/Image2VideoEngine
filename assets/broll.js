// broll.js (free kit): camera work on a still plate, so a photograph moves like footage.
// The plate is oversized once (sized automatically so no move ever shows an edge), then a camera moves over it:
//   const cam = BROLL.make(root, { src: 'assets/stills/car.jpg', duration: 8, gait: 0.8, shots: [
//     { t: 0,   dur: 1.5, move: 'hold' },                       // walking up to the car
//     { t: 1.5, dur: 1.8, move: 'push', by: 0.16 },             // in on the grille
//     { t: 3.3, dur: 1.6, move: 'truckR', by: 120 },            // travel along the body
//     { t: 4.9, dur: 1.5, move: 'orbitR', by: 150 },            // circle toward the rear
//     { t: 6.4, dur: 1.2, move: 'pull', by: 0.10 },             // step back
//   ] });
//   BROLL.live(tl, cam)            drives it on the composition's timeline (or call cam.update(t) inside frame(t))
// zoom0 is where the camera sits at frame 0: start below 1 and end below 1 for a wide -> tight -> wide arc, which is the
// shape a reel wants. The plate is sized automatically from the widest moment, so zoom below 1 never shows an edge.
// Moves: hold, push, pull, truckL, truckR, craneUp, craneDown, rollL, rollR, orbitL, orbitR.
// Feel: handheld (drift + tremor), gait (walking bob and sway), shakes ([{ at, power }]), grain, vignette.
// Parallax: cam.attach(cutoutEl, { gain: 1.4 }) moves a cut-out car faster than the background, which is what makes it
// read as footage instead of a zoom.
(function () {
  const E = STAGE.E;
  const DEG = Math.PI / 180;

  const CSS = [
    '.br-root { position: absolute; inset: 0; overflow: hidden; background: #050506; }',
    '.br-layer { position: absolute; inset: 0; transform-origin: 50% 50%; backface-visibility: hidden; will-change: transform; }',
    '.br-layer img { width: 100%; height: 100%; object-fit: cover; display: block; -webkit-user-drag: none; user-select: none; }',
    '.br-vig { position: absolute; inset: 0; pointer-events: none; }',
    '.br-grain { position: absolute; inset: -60px; pointer-events: none; opacity: 0; mix-blend-mode: overlay; background-repeat: repeat; }',
  ].join('\n');

  function css() {
    if (document.getElementById('br-css')) return;
    const s = document.createElement('style'); s.id = 'br-css'; s.textContent = CSS; document.head.appendChild(s);
  }

  // smooth value noise built once from a seed: the shake is the same on every render, and any frame draws on its own
  function noise(seed, len = 512) {
    const r = STAGE.mulberry32(seed >>> 0), v = new Float32Array(len);
    for (let i = 0; i < len; i++) v[i] = r() * 2 - 1;
    return (x) => {
      const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f);
      const a = v[((i % len) + len) % len], b = v[(((i + 1) % len) + len) % len];
      return a + (b - a) * u;
    };
  }

  // each move pushes one camera channel over the length of its shot; `by` is in that channel's own units
  // (zoom = a fraction, pan/lift = pixels, roll = degrees)
  const MOVES = {
    hold:      { ch: null },
    push:      { ch: 'zoom', dir: 1,  def: 0.14 },
    pull:      { ch: 'zoom', dir: -1, def: 0.14 },
    truckR:    { ch: 'pan',  dir: 1,  def: 100 },
    truckL:    { ch: 'pan',  dir: -1, def: 100 },
    craneUp:   { ch: 'lift', dir: -1, def: 80 },
    craneDown: { ch: 'lift', dir: 1,  def: 80 },
    rollR:     { ch: 'roll', dir: 1,  def: 1.4 },
    rollL:     { ch: 'roll', dir: -1, def: 1.4 },
    orbitR:    { ch: 'pan',  dir: 1,  def: 140, zoom: 0.05, roll: 0.4 },
    orbitL:    { ch: 'pan',  dir: -1, def: 140, zoom: 0.05, roll: -0.4 },
  };

  const val = (v, t) => (typeof v === 'function' ? v(t) : v);

  function make(root, o = {}) {
    css();
    const comp = document.querySelector('[data-composition-id]');
    const W = +((comp && comp.dataset.width) || 1920);
    const H = +((comp && comp.dataset.height) || 1080);
    const opts = Object.assign({
      src: '', duration: 6, shots: [], handheld: 1, gait: 0, shakes: [], zoom0: 1,
      grain: 0.35, vignette: 0.5, seed: 7, focus: '50% 50%', pad: 0.02,
    }, o);

    root.classList.add('br-root');
    const layer = document.createElement('div'); layer.className = 'br-layer';
    let img = null;
    if (opts.src) {
      img = document.createElement('img');
      img.src = opts.src; img.alt = ''; img.style.objectPosition = opts.focus;
      layer.appendChild(img);
    }
    root.appendChild(layer);

    const vig = document.createElement('div'); vig.className = 'br-vig';      vig.style.background = 'radial-gradient(ellipse 76% 72% at ' + opts.focus + ', transparent 52%, rgba(0,0,0,' +
      (0.62 * opts.vignette).toFixed(2) + ') 100%)';
    root.appendChild(vig);

    const grain = document.createElement('div'); grain.className = 'br-grain';
    grain.style.backgroundImage = 'url("data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'200\' height=\'200\'>' +
      '<filter id=\'g\'><feTurbulence type=\'fractalNoise\' baseFrequency=\'0.9\' numOctaves=\'3\' seed=\'' + (opts.seed + 3) + '\' stitchTiles=\'stitch\'/>' +
      '<feColorMatrix type=\'saturate\' values=\'0\'/></filter>' +
      '<rect width=\'100%25\' height=\'100%25\' filter=\'url(%23g)\' opacity=\'0.62\'/></svg>")';
    grain.style.opacity = String(opts.grain);
    root.appendChild(grain);

    const n = [0, 1, 2, 3, 4, 5].map((i) => noise(opts.seed * 97 + i * 13 + 1));
    const shots = (opts.shots || []).slice().sort((a, b) => a.t - b.t);
    const extras = [];
    const CORNERS = [[-W / 2, -H / 2], [W / 2, -H / 2], [W / 2, H / 2], [-W / 2, H / 2]];

    // the move itself: every shot adds its delta once it starts, so the camera carries on from where it was
    function poseNorm(t) {
      let zoom = opts.zoom0, pan = 0, lift = 0, roll = 0;
      for (const s of shots) {
        const m = MOVES[s.move] || MOVES.hold;
        const end = s.t + s.dur;
        const u = t <= s.t ? 0 : t >= end ? 1 : (t - s.t) / s.dur;
        if (!u) continue;
        const e = (E[s.ease] || E.inOutCubic)(u);
        const by = s.by != null ? s.by : (m.def || 0);
        if (m.ch === 'zoom') zoom += m.dir * by * e;
        else if (m.ch === 'pan') pan += m.dir * by * e;
        else if (m.ch === 'lift') lift += m.dir * by * e;
        else if (m.ch === 'roll') roll += m.dir * by * e;
        if (m.zoom) zoom += m.zoom * e;
        if (m.roll) roll += m.roll * e;
      }
      return { zoom, pan, lift, roll };
    }

    // the move, plus the feel of somebody holding the camera
    function poseAt(t) {
      const p = poseNorm(t);
      const hh = val(opts.handheld, t), gt = val(opts.gait, t);
      let cx = p.pan, cy = p.lift, r = p.roll;
      if (hh) {
        cx += (n[0](t * 0.33) * 7 + n[1](t * 1.6) * 1.6) * hh;
        cy += (n[2](t * 0.29) * 6 + n[3](t * 1.9) * 1.4) * hh;
        r += (n[4](t * 0.24) * 0.3 + n[5](t * 2.2) * 0.07) * hh;
      }
      if (gt) {
        const ph = t * Math.PI * 2 * 1.85;                 // about 1.85 steps a second
        cy += Math.sin(ph) * 8 * gt;
        cx += Math.sin(ph * 0.5) * 11 * gt;
        r += Math.sin(ph * 0.5 + 1.1) * 0.5 * gt;
      }
      for (const sh of opts.shakes) {
        const d = t - sh.at;
        if (d < 0 || d > 0.7) continue;
        const power = (sh.power != null ? sh.power : 1) * Math.exp(-d / (sh.decay || 0.16));
        cx += Math.sin(d * 71 + 1.3) * 13 * power;
        cy += Math.sin(d * 93 + 0.4) * 10 * power;
        r += Math.sin(d * 57) * 0.5 * power;
      }
      return { zoom: p.zoom, cx, cy, r };
    }

    // how much bigger than the frame the plate has to be, sampled over the whole shot list, so no edge is ever visible
    function solve(gain) {
      const g = gain == null ? 1 : gain;
      let need = 1;
      const steps = Math.max(60, Math.ceil(opts.duration * 120));
      for (let i = 0; i <= steps; i++) {
        const p = poseAt((i / steps) * opts.duration);
        const px = p.cx * g, py = p.cy * g;
        const rr = -p.r * DEG, co = Math.cos(rr), si = Math.sin(rr);
        for (const c of CORNERS) {
          const vx = c[0] + px, vy = c[1] + py;
          const ix = co * vx - si * vy, iy = si * vx + co * vy;
          need = Math.max(need, Math.abs(ix) / (W / 2) / p.zoom, Math.abs(iy) / (H / 2) / p.zoom);
        }
      }
      return need * (1 + opts.pad);
    }

    function draw(el, p, gain, s0) {
      const cx = p.cx * gain, cy = p.cy * gain, s = s0 * p.zoom;
      el.style.transform = 'translate(' + (-cx).toFixed(2) + 'px, ' + (-cy).toFixed(2) + 'px) rotate(' +
        p.r.toFixed(3) + 'deg) scale(' + s.toFixed(5) + ')';
    }

    let t0 = 0, s0 = null;
    const cam = {
      root, layer, img, duration: opts.duration, poseAt,
      get scale() { return s0; },
      update(t) {
        t0 = t;
        if (s0 == null) s0 = solve(1);
        const p = poseAt(t);
        draw(layer, p, 1, s0);
        for (const l of extras) draw(l.el, p, l.gain, l.s0);
        if (opts.grain) {
          grain.style.backgroundPosition = (n[1](t * 3.1) * 40).toFixed(1) + 'px ' + (n[2](t * 3.4) * 40).toFixed(1) + 'px';
        }
      },
      // a cut-out of the subject glued on top, moving faster than the plate: real parallax from one photograph
      attach(el, a = {}) {
        css();
        const gain = a.gain != null ? a.gain : 1.4;
        el.classList.add('br-layer');
        const l = { el, gain, s0: solve(gain) };
        extras.push(l);
        return () => { const i = extras.indexOf(l); if (i >= 0) extras.splice(i, 1); };
      },
    };
    return cam;
  }

  function live(tl, cam, dur) {
    const D = dur != null ? dur : cam.duration, d = { t: 0 };
    tl.fromTo(d, { t: 0 }, { t: D, duration: D, ease: 'none', onUpdate: () => cam.update(d.t) }, 0);
    cam.update(0);
    // the plate may still be loading when the first frame is drawn
    if (cam.img && cam.img.decode) cam.img.decode().then(() => cam.update(d.t)).catch(() => {});
    // HyperFrames re-dispatches hf-seek after it swaps frames in; redraw then so the plate is not a frame late
    window.addEventListener('hf-seek', (e) => {
      const dd = e && e.detail, t = dd && Number.isFinite(+dd.time) ? +dd.time : d.t;
      try { cam.update(t); } catch (err) { console.error(err); }
    });
    return tl;
  }

  window.BROLL = { make, live, MOVES };
})();
