// One state per guide lock. Feed an angle in radians from scroll or pointer input.
export function stepLock(state, target, elapsed, frequency = 2) {
  const omega = 2 * Math.PI * frequency;
  const offset = state.angle - target;
  const slope = state.velocity + omega * offset;
  const decay = Math.exp(-omega * elapsed);
  state.angle = target + (offset + slope * elapsed) * decay;
  state.velocity = (state.velocity - omega * slope * elapsed) * decay;
}

// Hold the roots and any floor contact fixed while the free lengths bend.
export function bendWeight(along, floorContact) {
  const release = Math.min(1, Math.max(0, along / .38));
  const clearance = Math.min(1, Math.max(0, floorContact / .32));
  return release * release * (3 - 2 * release) *
    clearance * clearance * (3 - 2 * clearance);
}