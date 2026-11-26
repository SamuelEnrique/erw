// Energy Research Warehouse (ERW) site, session 10401 (chain 720): a reader of one of the site's CSV downloads, in Python
// or in Stata, for a reader who wants a page's rows in a session of their own. It is the form of the price board's
// reader (lib/board.ts rowsReader, session 1614), with the columns given: the "#" provenance lines printed (Python) or
// counted (Stata) and skipped, the rows loaded as they are. The Stata reader keeps the owner's rules: no line
// continuation, one empty line between commands outside a loop and none inside one, every figure column destrung with
// force. Pure: the address is given.
export type ReaderSpec = {
  /** what the CSV is, in one line ("the ERW forecast for a place, hour by hour") */
  what: string;
  /** where the function that wrote the CSV lives, for the header ("site/lib/predict.ts rowsCsv") */
  by: string;
  /** the columns read as text in Python (dates and codes that must not become numbers) */
  text: string[];
  /** the columns that hold figures: destrung in Stata */
  figures: string[];
  /** the columns the Python reader prints the first rows of */
  show: string[];
  /** a column to count the rows by, in both readers; a CSV with no such column names none */
  count?: string;
  /** the data frame's name in Python */
  name: string;
};

export function csvReader(as: "py" | "do", url: string, spec: ReaderSpec): string {
  if (as === "py") {
    return [
      `# Energy Research Warehouse (ERW): read ${spec.what} (${spec.by}).`,
      "# The CSV opens with its provenance, lines that begin with \"#\"; they are printed and skipped, and the rows are",
      "# loaded as they are. A value that is not held is empty: nothing is filled.",
      "# Needs pandas.",
      "import io",
      "import urllib.request",
      "",
      "import pandas as pd",
      "",
      `URL = "${url}"`,
      "text = urllib.request.urlopen(URL, timeout=300).read().decode(\"utf-8\")",
      "lines = text.splitlines()",
      "n = 0",
      "while n < len(lines) and lines[n].startswith(\"#\"):",
      "    n += 1",
      "print(\"\\n\".join(lines[:n]))",
      `${spec.name} = pd.read_csv(io.StringIO("\\n".join(lines[n:])), dtype={${spec.text.map((c) => `"${c}": str`).join(", ")}})`,
      `print(${spec.name}.shape)`,
      ...(spec.count ? [`print(${spec.name}["${spec.count}"].value_counts(dropna=False))`] : []),
      `print(${spec.name}[[${spec.show.map((c) => `"${c}"`).join(", ")}]].head(24))`,
      "",
    ].join("\n");
  }
  return [
    `* Energy Research Warehouse (ERW): read ${spec.what} (${spec.by}).`,
    "* The CSV opens with its provenance, lines that begin with \"#\"; they are counted and skipped, the column names are",
    "* the first line after them. A value that is not held is empty: nothing is filled.",
    "clear",
    "",
    "tempfile raw",
    "",
    `copy "${url}" \`raw'`,
    "",
    "tempname fh",
    "",
    "local n 0",
    "",
    "file open `fh' using `raw', read text",
    "",
    "file read `fh' line",
    "",
    "while r(eof) == 0 {",
    "    if substr(`\"`macval(line)'\"', 1, 1) != \"#\" continue, break",
    "    local n = `n' + 1",
    "    file read `fh' line",
    "}",
    "",
    "file close `fh'",
    "",
    "import delimited using `raw', varnames(`=`n' + 1') encoding(\"utf-8\") bindquote(strict) stringcols(_all) clear",
    "",
    ...spec.figures.flatMap((c) => [`destring ${c}, replace force`, ""]),
    ...(spec.count ? [`tabulate ${spec.count}, missing`, ""] : []),
    "describe",
    "",
  ].join("\n");
}
