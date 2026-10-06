// Session 123: the site's own copy of grid_stress_yearly, one file per grid (written by
// warehouse/derived/mix_stress.py --snapshot; tests/test_session123.py holds each file equal to the table). The page is
// in review, so nothing is read from the database.
import caiso from "@/data/stress/caiso.json";
import ercot from "@/data/stress/ercot.json";
import isone from "@/data/stress/isone.json";
import miso from "@/data/stress/miso.json";
import nyiso from "@/data/stress/nyiso.json";
import pjm from "@/data/stress/pjm.json";
import spp from "@/data/stress/spp.json";
import type { Files, GridFile } from "@/lib/stress";

export const FILES: Files = {
  caiso: caiso as unknown as GridFile, ercot: ercot as unknown as GridFile, isone: isone as unknown as GridFile, miso: miso as unknown as GridFile,
  nyiso: nyiso as unknown as GridFile, pjm: pjm as unknown as GridFile, spp: spp as unknown as GridFile,
};
