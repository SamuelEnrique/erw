// Energy Research Warehouse (ERW) site, session 133: the files the one energy mix page (/mix) reads, by grid.
// Each is the site's own copy of a derived table or of a builder's output: data/mix (generation_mix_hourly_profile and
// generation_mix_records, warehouse/derived/mix_profile.py), data/clean (clean_energy_summary, mix_clean.py), data/stress
// (grid_stress_yearly, mix_stress.py), and data/mixplus, data/mix_forecast.json and data/mix_history.json
// (warehouse/derived/mix_views.py). Nothing here is read from the database.
import mix_caiso from "@/data/mix/caiso.json";
import mix_ercot from "@/data/mix/ercot.json";
import mix_isone from "@/data/mix/isone.json";
import mix_miso from "@/data/mix/miso.json";
import mix_nyiso from "@/data/mix/nyiso.json";
import mix_pjm from "@/data/mix/pjm.json";
import mix_spp from "@/data/mix/spp.json";
import clean_caiso from "@/data/clean/caiso.json";
import clean_ercot from "@/data/clean/ercot.json";
import clean_isone from "@/data/clean/isone.json";
import clean_miso from "@/data/clean/miso.json";
import clean_nyiso from "@/data/clean/nyiso.json";
import clean_pjm from "@/data/clean/pjm.json";
import clean_spp from "@/data/clean/spp.json";
import stress_caiso from "@/data/stress/caiso.json";
import stress_ercot from "@/data/stress/ercot.json";
import stress_isone from "@/data/stress/isone.json";
import stress_miso from "@/data/stress/miso.json";
import stress_nyiso from "@/data/stress/nyiso.json";
import stress_pjm from "@/data/stress/pjm.json";
import stress_spp from "@/data/stress/spp.json";
import mixplus_caiso from "@/data/mixplus/caiso.json";
import mixplus_ercot from "@/data/mixplus/ercot.json";
import mixplus_isone from "@/data/mixplus/isone.json";
import mixplus_miso from "@/data/mixplus/miso.json";
import mixplus_nyiso from "@/data/mixplus/nyiso.json";
import mixplus_pjm from "@/data/mixplus/pjm.json";
import mixplus_spp from "@/data/mixplus/spp.json";
import forecastJson from "@/data/mix_forecast.json";
import historyJson from "@/data/mix_history.json";
import type { GridFile as MixFile } from "@/lib/mix2";
import type { GridFile as CleanFile } from "@/lib/clean";
import type { GridFile as StressFile } from "@/lib/stress";

export type Slug = "caiso" | "ercot" | "isone" | "miso" | "nyiso" | "pjm" | "spp";
export type Hourly = { months: Record<string, number[]>; years: Record<string, number[]>; unit: string; status?: string; note?: string; hub?: string };
export type NuclearNote = { units: number; mean_pct: number; days: number; low: [string, number][] };
export type ExtraRecord = { key: string; label: string; unit: string; value: number; at: string; kind: "hour" | "day" | "run" };
export type PlusFile = {
  grid: Slug; name: string; tz: string; built: string; seasons: Record<string, number[]>; av_fuels: string[];
  capacity: Record<string, Record<string, number>>;
  availability: Record<string, Record<string, Record<string, number[]>>>;
  factors: Record<"price_da" | "price_rt" | "carbon" | "net_imports" | "temperature", Hourly>;
  nuclear: Record<string, Record<string, NuclearNote>>;
  records: Record<string, ExtraRecord[]>;
};
export type ErrorFigures = { n: number; actual: number; forecast: number; bias: number; mae: number };
export type ForecastSource = { first: string; last: string; all: ErrorFigures; hours: (ErrorFigures | null)[]; months: Record<string, ErrorFigures & { mae_by_hour: (number | null)[]; actual_by_hour: (number | null)[] }> };
export type ForecastFile = { built: string; grids: Record<string, { name: string; tz: string; forecast: string; sources: Record<string, ForecastSource> }> };
export type HistoryFile = { built: string; fuels: string[]; first: string; last_month: string; states: Record<string, Record<string, Record<string, number>>> };

export const MIX: Record<Slug, MixFile> = { caiso: mix_caiso as unknown as MixFile, ercot: mix_ercot as unknown as MixFile, isone: mix_isone as unknown as MixFile, miso: mix_miso as unknown as MixFile, nyiso: mix_nyiso as unknown as MixFile, pjm: mix_pjm as unknown as MixFile, spp: mix_spp as unknown as MixFile };
export const CLEAN: Record<Slug, CleanFile> = { caiso: clean_caiso as unknown as CleanFile, ercot: clean_ercot as unknown as CleanFile, isone: clean_isone as unknown as CleanFile, miso: clean_miso as unknown as CleanFile, nyiso: clean_nyiso as unknown as CleanFile, pjm: clean_pjm as unknown as CleanFile, spp: clean_spp as unknown as CleanFile };
export const STRESS: Record<Slug, StressFile> = { caiso: stress_caiso as unknown as StressFile, ercot: stress_ercot as unknown as StressFile, isone: stress_isone as unknown as StressFile, miso: stress_miso as unknown as StressFile, nyiso: stress_nyiso as unknown as StressFile, pjm: stress_pjm as unknown as StressFile, spp: stress_spp as unknown as StressFile };
export const PLUS: Record<Slug, PlusFile> = { caiso: mixplus_caiso as unknown as PlusFile, ercot: mixplus_ercot as unknown as PlusFile, isone: mixplus_isone as unknown as PlusFile, miso: mixplus_miso as unknown as PlusFile, nyiso: mixplus_nyiso as unknown as PlusFile, pjm: mixplus_pjm as unknown as PlusFile, spp: mixplus_spp as unknown as PlusFile };
export const FORECAST = forecastJson as unknown as ForecastFile;
export const HISTORY = historyJson as unknown as HistoryFile;
