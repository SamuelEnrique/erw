"use client";
// Session 182, part 4: what the request flow hands to the impact study's form, which the page creates and the flow
// hosts. `between` is placed between the form's inputs and its Ask button (step two, the picker of chart forms);
// `onAsked` tells the flow which request the form queued, so that the address keeps it. Outside the flow the context
// is null and the form is what it was. (A context, not cloned props: an element the page hands to a client component
// arrives as a reference, which cannot be cloned.)
import { createContext, type ReactNode } from "react";

export type FlowHostValue = { between: ReactNode; onAsked: (id: string) => void };
export const FlowHost = createContext<FlowHostValue | null>(null);
