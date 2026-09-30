import type { Metadata } from "next";
import { EventWindow, N, day, find, pickOf } from "../EventWindow";

// Session 39: Winter Storm Elliott, December 2022, event elliott_2022 of event_window_daily (docs/methods/events.md):
// PJM, MISO, SPP, NYISO, ISO-NE and ERCOT, with ERCOT's hub prices (PJM's prices are internal).
export const metadata: Metadata = { title: "Winter Storm Elliott, December 2022" };
export const revalidate = 3600;

const EV = "elliott_2022";
const FERC = "https://www.ferc.gov/sites/default/files/2024-02/24_Winter-Storm_Elliot_0207_UPDATE.pdf";
const PJM = "https://www.pjm.com/-/media/DotCom/library/reports-notices/special-reports/2023/20230717-winter-storm-elliott-event-analysis-and-recommendation-report.pdf";
const inWin = (d: string) => d >= "2022-12-19" && d <= "2022-12-29";

export default function Elliott2022() {
  return (
    <EventWindow
      event={EV}
      title="Winter Storm Elliott: six grids, December 2022"
      crumb="Winter Storm Elliott"
      start="2022-12-19"
      end="2022-12-29"
      hub="ercot:HB_HUBAVG"
      grids={[
        { entity: "eia930:PJM", name: "PJM", slug: "pjm", tz: "Eastern time" },
        { entity: "eia930:MISO", name: "MISO", slug: "miso", tz: "Eastern Standard Time all year" },
        { entity: "eia930:SWPP", name: "SPP", slug: "spp", tz: "Central time" },
        { entity: "eia930:NYIS", name: "NYISO", slug: "nyiso", tz: "Eastern time" },
        { entity: "eia930:ISNE", name: "ISO-NE", slug: "isone", tz: "Eastern time" },
        { entity: "eia930:ERCO", name: "ERCOT", slug: "ercot", tz: "ERCOT operating days, Central time" },
      ]}
      framing={
        <>
          <p className="mb-2">
            FERC and NERC write that the storm reached the central U.S. by December 21, 2022, &quot;eventually blanketing most of the eastern United States on
            December 23 and 24, and did not subside until December 26&quot;. At its worst &quot;there were 90,500 MW of coincident unplanned generating unit outages,
            derates and failures to start&quot; (<a href={FERC}>FERC, NERC and the Regional Entities, inquiry report</a>). PJM writes that &quot;at one point, almost a
            quarter of the generation capacity&quot;, 47,000 MW, was on forced outages, and that its load on Dec. 23 &quot;came in at about 136,000 MW&quot; against a forecast
            of about 127,000 MW (<a href={PJM}>PJM, Winter Storm Elliott Event Analysis and Recommendation Report</a>).
          </p>
          <p>
            This page sets the demand served by six grids, their peak hour each day and the carbon intensity of their generation over 2022-12-19 to
            2022-12-29 against the same weekdays 364 and 728 days earlier, with ERCOT&apos;s hub prices. PJM&apos;s prices are not public in the warehouse.
          </p>
        </>
      }
      caveat={
        <>
          Demand here is demand served. PJM writes that on Dec. 23 and Dec. 24 it &quot;remained reliable, was able to serve its customers&quot;; the balancing authorities
          that shed firm load were in the southeast U.S. (FERC and NERC), among them TVA and Duke, which PJM writes &quot;were both in an EEA-3 and shedding load&quot;. The baseline weeks hold Christmas too (the same weekdays of 2021 and 2020).
        </>
      }
      after={(rows) => {
        const pjm = pickOf(rows, "eia930:PJM", "demand_max_mw", "max", inWin);
        const spp = pickOf(rows, "eia930:SWPP", "demand_max_mw", "max", inWin);
        const spp23 = find(rows, "eia930:SWPP", "demand_max_mw", "2022-12-23");
        const ne = pickOf(rows, "eia930:ISNE", "demand_max_pct_vs_baseline", "max", inWin);
        return (
          <>
            <p className="mb-2">
              PJM&apos;s highest hour in EIA&apos;s data, <N r={pjm} event={EV} /> MW on {day(pjm)}, agrees with the report&apos;s &quot;about 136,000 MW&quot; on Dec. 23. The forced
              outages of Dec. 24 do not show in demand served: PJM served its load. ISO-NE barely moved: its peak hour was at most <N r={ne} event={EV} />% above the
              baseline ({day(ne)}).
            </p>
            <p>
              <strong>A date that does not match.</strong> PJM&apos;s report says SPP &quot;set a new winter peak&quot; on Dec. 23. In EIA&apos;s hourly data SPP&apos;s highest hour of the
              window is on {day(spp)}, <N r={spp} event={EV} /> MW, the hour from 18:00 Central time, which is 00:00 UTC on Dec. 23; on 2022-12-23 itself (Central
              time) its highest hour was <N r={spp23} event={EV} /> MW. The warehouse holds no SPP peak record to say which count the report used.
            </p>
          </>
        );
      }}
    />
  );
}
