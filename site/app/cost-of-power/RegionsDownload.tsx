"use client";
// Chain 780 (session 11600): the downloads of "Where the next gigawatts can go": the rows and columns shown, as a CSV
// in the page's own figures, with a Python and a Stata reader of it. Made in the browser on the press, as the tab's
// other downloads are (components/largeload/Download.tsx): no route and no request.
import { Download } from "@/components/largeload/Download";
import { CSV_NAME, pythonReader, stataReader } from "./regions";

export function RegionsDownload({ csv, rows, cols }: { csv: string; rows: number; cols: number }) {
  const nHead = csv.split("\n").findIndex((l) => !l.startsWith("#"));
  return (
    <span data-sr-downloads="1">
      <Download make={() => csv} name={CSV_NAME} mark={{ "data-sr-csv": `${rows}|${cols}`, "data-download": "csv" }}>CSV of these {rows} places and {cols} columns</Download>,{" "}
      <Download make={() => pythonReader(nHead)} name="erw-regions-side-by-side.py" type="text/x-python" mark={{ "data-download": "python" }}>Python</Download>,{" "}
      <Download make={() => stataReader(nHead)} name="erw-regions-side-by-side.do" type="text/plain" mark={{ "data-download": "stata" }}>Stata</Download>
    </span>
  );
}
