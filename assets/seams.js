// seams.js (free kit): the page's scene transition — a blur cut, never a flash.
// The outgoing frame defocuses over its last 0.20 s, the incoming one pulls focus back
// over its first 0.18 s, on the plate only, so the change of picture happens inside the
// camera move and the type stays sharp.
//
//   SEAM.blur(tl, DUR)                         focus in at the head, defocus at the tail
//   SEAM.blur(tl, DUR, { in: 0 })              first frame stays sharp (frame 0 = thumbnail)
//   SEAM.blur(tl, DUR, { out: 0 })             last frame stays sharp (closing card holds)
//   SEAM.blur(tl, DUR, { out: 0.26, px: 22 })  a harder cut for a violent seam
//
// Options: in / out in seconds, px of blur, el to aim at (default '#plate').
// Nothing else is needed: no flash overlay, no whip, no transition sound.
(function () {
  const DEFAULTS = { in: 0.18, out: 0.20, px: 18, el: '#plate' };

  function blur(tl, dur, opts) {
    const o = Object.assign({}, DEFAULTS, opts || {});
    const el = typeof o.el === 'string' ? document.querySelector(o.el) : o.el;
    if (!el) return tl;
    el.style.willChange = 'filter';

    if (o.in > 0) {
      tl.fromTo(el, { filter: `blur(${o.px}px)` },
        { filter: 'blur(0px)', duration: o.in, ease: 'power2.out' }, 0);
    }
    if (o.out > 0 && dur > o.out) {
      tl.fromTo(el, { filter: 'blur(0px)' },
        { filter: `blur(${o.px}px)`, duration: o.out, ease: 'power2.in' }, dur - o.out);
    }
    return tl;
  }

  window.SEAM = { blur };
})();
