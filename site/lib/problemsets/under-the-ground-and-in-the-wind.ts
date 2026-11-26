// Energy Research Warehouse (ERW) site, session 8901 (chain 507, part C): problem set "What is under the ground and in the
// wind". Reading the resource map's layers and their units, and why a resource is not a power plant. Every figure is read
// from the committed list of layers the map reads, site/data/resources/manifest.json (written by
// warehouse/connectors/resource_layers.py, drawn by the resources tab of /map, app/resources/view.tsx), and carries its
// pf| key (lib/pagefile.ts). A layer is found by its id ("@id=..."), so a list rebuilt in another order gives the same
// figures. The list names no source table of the warehouse: its layers are publishers' files, each with its own source
// and terms in the list.
import type { Question } from "@/lib/problems";
import type { Segment } from "@/lib/pagefile";
import { calc, fig, open, type Built, type Meta, type SetGuide } from "./common";

const F = "resources/manifest.json";
type Legend = { min: number; max: number };
type Layer = { id: string; title: string; unit?: string; value_label?: string; publisher?: string; vintage?: string; source_resolution?: string; legend?: Legend; other_extents?: { extent: string; legend?: Legend }[] };
type Manifest = { layers: Layer[] };

export const META: Meta = {
  slug: "under-the-ground-and-in-the-wind", title: "What is under the ground and in the wind",
  line: "The resource map's layers read in their own units: the wind and the sun, a modelled wind farm's capacity factor, geothermal sites, power that dams without turbines could make, and biomass counted in tonnes.",
  teacher: "About 40 minutes. Prerequisites: a unit and what it measures (m/s, kWh per square metre per day, MW, MWh, tonnes), a ratio, a share. Students should open the resources tab of /map, switch each layer on and read its legend, and open the Method note at the foot for each layer's unit, vintage and grain. Some figures (a layer's totals) are in the list of layers itself, site/data/resources/manifest.json.",
  pages: [{ href: "/map?tab=resources", label: "Where the resources are" }, { href: "/data/methods/resources", label: "Method: the resource layers" }],
};

export const GUIDE_ENTRY: SetGuide = {
  can: "read a resource layer's legend and unit, tell a resource estimate from a power plant's output, and turn MWh per MW into hours",
  grids: ["the contiguous United States (each layer's own extent)"],
  tables: [],
  skills: ["a unit and what it measures", "a map cell as a mean", "a capacity factor", "MWh per MW as hours", "a share of a total"],
  order: ["r2", "r1", "r3", "r6", "r4", "r5"],
  files: [F],
};

export async function build(): Promise<Built> {
  const m = open<Manifest>(F);
  const L = (id: string) => {
    const l = m.layers.find((x) => x.id === id);
    if (!l) throw new Error(`no layer ${id} in site/data/resources/manifest.json`);
    return l;
  };
  const at = (id: string, path: Segment[], u: string) => fig(F, ["layers", { id }, ...path], u);
  const ghi = L("solar_ghi"), dni = L("solar_dni"), wind = L("wind_speed_100m"), cf = L("wind_capacity_factor"), geo = L("geothermal_hydrothermal_sites");
  const npd = L("hydropower_npd"), bio = L("biomass");
  // Session 9601 (chain 620, the browser read of 20 November 2026): the legend a student reads on the map is one scale
  // over every part of a layer (the contiguous states, and Alaska and Hawaii where the layer has them: legendOf in
  // lib/resources.ts), so its ends are the lowest low and the highest high among the parts. The set read the contiguous
  // states' range alone (2.81 to 6.50 for the sun) while the map's legend ran from 1.6 to 6.9. Each end is still one
  // figure of the list, and its hover names the part it is read from.
  const legendEnd = (id: string, end: "min" | "max", u: string) => {
    const l = L(id);
    let best: { v: number; path: Segment[]; where: string } = { v: l.legend?.[end] ?? NaN, path: ["legend", end], where: "the contiguous states" };
    for (const x of l.other_extents ?? []) {
      const v = x.legend?.[end];
      if (typeof v === "number" && (!Number.isFinite(best.v) || (end === "min" ? v < best.v : v > best.v))) best = { v, path: ["other_extents", { extent: x.extent }, "legend", end], where: x.extent.split(",")[0] };
    }
    return { fig: at(id, best.path, u), where: best.where };
  };
  const parts = (id: string) => ["the contiguous states", ...(L(id).other_extents ?? []).map((x) => x.extent.split(",")[0])];

  // ---------------------------------------------------------------- worked example: the sun's range on the map
  const gLow = legendEnd("solar_ghi", "min", ghi.unit ?? ""), gHigh = legendEnd("solar_ghi", "max", ghi.unit ?? "");
  const gl = gLow.fig, gh = gHigh.fig;
  const example: Question = {
    id: "rx", tables: [],
    q: `Switch on the layer "${ghi.title}" (${ghi.value_label}). What are the lowest and the highest values of its legend, and the highest is how many times the lowest?`,
    answer: ["Lowest ", gl, ", highest ", gh, ": the sunniest cell receives ", calc("ratio", gh, gl, "times"), " the energy per square metre of the least sunny."],
    line: [gh, " / ", gl, " = ", calc("ratio", gh, gl, "times")],
    steps: [[`On the resources tab of /map, switch on ${ghi.title}; the legend runs from its lowest to its highest value, in ${ghi.unit}, over every part of the layer (${parts("solar_ghi").join("; ")}), and prints one decimal. In site/data/resources/manifest.json the layer with id solar_ghi holds a legend for the contiguous states and one for each of its other extents: the map's legend runs from the lowest of their lows (${gLow.where}) to the highest of their highs (${gHigh.where}). The answer divides the list's own values, which hold more decimals than the legend prints, so a ratio of the legend's rounded ends can differ in its last digit.`],
      ["Lowest ", gl, ", highest ", gh, "."], ["Divide: ", gh, " / ", gl, " = ", calc("ratio", gh, gl, "times"), "."]],
    why: `A layer's unit says what is counted: here energy from the sun falling on a square metre in an average day, from ${ghi.publisher}, not the output of any panel.`,
  };

  // ---------------------------------------------------------------- r1: the wind, the map's cells against the source's
  const wl = legendEnd("wind_speed_100m", "max", wind.unit ?? "").fig, ws = at("wind_speed_100m", ["source_stats", "max"], wind.unit ?? "");
  const q1: Question = {
    id: "r1", tables: [],
    q: `The layer "${wind.title}": what is the highest value of its legend, what is the highest value in the source's own cells (the list's source_stats, max), and how far apart are they? Why is the map's lower?`,
    answer: ["The legend's highest ", wl, ", the source's highest ", ws, ": the map's is lower by ", calc("diff", ws, wl, wind.unit ?? ""), ", because each map cell is the mean of the source's cells inside it."],
    line: [ws, " - ", wl, " = ", calc("diff", ws, wl, wind.unit ?? "")],
    // session 10229 (the problems audit, finding 4): the legend prints one decimal; the key subtracts the list's value
    steps: [[`Switch on ${wind.title} and read the legend's top; or the layer wind_speed_100m, legend, max: `, wl, ". The legend prints it to one decimal; the answer subtracts the list's own value, so a difference from the legend's rounded top can differ in its last digit."],
      [`The source's own grain is ${wind.source_resolution}; the list's source_stats, max, is the highest of its cells: `, ws, "."],
      ["Subtract: ", ws, " - ", wl, " = ", calc("diff", ws, wl, wind.unit ?? ""), ". The Method note says a coarser cell is the mean of the source's cells inside it, and a mean is never above the highest of what it averages."]],
    why: "A map has to average a fine source into larger cells, which lowers the peaks: the windiest spot is windier than any cell of the map shows.",
  };

  // ---------------------------------------------------------------- r2: two measures of the sun
  const dHigh = legendEnd("solar_dni", "max", dni.unit ?? ""), dh = dHigh.fig;
  const q2: Question = {
    id: "r2", tables: [],
    q: `Two solar layers share a unit (${ghi.unit}): "${ghi.title}" and "${dni.title}". What is the highest value of each legend, and the second's is how many times the first's?`,
    answer: [`${ghi.title} `, gh, `; ${dni.title} `, dh, ": ", calc("ratio", dh, gh, "times"), "."],
    line: [dh, " / ", gh, " = ", calc("ratio", dh, gh, "times")],
    steps: [[`Switch on each layer in turn and read the legend's top; or, in the list, the highest of each layer's legends over its parts (${gHigh.where} for solar_ghi, ${dHigh.where} for solar_dni): `, gh, " and ", dh, "."],
      ["Divide: ", dh, " / ", gh, " = ", calc("ratio", dh, gh, "times"), "."]],
    why: "Global horizontal irradiance is the sunlight on a flat surface; direct normal irradiance is the beam on a surface turned to face the sun. In a clear desert the direct beam is the larger, which is why plants that track the sun or concentrate it are built there.",
  };

  // ---------------------------------------------------------------- r3: a modelled wind farm's capacity factor
  const cm = at("wind_capacity_factor", ["stats", "mean"], cf.unit ?? ""), cx = at("wind_capacity_factor", ["stats", "max"], cf.unit ?? "");
  const belowFull = cx.v < 1;  // a capacity factor below one: less than full power on average
  const q3: Question = {
    id: "r3", tables: [],
    q: `The layer "${cf.title}" (${cf.value_label}) is a ${cf.unit}. What are the mean and the highest values the list gives for it, and the highest is how many times the mean?`,
    answer: ["Mean ", cm, ", highest ", cx, ": the best place is ", calc("ratio", cx, cm, "times"), " the mean. ",
      belowFull ? "Even there a wind farm makes less in a year than it would at full power every hour." : "The list's highest reaches full power."],
    line: [cx, " / ", cm, " = ", calc("ratio", cx, cm, "times")],
    steps: [["In site/data/resources/manifest.json, the layer wind_capacity_factor, stats: mean ", cm, ", max ", cx, ". The legend on the map runs to the same top."],
      ["A capacity factor is the energy a plant makes over the energy it would make at full power every hour: a ratio, so multiply by 100 for a percent."],
      ["Divide: ", cx, " / ", cm, " = ", calc("ratio", cx, cm, "times"), "."]],
    why: "Nameplate megawatts are not energy: a wind farm's output follows the wind, so the energy it makes in a year is its capacity times the hours times its capacity factor.",
  };

  // ---------------------------------------------------------------- r4: geothermal sites, one against all
  const gt = at("geothermal_hydrothermal_sites", ["total_mwe_mean"], geo.unit ?? ""), gx = at("geothermal_hydrothermal_sites", ["stats", "max"], geo.unit ?? "");
  const gn = at("geothermal_hydrothermal_sites", ["stats", "n"], "sites");
  const q4: Question = {
    id: "r4", tables: [],
    q: `The layer "${geo.title}": how many sites does it hold, what is the sum of their estimated output (${geo.value_label}), the largest site's, and what share of the sum is the largest?`,
    answer: [gn, ": in all ", gt, "; the largest ", gx, ", or ", calc("pct", gx, gt, "%"), " of the sum."],
    line: [gx, " / ", gt, " x 100 = ", calc("pct", gx, gt, "%")],
    steps: [["In site/data/resources/manifest.json, the layer geothermal_hydrothermal_sites: stats, n, ", gn, "; total_mwe_mean, ", gt, "; stats, max, ", gx, "."],
      ["Share: ", gx, " / ", gt, " x 100 = ", calc("pct", gx, gt, "%"), "."]],
    why: `MWe is megawatts of electricity a resource is estimated to support (${geo.publisher}), not a plant that exists: a resource estimate says what could be built, and much of it may never be.`,
  };

  // ---------------------------------------------------------------- r5: dams without turbines, MWh per MW
  const nc = at("hydropower_npd", ["total_cap_mw"], "MW"), ng = at("hydropower_npd", ["total_gen_mwh_yr"], "MWh a year");
  const q5: Question = {
    id: "r5", tables: [],
    q: `The layer "${npd.title}" holds dams that make no power today. What capacity and what yearly energy does it estimate for them in all, and how many hours of full output a year is that energy?`,
    answer: ["Capacity ", nc, ", energy ", ng, ": ", calc("ratio", ng, nc, "hours"), " of full output a year."],
    line: [ng, " / ", nc, " = ", calc("ratio", ng, nc, "hours")],
    steps: [["In site/data/resources/manifest.json, the layer hydropower_npd: total_cap_mw ", nc, " and total_gen_mwh_yr ", ng, "."],
      ["MWh divided by MW is hours: ", ng, " / ", nc, " = ", calc("ratio", ng, nc, "hours"), ", the hours the dams would need at full power to make a year's energy."]],
    why: "Hours of full output set against all the hours of a year are a capacity factor in another form: an estimate of energy, from a capacity that is not built.",
  };

  // ---------------------------------------------------------------- r6: biomass counted in tonnes
  const bt = at("biomass", ["national_total"], bio.unit ?? ""), bc = at("biomass", ["parts", "CropRes"], bio.unit ?? "");
  const q6: Question = {
    id: "r6", tables: [],
    q: `The layer "${bio.title}" is counted in ${bio.unit}. What is its national total, how much of it is crop residue (the part CropRes), and what share is that?`,
    answer: ["In all ", bt, "; crop residue ", bc, ", or ", calc("pct", bc, bt, "%"), ". A tonne is a mass, not energy: the map does not say how much power it would make."],
    line: [bc, " / ", bt, " x 100 = ", calc("pct", bc, bt, "%")],
    steps: [["In site/data/resources/manifest.json, the layer biomass: national_total ", bt, "; parts, CropRes, ", bc, "."], ["Share: ", bc, " / ", bt, " x 100 = ", calc("pct", bc, bt, "%"), "."]],
    why: "To turn tonnes into energy needs the heat in each kind of biomass and the efficiency of the plant that burns it, which the layer does not give; a figure in the wrong unit cannot be compared with a power plant.",
  };

  return { example, questions: [q1, q2, q3, q4, q5, q6] };
}
