import fs from 'fs';
import { topology } from 'topojson-server';
import { presimplify, simplify, planarTriangleArea, filter, filterWeight } from 'topojson-simplify';
import { quantize } from 'topojson-client';
const [,, input, output, minArea = '0.4', q = '1e5'] = process.argv;
const g = JSON.parse(fs.readFileSync(input));
let t = topology(g);
t = presimplify(t, planarTriangleArea);
t = simplify(t, +minArea);
t = quantize(t, +q);
// drop rivers/lakes pieces that vanished
fs.writeFileSync(output, JSON.stringify(t));
console.log('arcs', t.arcs.length, 'bytes', fs.statSync(output).size);
