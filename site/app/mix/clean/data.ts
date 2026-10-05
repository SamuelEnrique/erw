// Session 122: the site's own copy of clean_energy_summary, one file per grid (written by
// warehouse/derived/mix_clean.py --snapshot; tests/test_session122.py holds each file equal to the table). The page is
// in review, so nothing is read from the database.
import caiso from "@/data/clean/caiso.json";
import ercot from "@/data/clean/ercot.json";
import isone from "@/data/clean/isone.json";
import miso from "@/data/clean/miso.json";
import nyiso from "@/data/clean/nyiso.json";
import pjm from "@/data/clean/pjm.json";
import spp from "@/data/clean/spp.json";
import type { Files, GridFile } from "@/lib/clean";

export const FILES: Files = {
  caiso: caiso as unknown as GridFile, ercot: ercot as unknown as GridFile, isone: isone as unknown as GridFile, miso: miso as unknown as GridFile,
  nyiso: nyiso as unknown as GridFile, pjm: pjm as unknown as GridFile, spp: spp as unknown as GridFile,
};
