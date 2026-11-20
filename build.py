#!/usr/bin/env python3
"""Turns an OSM extract of one city into a road pack for My Camera's street stamp.

Pack (.rpk) = gzip of, big-endian (Java DataInputStream):
  "RPK1", int minLatE6, minLonE6, maxLatE6, maxLonE6,
  int nNames, then each name as Java writeUTF (u16 length + UTF-8),
  int nWays, then per way: int nameIndex, int nPoints, int latE6, int lonE6 of the first point,
  then for each further point the change in latE6 and lonE6 as zigzag varints (small = 1-2 bytes).
Only named roads cars use (same list as RoadSnap.HIGHWAYS). Data (c) OpenStreetMap contributors, ODbL.
usage: build.py city.osm.pbf out.rpk minlat minlon maxlat maxlon
"""
import gzip, struct, sys
import osmium

HW = {"motorway", "trunk", "primary", "secondary", "tertiary", "unclassified", "residential", "living_street", "road",
      "motorway_link", "trunk_link", "primary_link", "secondary_link", "tertiary_link"}

src, out = sys.argv[1], sys.argv[2]
bbox = [float(x) for x in sys.argv[3:7]]
names, name_ix, ways = [], {}, []

class H(osmium.SimpleHandler):
    def way(self, w):
        if w.tags.get("highway") not in HW: return
        name = (w.tags.get("name") or "").strip().replace("\0", "")
        if not name: return
        pts = []
        for n in w.nodes:
            if n.location.valid():
                pts.append((round(n.location.lat * 1e6), round(n.location.lon * 1e6)))
        if len(pts) < 2: return
        if name not in name_ix:
            name_ix[name] = len(names); names.append(name)
        ways.append((name_ix[name], pts))

def varint(b, v):
    z = (v << 1) ^ (v >> 63)
    while z >= 0x80:
        b.append((z & 0x7F) | 0x80); z >>= 7
    b.append(z)

H().apply_file(src, locations=True)
b = bytearray(b"RPK1")
b += struct.pack(">iiii", *[round(v * 1e6) for v in bbox])
b += struct.pack(">i", len(names))
for n in names:
    e = n.encode("utf-8")[:65535]
    b += struct.pack(">H", len(e)) + e
b += struct.pack(">i", len(ways))
for ni, pts in ways:
    b += struct.pack(">ii", ni, len(pts))
    b += struct.pack(">ii", pts[0][0], pts[0][1])
    for (pa, po), (la, lo) in zip(pts, pts[1:]):
        varint(b, la - pa); varint(b, lo - po)
with gzip.open(out, "wb", 9) as f: f.write(b)
print(f"{out}: {len(ways)} roads, {len(names)} names, {sum(len(p) for _, p in ways)} points, raw {len(b)//1024} KB")
