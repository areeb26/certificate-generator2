/** Hit box for a certificate text overlay (canvas pixel space). */
export function overlayHitBox(pos, fontSize, alignment, metrics) {
  if (!pos) return null;
  const width = Math.max(
    metrics.width || 0,
    (metrics.actualBoundingBoxLeft || 0) + (metrics.actualBoundingBoxRight || 0),
    fontSize
  );
  const ascent = metrics.actualBoundingBoxAscent || fontSize * 0.9;
  const descent = metrics.actualBoundingBoxDescent || fontSize * 0.35;
  const pad = Math.max(12, fontSize * 0.35);
  let left = pos.x;
  if (alignment === 'center') left = pos.x - width / 2;
  else if (alignment === 'right') left = pos.x - width;
  // rtl-end: left edge is the pin (same as left)
  return {
    left: left - pad,
    right: left + width + pad,
    top: pos.y - ascent - pad,
    bottom: pos.y + descent + pad,
  };
}

export function pointInHitBox(x, y, box) {
  return !!box && x >= box.left && x <= box.right && y >= box.top && y <= box.bottom;
}
