"""Parse an ERW table's provenance header (the leading '#' lines) into a dict.

Energy Research Warehouse (ERW). The header format is written by
warehouse/connectors/iso_prices.py; every line is also kept verbatim under
"header", so nothing is lost if a line is not recognised here.
"""

import re
from typing import Dict, List

# Full names of the organizations that publish the source reports, for citations.
PUBLISHERS = {
    "ercot": "Electric Reliability Council of Texas (ERCOT)",
    "caiso": "California Independent System Operator (CAISO)",
    "nyiso": "New York Independent System Operator (NYISO)",
    "miso": "Midcontinent Independent System Operator (MISO)",
    "spp": "Southwest Power Pool (SPP)",
    "isone": "ISO New England (ISO-NE)",
    "pjm": "PJM Interconnection (PJM)",
    "eia": "U.S. Energy Information Administration (EIA)",
}


def _source(text: str) -> Dict[str, str]:
    """'caiso:PRC_LMP OASIS ..., https://..' or 'ERCOT NP4-190-CD DAM ..., https://..'."""
    url = ""
    m = re.search(r",\s*(https?://\S+)\s*$", text)
    if m:
        url = m.group(1)
        text = text[:m.start()]
    parts = text.split(" ", 1)
    first, rest = parts[0], (parts[1] if len(parts) > 1 else "")
    if ":" in first:
        source_id, report = first, rest
    else:
        # ERCOT style: "ERCOT NP4-190-CD DAM Settlement Point Prices"
        more = rest.split(" ", 1)
        source_id = f"{first.lower()}:{more[0]}"
        report = more[1] if len(more) > 1 else ""
    return {"source": source_id, "report": report.strip(), "report_url": url}


def parse_header(lines: List[str]) -> Dict:
    info: Dict = {"header": list(lines), "title": None, "shape": None, "window": None,
                  "forward_dam_days": [], "retrieved": None, "run_log": None,
                  "raw_files": None, "file_summary": None, "sources": [], "notes": []}
    for line in lines:
        s = line.strip()
        if s.startswith("Energy Research Warehouse (ERW):"):
            info["title"] = s.split(":", 1)[1].strip()
        elif s.startswith("Shape:"):
            info["shape"] = s
        elif s.startswith("Window:"):
            info["window"] = s[len("Window:"):].strip()
        elif s.startswith("Forward DAM days"):
            info["forward_dam_days"] = [d.strip() for d in s.split(":", 1)[1].split(",") if d.strip()]
        elif s.startswith("Retrieved:"):
            m = re.search(r"(\d{8}T\d{6}Z)", s)
            info["retrieved"] = m.group(1) if m else s[len("Retrieved:"):].strip()
        elif s.startswith("Run log:"):
            info["run_log"] = s[len("Run log:"):].split(" (")[0].strip()
        elif s.startswith("Raw files:"):
            info["raw_files"] = s[len("Raw files:"):].split(" (")[0].strip()
        elif s.startswith("File holds"):
            info["file_summary"] = s
        elif s.startswith("Source:"):
            info["sources"].append(_source(s[len("Source:"):].strip()))
        elif s.startswith("document list:") and info["sources"]:
            info["sources"][-1]["document_list"] = s.split(":", 1)[1].strip()
        elif line.startswith("  ") and info["sources"]:
            info["sources"][-1].setdefault("details", []).append(s)
        else:
            info["notes"].append(s)
    return info
