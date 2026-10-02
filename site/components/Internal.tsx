"use client";
// Session 67: is this browser in the internal view of the release gate (lib/release.ts)? /internal/unlock sets a
// readable cookie beside the httpOnly one the proxy checks; this reads it after the page loads, so the page a server
// renders (and caches) is always the visitor's view, and an internal browser redraws its links and menu once.
import { useSyncExternalStore } from "react";
import { VIEW } from "@/lib/release";

const subscribe = () => () => {};
const read = () => document.cookie.split(";").some((c) => c.trim() === `${VIEW}=internal`);

export function useInternal(): boolean {
  return useSyncExternalStore(subscribe, read, () => false);
}
