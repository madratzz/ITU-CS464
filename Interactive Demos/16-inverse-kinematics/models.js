/* Pure numerical models. Local copies keep every lab portable. */
(function(root) {
  'use strict';
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  function spring(s, target, k, c, mass, dt) {
    s.v += (k * (target - s.x) - c * s.v) / mass * dt;
    s.x += s.v * dt;
    return s;
  }
  function reflect(v, n, restitution, friction, slide = false) {
    const dot = v[0] * n[0] + v[1] * n[1];
    if (dot >= 0) return [...v];
    return v.map((x, i) => (x - dot * n[i]) * (1 - friction) - (slide ? 0 : restitution * dot * n[i]));
  }
  // Earliest constant-speed ballistic interception, including constant target velocity.
  function intercept(r, v, speed, gravity, maxTime = 12) {
    const f = t => (r[0] + v[0] * t) ** 2 + (r[1] + v[1] * t + .5 * gravity * t * t) ** 2 - speed * speed * t * t;
    let a = 0, fa = f(0);
    for (let i = 1; i <= 2400; i++) {
      let b = maxTime * i / 2400, fb = f(b);
      if (fa * fb <= 0) {
        for (let j = 0; j < 45; j++) { const m = (a + b) / 2; if (f(a) * f(m) <= 0) b = m; else a = m; }
        const t = (a + b) / 2;
        return { t, velocity: [(r[0] + v[0] * t) / t, (r[1] + v[1] * t + .5 * gravity * t * t) / t] };
      }
      a = b; fa = fb;
    }
    return null;
  }
  function bezier(p, t) { const u = 1 - t; return [0, 1].map(i => u ** 3 * p[0][i] + 3 * u * u * t * p[1][i] + 3 * u * t * t * p[2][i] + t ** 3 * p[3][i]); }
  function tangent(p, t) { return [0, 1].map(i => 3 * (1 - t) ** 2 * (p[1][i] - p[0][i]) + 6 * (1 - t) * t * (p[2][i] - p[1][i]) + 3 * t * t * (p[3][i] - p[2][i])); }
  function arcTable(p, count = 400) {
    const lengths = [0]; let prev = p[0];
    for (let i = 1; i <= count; i++) { const pt = bezier(p, i / count); lengths.push(lengths[i - 1] + Math.hypot(pt[0] - prev[0], pt[1] - prev[1])); prev = pt; }
    return { lengths, total: lengths[count], count };
  }
  function arcParameter(table, progress) {
    if (table.total < 1e-9) return clamp(progress, 0, 1);
    const d = clamp(progress, 0, 1) * table.total; let lo = 0, hi = table.count;
    while (hi - lo > 1) { const m = (lo + hi) >> 1; if (table.lengths[m] < d) lo = m; else hi = m; }
    const span = table.lengths[hi] - table.lengths[lo];
    return (lo + (span > 1e-12 ? (d - table.lengths[lo]) / span : 0)) / table.count;
  }
  function ik(root, target, upper, lower, bend = 1) {
    const dx = target[0] - root[0], dy = target[1] - root[1], requested = Math.hypot(dx, dy);
    const d = clamp(requested, Math.abs(upper - lower) + 1e-6, upper + lower - 1e-6);
    const direction = requested < 1e-9 ? -Math.PI / 2 : Math.atan2(dy, dx);
    const alpha = Math.acos(clamp((upper * upper + d * d - lower * lower) / (2 * upper * d), -1, 1));
    const knee = [root[0] + upper * Math.cos(direction + bend * alpha), root[1] + upper * Math.sin(direction + bend * alpha)];
    const foot = [root[0] + d * Math.cos(direction), root[1] + d * Math.sin(direction)];
    return { knee, foot, error: Math.hypot(foot[0] - target[0], foot[1] - target[1]), reachable: requested <= upper + lower && requested >= Math.abs(upper - lower), kneeAngle: Math.acos(clamp((upper * upper + lower * lower - d * d) / (2 * upper * lower), -1, 1)) };
  }
  const api = { clamp, spring, reflect, intercept, bezier, tangent, arcTable, arcParameter, ik };
  if (typeof module !== 'undefined') module.exports = api; else root.DemoMath = api;
})(typeof window === 'undefined' ? globalThis : window);
