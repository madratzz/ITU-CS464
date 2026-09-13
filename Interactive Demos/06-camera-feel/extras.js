'use strict';
const Extra = (() => {
  const T = THREE, L = Lab;
  function playback(reset, { running = true, step = null } = {}) {
    const state = { running: running && !matchMedia('(prefers-reduced-motion: reduce)').matches };
    const items = [['play', state.running ? 'Pause' : 'Play', () => { state.running = !state.running; L.$('play').textContent = state.running ? 'Pause' : 'Play'; }, true], ['reset', 'Reset trial', reset]];
    if (step) items.push(['step', 'Step', () => { state.running = false; L.$('play').textContent = 'Play'; step(1 / 120); }]);
    L.buttons(items); return state;
  }
  function aircraft(color) {
    const g = new T.Group();
    g.add(L.box(.55, .4, 3.4, 0xcad7e3)); g.add(L.box(4.2, .12, 1, color));
    g.add(L.box(1.7, .1, .6, color, 0, .18, -1.3)); g.add(L.box(.12, .7, .6, L.colors.orange, 0, .4, -1.3));
    const n = new T.Mesh(new T.ConeGeometry(.28, .8, 16), L.material(L.colors.orange)); n.rotation.x = Math.PI / 2; n.position.z = 2; g.add(n); return g;
  }
  function bone(color, radius = .13) { const b = new T.Mesh(new T.CylinderGeometry(radius, radius, 1, 16), L.material(color)); b.castShadow = true; return b; }
  function segment(mesh, a, b) { const d = b.clone().sub(a); mesh.position.copy(a).add(b).multiplyScalar(.5); mesh.scale.y = d.length(); if (d.lengthSq() > 1e-10) mesh.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), d.normalize()); }
  function trail(color, scene, limit = 300) { const points = [], mesh = L.line([[0, 0, 0], [0, 0, 0]], color); scene.add(mesh); return { add(p) { points.push(p.clone()); if (points.length > limit) points.shift(); L.replaceLine(mesh, points); }, clear() { points.length = 0; L.replaceLine(mesh, [new T.Vector3(), new T.Vector3()]); }, mesh }; }
  function graph(series, colors, min, max, title = 'RESPONSE / LAST 6 SECONDS') {
    L.$('graph-wrap').hidden = false;
    const canvas = L.$('graph'), ctx = canvas.getContext('2d'); const w = canvas.clientWidth, h = 115, ratio = Math.min(devicePixelRatio, 2);
    if (canvas.width !== w * ratio || canvas.height !== h * ratio) { canvas.width = w * ratio; canvas.height = h * ratio; }
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0); ctx.clearRect(0, 0, w, h); ctx.font = '10px monospace'; ctx.fillStyle = '#9aa2b1'; ctx.fillText(title, 10, 15);
    const y = v => 95 - (v - min) / (max - min) * 65;
    ctx.strokeStyle = '#344150'; for (const v of [min, (min + max) / 2, max]) { ctx.beginPath(); ctx.moveTo(35, y(v)); ctx.lineTo(w - 10, y(v)); ctx.stroke(); ctx.fillText(v.toFixed(1), 2, y(v) + 3); }
    series.forEach((values, i) => { ctx.strokeStyle = colors[i]; ctx.lineWidth = 2; ctx.beginPath(); values.forEach((v, j) => { const x = 35 + j / Math.max(1, values.length - 1) * (w - 50); if (j) ctx.lineTo(x, y(v)); else ctx.moveTo(x, y(v)); }); ctx.stroke(); });
  }
  function onPlane(engine, plane, fn, { draggable = false, pick = null } = {}) {
    const canvas = engine.renderer.domElement, ray = new T.Raycaster(); let active = false;
    const point = e => { const r = canvas.getBoundingClientRect(); ray.setFromCamera(new T.Vector2((e.clientX - r.left) / r.width * 2 - 1, -(e.clientY - r.top) / r.height * 2 + 1), engine.camera); return ray.ray.intersectPlane(plane, new T.Vector3()); };
    canvas.addEventListener('pointerdown', e => { const p = point(e); if (!p || (pick && !pick(ray, p))) return; active = true; canvas.setPointerCapture(e.pointerId); fn(p); });
    canvas.addEventListener('pointermove', e => { if (active && draggable) { const p = point(e); if (p) fn(p); } });
    for (const name of ['pointerup', 'pointercancel', 'lostpointercapture']) canvas.addEventListener(name, () => active = false);
  }
  function fixed(callback, hz = 120) { let acc = 0; return dt => { acc += dt; while (acc >= 1 / hz) { callback(1 / hz); acc -= 1 / hz; } }; }
  function help(text) { L.$('help').textContent = text; }
  function legend(text) { L.$('stage').insertAdjacentHTML('beforeend', `<div class="legend-strip">${text}</div>`); }
  return { playback, aircraft, bone, segment, trail, graph, onPlane, fixed, help, legend };
})();
