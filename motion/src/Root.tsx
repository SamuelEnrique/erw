// The one composition, Motion: its size and length come from the spec it is given (specs.mjs writes them).
import React from "react";
import { Composition } from "remotion";
import { FPS } from "./brand";
import { DrawOn } from "./DrawOn";
import { Frame } from "./Frame";
import { CountUp, Reorder, RollCall } from "./Others";
import type { Spec } from "./types";

export const Motion: React.FC<{ spec: Spec }> = ({ spec }) => (
  <Frame spec={spec}>
    {spec.type === "draw-on" && <DrawOn spec={spec} />}
    {spec.type === "count-up" && <CountUp spec={spec} />}
    {spec.type === "roll-call" && <RollCall spec={spec} />}
    {spec.type === "reorder" && <Reorder spec={spec} />}
  </Frame>
);

const placeholder: Spec = {
  id: "placeholder", type: "count-up", kicker: "ERW", title: "A spec is passed at render time", subtitle: "", source: "",
  width: 1080, height: 1350, frames: 300, value: 0, decimals: 0, unit: "", sentence: "",
};

export const Root: React.FC = () => (
  <Composition
    id="Motion"
    component={Motion}
    durationInFrames={300}
    fps={FPS}
    width={1080}
    height={1350}
    defaultProps={{ spec: placeholder }}
    calculateMetadata={({ props }) => ({ durationInFrames: props.spec.frames, width: props.spec.width, height: props.spec.height })}
  />
);
