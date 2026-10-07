// Session 146: the reader of a grid file for "Where the resources are", off the page's own thread. A level of a grid is
// a megabyte or more of text; read and decoded here, the map goes on answering the mouse while a finer level arrives.
// The page hands over the file's address (under /resources/layer, which the release gate covers) and gets back the
// decoded cells, as lib/resources.ts decodes them. Nothing else is asked of the network.
import { decodeGrid, type GridFile } from "../../lib/resources";

type Ask = { id: number; url: string };
const scope = self as unknown as { onmessage: ((e: MessageEvent<Ask>) => void) | null; postMessage: (m: unknown, transfer?: Transferable[]) => void };

scope.onmessage = async (e) => {
  const { id, url } = e.data;
  try {
    const res = await fetch(url, { credentials: "same-origin" });
    if (!res.ok) throw new Error(`the server answered ${res.status}`);
    if (!(res.headers.get("content-type") ?? "").includes("json")) throw new Error("this layer is in review");
    const grid = decodeGrid((await res.json()) as GridFile);
    scope.postMessage({ id, ok: true, grid }, [grid.data.buffer]);
  } catch (err) {
    scope.postMessage({ id, ok: false, error: (err as Error).message });
  }
};
