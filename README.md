# roadpacks

Offline street maps for My Camera, built monthly from OpenStreetMap. The camera downloads your
city so the street stamped on photos is exact, instant, and works with no signal.

- `cities.json`: the cities (id, name, country, bounding box `[minLat, minLon, maxLat, maxLon]`,
  Geofabrik region to build from).
- `build.py`: turns a city's roads into a `.rpk` pack (format described at the top of the file).
- `.github/workflows/build.yml`: builds every city and publishes the packs plus `index.json` to the
  `maps` release: `https://github.com/ngentil/roadpacks/releases/download/maps/<file>`.

Map data © OpenStreetMap contributors, available under the Open Database License (ODbL).
