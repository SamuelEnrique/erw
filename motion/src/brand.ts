// Energy Research Warehouse (ERW), session 274: the brand of docs/brand.md, for the motion videos.
// White page, Source Serif 4 for display, IBM Plex Sans for text, IBM Plex Mono for figures, cardinal the only accent.
import { loadFont as loadSerif } from "@remotion/google-fonts/SourceSerif4";
import { loadFont as loadSans } from "@remotion/google-fonts/IBMPlexSans";
import { loadFont as loadMono } from "@remotion/google-fonts/IBMPlexMono";

export const SERIF = loadSerif("normal", { weights: ["600"], subsets: ["latin"] }).fontFamily;
export const SANS = loadSans("normal", { weights: ["400", "500", "600"], subsets: ["latin"] }).fontFamily;
export const MONO = loadMono("normal", { weights: ["400", "500"], subsets: ["latin"] }).fontFamily;

export const C = {
  page: "#FFFFFF",
  fog: "#F7F3EA",
  rule: "#E3DED1",
  captions: "#6B675F",
  ink: "#2E2D29",
  cardinal: "#8C1515",
};

// docs/brand.md, "Chart series": in this order. The highlighted series takes cardinal.
export const SERIES = ["#8C1515", "#2E2D29", "#3C6E9E", "#6B675F", "#8F8A80"];

export const FPS = 30;
