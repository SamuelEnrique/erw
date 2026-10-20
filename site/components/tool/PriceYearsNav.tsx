"use client";
// Energy Research Warehouse (ERW) site, session 352: the "Price years" choice on a page the server prices (the generator,
// the datacenter): a change rewrites the address's `py` (taken out at the default, so the bare address stays bare) and
// asks the server again, the other parameters kept.
import { useRouter } from "next/navigation";
import { DEFAULT_WINDOW, type PriceYear } from "@/lib/priceyears";
import { PriceYearsChoice } from "./PriceYearsChoice";

export function PriceYearsNav({ ws, read, value, unit, path }: { ws: PriceYear[]; read: boolean; value: string; unit: string; path: string }) {
  const router = useRouter();
  const go = (id: string) => {
    const q = new URLSearchParams(window.location.search);
    if (id === DEFAULT_WINDOW) q.delete("py"); else q.set("py", id);
    const s = q.toString();
    router.push(`${path}${s ? `?${s}` : ""}`, { scroll: false });
  };
  return <PriceYearsChoice ws={ws} read={read} value={value} onChange={go} unit={unit} />;
}
