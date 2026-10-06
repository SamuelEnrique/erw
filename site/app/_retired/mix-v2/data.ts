// Session 94: the site's own copy of generation_mix_hourly_profile and generation_mix_records, one file per grid
// (written by warehouse/derived/mix_profile.py --snapshot; tests/test_session94.py holds each file equal to the table).
// The page is in review and its two tables are not in the live set yet, so nothing is read from the database.
import caiso from "@/data/mix/caiso.json";
import ercot from "@/data/mix/ercot.json";
import isone from "@/data/mix/isone.json";
import miso from "@/data/mix/miso.json";
import nyiso from "@/data/mix/nyiso.json";
import pjm from "@/data/mix/pjm.json";
import spp from "@/data/mix/spp.json";
import type { Files, GridFile } from "@/lib/mix2";

export const FILES: Files = {
  caiso: caiso as unknown as GridFile, ercot: ercot as unknown as GridFile, isone: isone as unknown as GridFile, miso: miso as unknown as GridFile,
  nyiso: nyiso as unknown as GridFile, pjm: pjm as unknown as GridFile, spp: spp as unknown as GridFile,
};
