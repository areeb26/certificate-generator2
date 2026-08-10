import assert from 'node:assert/strict';
import { overlayHitBox, pointInHitBox } from './overlayHitBox.js';

const pos = { x: 200, y: 110 };
const box = overlayHitBox(pos, 36, 'center', { width: 80, actualBoundingBoxAscent: 28, actualBoundingBoxDescent: 8 });
assert.ok(box, 'box');
assert.ok(pointInHitBox(200, 110, box), 'center of course should be hittable');
assert.ok(pointInHitBox(200, 90, box), 'above baseline (glyph body) should be hittable');
assert.ok(!pointInHitBox(200, 10, box), 'far above should miss');
assert.ok(!pointInHitBox(20, 110, box), 'far left should miss');

const tinyUrdu = overlayHitBox(pos, 36, 'center', { width: 4 });
assert.ok(pointInHitBox(200, 110, tinyUrdu), 'tiny measureText width still hittable via fontSize floor');

console.log('OK: overlayHitBox checks passed');
