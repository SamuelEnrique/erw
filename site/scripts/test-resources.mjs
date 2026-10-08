// Energy Research Warehouse (ERW) site, session 146: the pure functions of "Where the resources are" (lib/resources.ts).
//
//   node scripts/test-resources.mjs
//
// No site, no browser, no network. The grid decoding, the cell a place falls in, the level drawn at a zoom, the plane
// and its inverse, the address that holds the view, whether a place is inside a shape, and the toggles made from a
// manifest. Where the data side's manifest and files are on the machine, every grid file of it is decoded and its
// values are read back against an independent decoding (Node's Buffer); on a machine without them that part is
// skipped and says so. Exit 1 on a failure.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as R from "../lib/resources.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const close = (a, b, tol = 1e-9) => Math.abs(a - b) <= tol;

// a grid of 4 columns and 3 rows, encoded here with Buffer (not with the page's code)
const stored = [10, 20, 30, 40, 50, 65535, 70, 80, 90, 100, 110, 65535];
const buf = Buffer.alloc(stored.length * 2);
stored.forEach((v, i) => buf.writeUInt16LE(v, 2 * i));
const file = { lon0: -100, lat0: 40, dlon: 0.5, dlat: 0.25, ncols: 4, nrows: 3, scale: 0.01, offset: 2, nodata: 65535, encoding: "uint16-le-base64", values: buf.toString("base64") };
const g = R.decodeGrid(file);
check(g.data.length === 12 && stored.every((v, i) => g.data[i] === v), "a grid decodes to its stored values, row-major from the north");
check(close(R.valueAt(g, -99.9, 39.9), 10 * 0.01 + 2) && close(R.valueAt(g, -98.1, 39.9), 40 * 0.01 + 2) && close(R.valueAt(g, -99.9, 39.3), 90 * 0.01 + 2), "a value is stored * scale + offset, at the cell the place falls in");
check(R.valueAt(g, -99.4, 39.6) === null && R.valueAt(g, -98.2, 39.3) === null, "an empty cell is null, never a number");
check(R.cellOf(g, -100, 40)?.col === 0 && R.cellOf(g, -100, 40)?.row === 0 && R.cellOf(g, -98.0001, 39.2501)?.col === 3 && R.cellOf(g, -98.0001, 39.2501)?.row === 2, "the west and north edges belong to the first cell; the last cell ends at the east and south edges");
check(R.cellOf(g, -98, 39.9) === null && R.cellOf(g, -100.01, 39.9) === null && R.cellOf(g, -99, 40.01) === null && R.cellOf(g, -99, 39.25) === null && R.valueAt(g, -120, 10) === null, "a place outside the grid has no cell and no value");
check((() => { try { R.decodeGrid({ ...file, ncols: 5 }); return false; } catch { return true; } })() && (() => { try { R.decodeGrid({ ...file, encoding: "float32" }); return false; } catch { return true; } })(), "a file whose bytes do not match its size, or of another encoding, is refused");
check(R.decodeGrid({ ...file, dlat: -0.25 }).dlat === 0.25, "a negative row height is read as its size");
check(R.decimalsOf(0.01) === 2 && R.decimalsOf(0.001) === 3 && R.decimalsOf(1) === 0 && R.decimalsOf(0.1) === 1 && R.decimalsOf(0.005) === 3 && R.show(7.5, 2) === "7.50", "a value is printed to the decimals its scale stores");

// the level by zoom
const levels = [0.025, 0.2, 0.05, 0.1].map((c) => ({ file: `x_${c}.json`, cell_deg: c }));
check(R.levelFor(levels, 3).cell_deg === 0.2, "zoomed out past the coarsest level's pixel, the coarsest is drawn");
check(R.levelFor(levels, 10).cell_deg === 0.1 && R.levelFor(levels, 15).cell_deg === 0.05 && R.levelFor(levels, 29.9).cell_deg === 0.05 && R.levelFor(levels, 30).cell_deg === 0.025 && R.levelFor(levels, 5000).cell_deg === 0.025,
  `the level drawn is the finest whose cells are at least ${R.MIN_CELL_PX} of a pixel wide`);
check(R.levelFor(levels, 5000, R.MIN_CELL_PX, 0.05).cell_deg === 0.05 && R.levelFor(levels, 5000, R.MIN_CELL_PX, 0.2).cell_deg === 0.2, "a floor on the cell size holds at any zoom");
check(R.levelFor([], 10) === null && R.levelFor([{ file: "a", cell_deg: 0.1 }], 0.001).cell_deg === 0.1, "no level, no pick; one level is always the pick");
{
  // finer as the zoom grows, never coarser
  let last = Infinity, mono = true;
  for (let px = 1; px < 400; px *= 1.3) { const c = R.levelFor(levels, px).cell_deg; if (c > last) mono = false; last = c; }
  check(mono, "zooming in never picks a coarser level");
}

// the plane and its inverse
{
  const v = { z: 3.7, lon: -101.3, lat: 33.2 }, W = 987, H = 571;
  const [x, y] = R.toScreen(v, W, H, -97.25, 30.5), [lon, lat] = R.toPlace(v, W, H, x, y);
  check(close(lon, -97.25, 1e-9) && close(lat, 30.5, 1e-9), "a place drawn and read back is the same place");
  const [cx, cy] = R.toScreen(v, W, H, v.lon, v.lat);
  check(close(cx, W / 2) && close(cy, H / 2), "the view's centre is the middle of the box");
  const [x1] = R.toScreen({ z: 1, lon: R.HOME.lon, lat: R.HOME.lat }, W, H, R.HOME.lon - R.HOME.spanLon / 2, R.HOME.lat), [, y1] = R.toScreen({ z: 1, lon: R.HOME.lon, lat: R.HOME.lat }, W, H, R.HOME.lon, R.HOME.lat + R.HOME.spanLat / 2);
  check(x1 >= -1e-6 && y1 >= -1e-6 && (close(x1, 0, 1e-6) || close(y1, 0, 1e-6)), "at zoom 1 the contiguous states fill the box");
  const z2 = R.zoomAbout(v, W, H, 200, 150, 2.5), before = R.toPlace(v, W, H, 200, 150), after = R.toPlace(z2, W, H, 200, 150);
  check(close(z2.z, 9.25) && close(before[0], after[0], 1e-9) && close(before[1], after[1], 1e-9), "zooming about a point keeps the place under it");
  check(R.zoomAbout(v, W, H, 0, 0, 1e9).z === R.Z_MAX && R.zoomAbout(v, W, H, 0, 0, 1e-9).z === R.Z_MIN && R.clampView({ z: 1, lon: 40, lat: -80 }).lon === -60, "the zoom and the centre stay inside their limits");
  check(close(R.KX, Math.cos(37.5 * Math.PI / 180)), "longitude is squeezed by the cosine of 37.5 degrees");
}

// the address
{
  const layers = [{ id: "oil_gas_basins", title: "Sedimentary basins", group: "oil and gas" }, { id: "wind_speed_100m", title: "Wind speed at 100 m", group: "wind" }];
  const bare = R.parseShown("", layers);
  check(JSON.stringify(bare.on) === '["wind_speed_100m"]' && bare.view.z === 1 && bare.view.lon === R.HOME.lon && bare.view.lat === R.HOME.lat && bare.fuel === null, "a bare address is the contiguous states with wind speed on");
  check(JSON.stringify(R.parseShown("", [layers[0]]).on) === '["oil_gas_basins"]' && R.parseShown("", []).on.length === 0, "without wind speed the first layer held is on; with no layer, none");
  const s = { on: ["oil_gas_basins", "plants_operating", "queue"], view: { z: 6.25, lon: -101.5, lat: 31.75 }, fuel: ["solar", "wind"] };
  const q = R.shownQuery(s), back = R.parseShown(q, layers);
  check(q === "?on=oil_gas_basins,plants_operating,queue&z=6.25&c=-101.5,31.75&fuel=solar,wind" && JSON.stringify(back) === JSON.stringify(s), `a view written to the address and read back is the same view (${q})`);
  const odd = R.parseShown("?on=nothing,queue,queue&z=abc&c=1e9,x", layers);
  check(JSON.stringify(odd.on) === '["queue"]' && odd.view.z === 1 && odd.view.lon === -60 && odd.view.lat === R.HOME.lat, "a layer the page does not hold is dropped, and a number it cannot read is the default");
  check(R.parseShown("?on=", layers).on.length === 0, "an address may switch every layer off");
}

// shapes
{
  const square = { type: "Polygon", coordinates: [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]], [[4, 4], [6, 4], [6, 6], [4, 6], [4, 4]]] };
  check(R.inGeometry(square, 1, 1) && !R.inGeometry(square, 5, 5) && !R.inGeometry(square, 11, 5) && !R.inGeometry(square, -1, 5), "a place is inside a polygon and outside its hole");
  const multi = { type: "MultiPolygon", coordinates: [square.coordinates, [[[20, 20], [21, 20], [21, 21], [20, 21], [20, 20]]]] };
  check(R.inGeometry(multi, 20.5, 20.5) && R.inGeometry(multi, 9, 9) && !R.inGeometry(multi, 15, 15) && !R.inGeometry({ type: "LineString", coordinates: [[0, 0], [1, 1]] }, 0.5, 0.5) && !R.inGeometry(null, 0, 0), "a multipolygon holds a place when one of its parts does; a line has no inside");
  check(JSON.stringify(R.boxOf(multi)) === "[0,0,21,21]" && R.boxOf({ type: "Polygon", coordinates: [] }) === null, "the box of a shape is its west, south, east and north");
  check(JSON.stringify(R.along(R.rampOf([200, 100, 0], [0, 0, 0]), 0.5)) === "[200,100,0]" && R.position(5, { min: 0, max: 10 }) === 0.5 && R.position(6, { min: 0, max: 10, stops: [5, 6, 7] }) === 0.5 && R.position(2.5, { min: 0, max: 10, stops: [5, 6, 7] }) === 0.125 && R.position(99, { min: 0, max: 10, stops: [5] }) === 1 && R.position(-1, { min: 0, max: 10 }) === 0 && R.positionOn(R.knotsOf({ min: 0, max: 10, stops: [7, 5, 6, 5, 99] }), 6) === 0.5 && R.positionOn([], 3) === 0.5 && R.css([1, 2, 3], 0.5) === "rgba(1,2,3,0.5)" && JSON.stringify(R.rgbOf("#eda100")) === "[237,161,0]", "the middle of a ramp is its hue; a value sits on its legend in proportion");
  const ramp = R.rampOf([237, 161, 0], [46, 45, 41]);
  const light = (c) => 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
  check(ramp.every((c, i) => i === 0 || light(c) < light(ramp[i - 1])), "a ramp runs from light to dark, one hue");
}

// a layer in several parts, its one legend, its classes
{
  const l = { id: "solar_ghi", group: "solar", title: "GHI", kind: "grid", levels: [{ file: "a_0p2.json", cell_deg: 0.2 }], legend: { min: 2.8, max: 6.5, stops: [4, 5] },
    other_extents: [{ extent: "Hawaii", levels: [{ file: "a_hawaii_0p2.json", cell_deg: 0.2 }], legend: { min: 2.9, max: 6.9 }, grid: { west: -160.6, north: 22.4, east: -154.6, south: 18.6 } }, { extent: "Nowhere", levels: [] }] };
  const py = R.pyramidsOf(l);
  check(py.length === 2 && py[0].key === "solar_ghi" && py[0].box === null && py[1].key === "solar_ghi:Hawaii" && JSON.stringify(py[1].box) === "[-160.6,18.6,-154.6,22.4]" && JSON.stringify(R.filesOf(l)) === '["a_0p2.json","a_hawaii_0p2.json"]',
    "a grid kept in several parts has a pyramid a part, each with its box, and every part's files are the layer's files");
  const lg = R.legendOf(l);
  check(lg.min === 2.8 && lg.max === 6.9 && JSON.stringify(lg.stops) === "[4,5]" && R.legendOf({ ...l, legend: { kinds: ["a"] } }) === null && R.legendOf({ ...l, legend: "{}" }) === null, "one legend holds every part's range; a legend with no range is none");
  const tones = R.classTones([{ value: 1, label: "Class 1 (most favorable)" }, { value: 2, label: "Class 2" }, { value: 5, label: "Class 5 (least favorable)" }, { value: 999, label: "Class 999 (not assessed for deep EGS potential)" }]);
  check(tones[0] === 1 && tones[2] === 0.06 && tones[1] > tones[2] && tones[1] < tones[0] && tones[3] === null, "classes named from most to least run dark to light, and a class that is not assessed is no step of the scale");
  const up = R.classTones([{ value: 1, label: "< 0.1" }, { value: 2, label: "0.1 - 0.5" }, { value: 3, label: "> 15" }]);
  check(up[0] === 0.06 && up[2] === 1 && up[1] > up[0] && up[1] < up[2], "classes in rising order run light to dark");
  check(R.tickLabel(0.6, { min: 0.6, max: 2209.9 }) === "0.6" && R.tickLabel(1000, { min: 0.6, max: 2209.9 }) === "1,000" && R.tickLabel(2209.9, { min: 0.6, max: 2209.9 }) === "2,210" && R.tickLabel(0.1, { min: 0.01, max: 0.54 }) === "0.10" && R.tickLabel(2002700, { min: 0, max: 2002700 }) === "2M" && R.tickLabel(63000, { min: 0, max: 2002700 }) === "63K" && R.plainNumber(16400.7220361) === "16,400.7" && R.plainNumber(0.2419) === "0.2419",
    "a legend's ticks are short for a large range and keep the decimals a small one needs");
  const css = R.rampCss("--color-fuel-wind");
  check(css.length === 5 && css[2] === "var(--color-fuel-wind)" && css[0] === "color-mix(in srgb, var(--color-fuel-wind) 28%, #ffffff)" && css[4] === "color-mix(in srgb, var(--color-fuel-wind) 18%, var(--color-ink))" && R.alongCss("--color-fuel-wind", 0.5).includes("var(--color-fuel-wind) 100%"), "the legend's ramp in CSS is the map's ramp, step for step");
}

// the toggles
{
  const m = {
    layers: [{ id: "oil_gas_basins", group: "oil and gas", title: "Sedimentary basins", kind: "shapes", file: "oil_gas_basins.json" }, { id: "tides", group: "tidal", title: "Tidal range", kind: "grid", levels: [{ file: "tides_0p2.json", cell_deg: 0.2 }] }],
    missing: [{ id: "solar_ghi", group: "solar", title: "Global horizontal irradiance", reason: "the download was refused" }, { id: "geothermal_x", group: "geothermal", title: "Heat flow", reason: "not published openly" }],
  };
  const groups = R.toggleGroups(m), by = Object.fromEntries(groups.map((x) => [x.id, x]));
  check(groups.slice(0, 7).map((x) => x.id).join() === "wind,solar,geothermal,oil_gas,hydropower,biomass,offshore_wind" && groups[7].id === "tidal" && groups[7].items[0].held, "the groups are the owner's seven in order, then any other the manifest holds");
  check(by.oil_gas.items[0].held && by.oil_gas.items[0].layer.id === "oil_gas_basins" && by.oil_gas.items.length === 2 && !by.oil_gas.items[1].held && by.oil_gas.items[1].label === "Tight oil and shale gas plays", "a layer held is a toggle; an expected layer not held is a placeholder");
  check(by.solar.items.length === 2 && by.solar.items[0].label === "Global horizontal irradiance" && by.solar.items[0].reason === "the download was refused" && /not among/.test(by.solar.items[1].reason), "a placeholder carries the manifest's own reason where it gives one");
  check(by.geothermal.items.length === 3 && by.geothermal.items[2].label === "Heat flow" && by.geothermal.items[2].reason === "not published openly", "a missing layer nobody expected is still named, with its reason");
  check(by.wind.items.every((x) => !x.held) && by.wind.items.length === 2, "a group with nothing held shows its expected layers greyed");
  check(R.groupId("Oil and gas") === "oil_gas" && R.groupId("offshore wind") === "offshore_wind" && R.groupId("hydro") === "hydropower" && R.groupId("geothermal") === "geothermal" && R.groupId("Wind") === "wind", "a group is read as the manifest writes it");
  check(R.stemOf("wind_speed_100m_0p2.json") === "wind_speed_100m_0p2" && R.layerHref("oil_gas_basins.geojson") === "/resources/layer/oil_gas_basins" && JSON.stringify(R.filesOf(m.layers[1])) === '["tides_0p2.json"]' && JSON.stringify(R.filesOf(m.layers[0])) === '["oil_gas_basins.json"]', "a layer's file is asked for at an address without an extension, which the release gate covers");
}

// the data side's files, where they are on the machine
{
  const manifestPath = path.join(here, "..", "data", "resources", "manifest.json");
  const dirs = [path.join(here, "..", "data", "resources", "layers"), path.join(here, "..", "public", "resources-data")];
  if (!fs.existsSync(manifestPath)) console.log("note: no data/resources/manifest.json on this machine; the real files were not read");
  else {
    const m = JSON.parse(fs.readFileSync(manifestPath, "utf-8"));
    let grids = 0, shapes = 0, points = 0;
    for (const l of m.layers ?? []) {
      for (const f of R.filesOf(l)) {
        const p = dirs.map((d) => path.join(d, f)).find((x) => fs.existsSync(x));
        if (!p) continue;
        const body = JSON.parse(fs.readFileSync(p, "utf-8"));
        if (l.kind === "grid") {
          grids += 1;
          const grid = R.decodeGrid(body), raw = Buffer.from(body.values, "base64");
          let same = raw.length === 2 * grid.data.length, valid = 0;
          for (let i = 0; i < grid.data.length && same; i += 97) { if (raw.readUInt16LE(2 * i) !== grid.data[i]) same = false; }
          for (let i = 0; i < grid.data.length; i++) if (grid.data[i] !== grid.nodata) valid += 1;
          const level = [...(l.levels ?? []), ...(l.other_extents ?? []).flatMap((x) => x.levels ?? [])].find((v) => v.file === f);
          check(same && valid > 0 && close(grid.dlon, level.cell_deg, 1e-9) && close(grid.dlat, level.cell_deg, 1e-9) && (level.ncols === undefined || level.ncols === grid.ncols) && (level.nrows === undefined || level.nrows === grid.nrows),
            `${f}: ${grid.ncols} by ${grid.nrows} cells of ${grid.dlon} degrees decode as Buffer reads them; ${valid.toLocaleString("en-US")} hold a value`);
        } else if (l.kind === "shapes") {
          shapes += 1;
          check(Array.isArray(body.features) && body.features.length > 0 && body.features.every((x) => x.geometry && R.boxOf(x.geometry) && typeof x.properties?.name === "string"), `${f}: ${body.features?.length} features, each with a shape and a name`);
        } else {
          points += 1;
          check(Array.isArray(body.rows) && body.rows.length > 0 && body.rows.every((r) => Number.isFinite(r[0]) && Number.isFinite(r[1])), `${f}: ${body.rows?.length} rows, each with a longitude and a latitude`);
        }
      }
    }
    console.log(`note: the manifest's files on this machine: ${grids} grid levels, ${shapes} shape files, ${points} point files`);
  }
}

// session 159: hydropower as the manifest holds it, the gross capacity factor's placeholder, the queue grid by grid
{
  // a held hydropower layer takes the place of the expected placeholder; a missing layer the manifest names keeps its own reason
  const m = {
    layers: [
      { id: "wind_capacity_factor", group: "wind", title: "Wind capacity factor (supply curve sites)", kind: "points", file: "wind_capacity_factor.json" },
      { id: "hydropower_npd", group: "hydropower", title: "Hydropower potential at non-powered dams", kind: "points", file: "hydropower_npd.json" },
      { id: "hydropower_nsd", group: "hydropower", title: "Hydropower potential of new stream-reach development", kind: "shapes", file: "hydropower_nsd.json" },
    ],
    missing: [{ id: "wind_gross_capacity_factor", group: "wind", title: "Gross capacity factor", reason: "Not fetched: it needs a key." }],
  };
  const by = Object.fromEntries(R.toggleGroups(m).map((x) => [x.id, x]));
  check(by.hydropower.items.length === 2 && by.hydropower.items.every((x) => x.held), "two hydropower layers held are two toggles, and no greyed hydropower placeholder is left beside them");
  const gross = by.wind.items.filter((x) => !x.held && x.label === "Gross capacity factor");
  check(gross.length === 1 && gross[0].reason === "Not fetched: it needs a key." && by.wind.items.some((x) => x.held && x.layer.id === "wind_capacity_factor"),
    "the gross capacity factor is one greyed placeholder with the manifest's own reason, beside the capacity factor layer that is held");

  const ids = R.QUEUE_GRIDS.map((g) => g.id).join();
  const shown = R.QUEUE_GRIDS.filter((g) => g.shown).map((g) => g.id).join(), miso = R.QUEUE_GRIDS.find((g) => g.id === "miso"), nyiso = R.QUEUE_GRIDS.find((g) => g.id === "nyiso");
  check(ids === "ercot,spp,caiso,isone,miso,nyiso" && shown === "ercot,spp,caiso,isone", "the queue overlay knows six grids and draws four: ERCOT, SPP, CAISO, ISO-NE");
  check(miso && !miso.shown && miso.words === "paused while terms are reviewed" && R.queueLine(miso) === "MISO: paused while terms are reviewed" && miso.why.includes("You agree not use any automated means, including, without limitation, agents, robots, scripts, or spiders, to access, monitor, or copy any part of this Website or the App."),
    'MISO is not shown and reads "MISO: paused while terms are reviewed", with the sentence of its terms on hover');
  check(nyiso && !nyiso.shown && nyiso.words === "NYISO's terms do not allow it" && R.queueLine(nyiso) === "NYISO's terms do not allow it" && nyiso.why.includes("Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site") && nyiso.why.includes("All Rights Reserved."),
    'NYISO is not shown and reads "NYISO\'s terms do not allow it", with the sentences of its notice on hover');
  check(R.QUEUE_GRIDS.filter((g) => g.shown).every((g) => g.words === "" && g.why === "") && R.QUEUE_GRIDS.filter((g) => !g.shown).every((g) => g.words.length > 10 && g.why.length > 80 && !/PJM/.test(g.words + g.why)), "a grid that is shown needs no words; one that is not has its short words and its reason");
  check(R.queueGridOf("ercot_interconnection_queue") === "ercot" && R.queueGridOf("miso_interconnection_queue") === "miso" && R.queueGridOf("NYISO_interconnection_queue") === "nyiso" && R.queueGridOf("lbnl_interconnection_queue") === "other" && R.queueGridOf(null) === "other" && R.queueGridOf("") === "other",
    "a queue row's grid is read from the name of the table it came from; a table of none of the six is counted apart");
}

// session 159: the two hydropower files, where they are on the machine, against the manifest's own description
{
  const manifestPath = path.join(here, "..", "data", "resources", "manifest.json"), dir = path.join(here, "..", "data", "resources", "layers");
  const m = fs.existsSync(manifestPath) ? JSON.parse(fs.readFileSync(manifestPath, "utf-8")) : null;
  const npd = m?.layers?.find((l) => l.id === "hydropower_npd"), nsd = m?.layers?.find((l) => l.id === "hydropower_nsd");
  if (!npd || !nsd || !fs.existsSync(path.join(dir, npd.file)) || !fs.existsSync(path.join(dir, nsd.file))) console.log("note: the hydropower layers are not on this machine; their files were not read");
  else {
    const dams = JSON.parse(fs.readFileSync(path.join(dir, npd.file), "utf-8")), iv = dams.columns.indexOf("value");
    const caps = dams.rows.map((r) => r[iv]);
    check(npd.kind === "points" && npd.unit === "MW" && dams.rows.length === npd.rows && caps.every((v) => typeof v === "number" && v > 0) && close(Math.min(...caps), npd.stats.min) && close(Math.max(...caps), npd.stats.max) && close(caps.reduce((a, b) => a + b, 0) / caps.length, npd.stats.mean, 1e-9) && close(caps.reduce((a, b) => a + b, 0), npd.total_cap_mw, 1e-6),
      `the dams: ${dams.rows.length.toLocaleString("en-US")} points in MW; the file's minimum, mean, maximum and total are the manifest's (${npd.stats.min}, ${npd.stats.mean.toFixed(4)}, ${npd.stats.max}, ${npd.total_cap_mw})`);
    check(npd.hover_fields.every(([f]) => dams.columns.includes(f)) && npd.hover_fields.some(([f]) => f === "gen_mwh_yr") && npd.hover_fields.some(([f]) => f === "cf_yr") && !dams.columns.includes("dam_owner"),
      "the dams: the hover's fields are columns of the file, the generation and the capacity factor among them; no owner's name is in the file");
    const sheds = JSON.parse(fs.readFileSync(path.join(dir, nsd.file), "utf-8")), vals = sheds.features.map((f) => f.properties.value);
    check(nsd.kind === "shapes" && nsd.unit === "MW" && sheds.features.length === nsd.features && sheds.features.length === nsd.watersheds_with_capacity && vals.every((v) => typeof v === "number" && v > 0) && close(Math.min(...vals), nsd.stats.min) && close(Math.max(...vals), nsd.stats.max) && close(vals.reduce((a, b) => a + b, 0), nsd.total_p_mw, 1e-2),
      `the watersheds: ${sheds.features.length.toLocaleString("en-US")} HUC10 outlines in MW, each with the file's own total; minimum, maximum and total are the manifest's (${nsd.stats.min}, ${nsd.stats.max}, ${nsd.total_p_mw})`);
    check(sheds.features.every((f) => f.properties.kind === "HUC10 watershed" && /^\d{10}$/.test(f.properties.HUC10) && f.properties.P_MW_Sum === f.properties.value && Object.values(f.properties).every((v) => v !== -9999 && v !== -999)) && nsd.watersheds_in_file === nsd.watersheds_with_capacity + nsd.watersheds_no_reach + nsd.watersheds_coded_minus_999,
      `the watersheds: each is a HUC10 with the source's own capacity, none carries a no-value code as a number, and the ${nsd.watersheds_in_file.toLocaleString("en-US")} of the file are the ${nsd.watersheds_with_capacity.toLocaleString("en-US")} drawn, ${nsd.watersheds_no_reach.toLocaleString("en-US")} with no stream-reach and ${nsd.watersheds_coded_minus_999.toLocaleString("en-US")} coded -999`);
    const text = JSON.stringify([npd, nsd]) + fs.readFileSync(path.join(dir, npd.file), "utf-8") + fs.readFileSync(path.join(dir, nsd.file), "utf-8");
    check(!text.includes("@") && /Oak Ridge National Laboratory/.test(npd.publisher) && /Oak Ridge National Laboratory/.test(nsd.publisher) && !/^U\.S\. Geological Survey/.test(npd.publisher) && npd.terms_quote.includes("openly shared, without restriction") && nsd.terms_quote.includes("openly shared, without restriction"),
      "hydropower: the publisher is Oak Ridge National Laboratory, its data use policy is quoted, and no e-mail address is in the layers or their manifest entries");
  }
  const gone = (m?.missing ?? []).find((x) => /hydro/i.test(`${x.id} ${x.title}`)), gross = (m?.missing ?? []).find((x) => x.id === "wind_gross_capacity_factor");
  if (m) check(!gone && gross && /key issued to a named person/.test(gross.reason) && /no key is asked for/.test(gross.reason) && gross.reason.split(/(?<=\.)\s+/).length === 1,
    "the manifest names no hydropower layer as missing, and says in one sentence that a gross capacity factor needs a personal key and is not fetched");
}

// no em dash in the page's own files
{
  const files = ["lib/resources.ts", "lib/resourcesdata.ts", "app/resources/page.tsx", "app/resources/ResourceMap.tsx", "app/resources/layer/[name]/route.ts", "app/resources/overlay/plants/route.ts",
    "app/resources/overlay/queue/route.ts", "app/resources/overlay/datacenters/route.ts", "scripts/test-resources.mjs", "scripts/check-resources.mjs", "scripts/frametime-resources.mjs"];
  const dash = files.filter((f) => fs.existsSync(path.join(here, "..", f)) && fs.readFileSync(path.join(here, "..", f), "utf-8").includes(String.fromCharCode(0x2014)));
  check(dash.length === 0, `no em dash in the page's files${dash.length ? ` (${dash.join(", ")})` : ""}`);
}

console.log(bad ? `${bad} of ${n} failed` : `all ${n} passed`);
process.exit(bad ? 1 : 0);
