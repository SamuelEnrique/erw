// Moves a node process's clock forward, for scripts/suite_shifted.py (session 534).
// Loaded through NODE_OPTIONS="--require <this file>" with ERW_CLOCK_SHIFT_SECONDS set:
// Date.now(), new Date() with no argument and Date() called as a function read a clock
// that many seconds ahead; a Date built from a value is unchanged. Without the variable
// it does nothing.
"use strict";
const shift = Number(process.env.ERW_CLOCK_SHIFT_SECONDS || "");
if (Number.isFinite(shift) && shift !== 0) {
  const RealDate = Date;
  const off = shift * 1000;
  const now = () => RealDate.now() + off;
  globalThis.Date = new Proxy(RealDate, {
    construct(target, args, newTarget) {
      if (args.length === 0) return Reflect.construct(target, [now()], newTarget);
      return Reflect.construct(target, args, newTarget);
    },
    apply() {
      return new RealDate(now()).toString();
    },
    get(target, prop, receiver) {
      if (prop === "now") return now;
      return Reflect.get(target, prop, receiver);
    },
  });
}
