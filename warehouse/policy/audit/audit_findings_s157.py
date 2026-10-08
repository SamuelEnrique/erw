#!/usr/bin/env python3
"""Session 157: what a person read in the second 50 source documents (seed 157), for the fields code cannot settle.

Energy Research Warehouse (ERW). The same standards and the same classes as audit_findings.py (session 154), which
this module does not replace: keys are the draw numbers of runs/session157/audit/sample.csv
(warehouse/policy/eval/audit_s157_sample.csv). Every class can be checked by a second person against the saved
document: the source's words are quoted.

Classes of an extracted field: correct, wrong, missing, not_in_source, source_silent.
Classes of a model field: supported, unsupported, contradicted, judgment, blank, no_direction.

TRUE_STATES_154 and TRUE_STATES give the place as two-letter codes for both samples (audit_truth.py writes
warehouse/policy/eval/audit_states_truth.csv from them): the states where the project, plant or plan the action
concerns is, as the document says it; "" where the document names none.
"""

# Session 154's 50, from its own findings (audit_findings.py STATES) and the documents it saved: the codes of the
# states its quoted words name. Draw 7 keeps session 154's ruling (VA: the licensee's name is the only place the
# document names the state, and the two plants are in it). Draw 47 is a list of licence amendments at plants in
# several states whose title and summary name none: session 154 classed it source_silent, so "".
TRUE_STATES_154 = {
    1: "", 2: "", 3: "PA", 4: "", 5: "", 6: "", 7: "VA", 8: "TX", 9: "", 10: "CA", 11: "TX", 12: "LA;TX", 13: "WV",
    14: "AZ", 15: "ID;WA", 16: "", 17: "LA;MS", 18: "", 19: "WA", 20: "NY", 21: "CA;NM", 22: "KY", 23: "NY",
    24: "AR;TX", 25: "NY", 26: "", 27: "TX", 28: "AL", 29: "MN", 30: "NH", 31: "", 32: "LA;TX", 33: "", 34: "CA",
    35: "MI", 36: "AK", 37: "", 38: "OH", 39: "", 40: "TN", 41: "WI", 42: "", 43: "", 44: "AK", 45: "", 46: "MN",
    47: "", 48: "", 49: "", 50: "",
}

# states of the second 50: (class, the source's words or a note). The standard is session 154's: the state where the
# project, plant or plan the action concerns is, as the document says it. A contact's or an applicant's address, a
# filing room, Washington, DC and a state that stands only in a company's name do not count.
STATES = {
    1: ("source_silent", ""), 2: ("source_silent", ""), 3: ("source_silent", ""), 4: ("source_silent", ""),
    5: ("correct", "Unit 1 at the Craig Station in Craig, Colorado"),
    6: ("source_silent", "a public meeting in Washington, DC: no state"),
    7: ("correct", "RNP is located in Darlington County, South Carolina"),
    8: ("correct", "OH stands in the licensee's name, City of Hamilton, Ohio, a city of that state; the notice does not "
                   "say where the Greenup Hydroelectric Project is and names no state otherwise (session 154's ruling "
                   "on its draw 7; not settled from the document)"),
    9: ("correct", "existing utility systems in Thurston and portions of Pierce Counties, Washington"),
    10: ("source_silent", ""),
    11: ("missing", "operated by Union Electric Company near Jefferson City, Missouri ... Fulton City Hall, 18 E. 4th "
                    "Street, Fulton, Missouri (Arlington, Texas is the NRC office's dateline)"),
    12: ("missing", "facilities by Leaf River Energy Center LLC (LREC) in Smith, Jasper, and Clarke counties, Mississippi"),
    13: ("correct", "the SHINE Medical Isotope Production Facility (SHINE facility) in Rock County, Wisconsin"),
    14: ("missing", "located on the Klamath River and Fall Creek in Klamath County, Oregon and Siskiyou County, California"),
    15: ("correct", "the State of Wyoming's regulatory source material program"),
    16: ("source_silent", "names Shearon Harris Nuclear Power Plant, Unit 1 and no state"),
    17: ("missing", "on the Eel River and East Fork of the Russian River in Lake and Mendocino counties, California"),
    18: ("missing", "project locations: Julian, West Virginia, Idaho Springs, Colorado, and Blacksburg, Virginia ... "
                    "Sahuarita, Arizona ... Rolla, Missouri ... Navasota, Texas (Idaho Springs is a town in Colorado: "
                    "Idaho is not a place of the action)"),
    19: ("missing", "located on the Maury River in the City of Buena Vista, Virginia (Raleigh, NC is the new owner's address)"),
    20: ("correct", "AK stands in the licensee's name, City of Chignik, Alaska, a city of that state; this notice names "
                    "no state otherwise (the application's own notice, draw 47, places the project in the Lake and "
                    "Peninsula Borough, Alaska)"),
    21: ("correct", "regulated electric utilities in Virginia and South Carolina, respectively ... a competitive "
                    "electricity generator in Connecticut"),
    22: ("correct", "a 570 megawatt (MW) natural gas power plant in Sherman, Texas"),
    23: ("source_silent", "closed meetings held virtually: no state"),
    24: ("wrong", "located in federal waters in the Gulf of America near Louisiana (Offshore Abandonment Project): the "
                  "row's TX is the applicant's name, Texas Eastern Transmission, LP, and its address in Houston, Texas; "
                  "Louisiana is the only state the document ties to the place, and the place is federal waters near "
                  "it, not in it"),
    25: ("source_silent", ""),
    26: ("correct", "the Western Michigan nonattainment areas (Berrien, Western portion of Allegan, and Western portion "
                    "of Muskegon counties)"),
    27: ("wrong", "Emsworth Locks and Dam on the Ohio River in Allegheny County, Pennsylvania: the row's MO is the "
                  "applicant's name, FFP Missouri 5, LLC"),
    28: ("missing", "through Alabama state waters to the Mobile Bay Processing Plant and metering facilities near Coden "
                    "in Mobile County, Alabama (Houston, Texas is the applicant's address)"),
    29: ("correct", "located on the Little Androscoggin River in the City of Auburn, Maine"),
    30: ("correct", "SE Hialeah delivery facilities located in Miami-Dade County, Florida"),
    31: ("correct", "Idaho Nuclear Technology and Engineering Center site in Scoville, Butte County, Idaho"),
    32: ("missing", "Maine Department of Environmental Protection (Maine DEP) ... water quality certification (session "
                    "154's ruling on its draw 30: the state whose authority certifies the project)"),
    33: ("missing", "All of the above facilities are located in Platte and Colfax Counties, Nebraska"),
    34: ("correct", "Dummer Town Hall. Address: 75 Hill Road, Dummer, New Hampshire 03588 ... Hydro Station Drive, Dummer, NH"),
    35: ("missing", "the Pioneer small modular reactor project in Michigan"),
    36: ("correct", "All of the above facilities are located in Lafayette and Madison Counties, Florida"),
    37: ("missing", "from Pittsburg, New Hampshire to Westbrook, Maine ... from Westbrook, Maine to Dracut, Massachusetts "
                    "(Houston, Texas is the applicant's address)"),
    38: ("correct", "located in Polk, Pinellas, Hillsborough, Hardee, and DeSoto Counties, Florida"),
    39: ("source_silent", ""),
    40: ("source_silent", "a cask design's listing; the title and summary name no state"),
    41: ("missing", "located on the Blackstone River in Providence County, Rhode Island (Cambridge, MA is a contact's address)"),
    42: ("wrong", "Robert C. Byrd Locks and Dam facility on the Ohio River in Mason County, West Virginia: the row's OH "
                  "is the applicant's name, Ohio Power and Light, LLC (and the river's)"),
    43: ("source_silent", "names the Ripogenus and Penobscot Mills projects and no state"),
    44: ("missing", "The facility is located on the Licensee's site in Florissant, Missouri."),
    45: ("missing", "in Buckeye, Arizona ... operated by the Arizona Public Service Company (Arlington, Texas is the NRC "
                    "office's dateline)"),
    46: ("source_silent", "names the Kayuta Lake Hydroelectric Project and no state"),
    47: ("missing", "located on Indian Creek in the City of Chignik in the Lake and Peninsula Borough, Alaska"),
    48: ("source_silent", "a national standard; the title and summary name no state"),
    49: ("missing", "located on the Missisquoi River in Franklin County, Vermont"),
    50: ("missing", "near the Town of Fowler, in St. Lawrence County, New York"),
}

# The place of the second 50 as codes. Draws 8 and 20: the state of the city that is the licensee (flagged above).
# Draw 24: LA, the state the document names beside the federal waters where the line lies (flagged above).
TRUE_STATES = {
    1: "", 2: "", 3: "", 4: "", 5: "CO", 6: "", 7: "SC", 8: "OH", 9: "WA", 10: "", 11: "MO", 12: "MS", 13: "WI",
    14: "CA;OR", 15: "WY", 16: "", 17: "CA", 18: "AZ;CO;MO;TX;VA;WV", 19: "VA", 20: "AK", 21: "CT;SC;VA", 22: "TX",
    23: "", 24: "LA", 25: "", 26: "MI", 27: "PA", 28: "AL", 29: "ME", 30: "FL", 31: "ID", 32: "ME", 33: "NE", 34: "NH",
    35: "MI", 36: "FL", 37: "MA;ME;NH", 38: "FL", 39: "", 40: "", 41: "RI", 42: "WV", 43: "", 44: "MO", 45: "AZ",
    46: "", 47: "AK", 48: "", 49: "VT", 50: "NY",
}

# sector_tags (a keyword rule of the connector, not a model field). The table as held on 3 October, before session
# 154's fixes ran. supported: every tag held is the document's; missing: the document's plain sector, one of the tag
# list, is not tagged; wrong: a tag held is not the document's sector.
TAGS_MISSING = {
    6: "nuclear: AGENCY: Office of Nuclear Energy ... E.O. 14302 (Reinvigorating the Nuclear Industrial Base)",
    8: "renewables: the Greenup Hydroelectric Project No. 2614",
    9: "power and gas: maintenance, replacement, and upgrades of existing electric power and natural gas systems",
    12: "gas: LREC proposes to expand existing natural gas storage caverns and create a new natural gas storage cavern",
    14: "renewables: Name of Project: Klamath Hydroelectric Project",
    17: "renewables: to surrender and decommission the Potter Valley Hydroelectric Project No. 77 (the row's power is "
        "the word Electric in the applicant's name)",
    20: "renewables: the proposed surrender of the Chignik Hydroelectric Project",
    27: "renewables: the 24-megawatt Emsworth Locks and Dam Hydroelectric Project No. 13757",
    28: "gas: approximately 119.33 miles of 20- and 24-inch-diameter natural gas pipelines, under section 7(b) of the "
        "Natural Gas Act",
    34: "renewables: the Pontook Hydroelectric Project (FERC No. 2861-056)",
    35: "nuclear: the Pioneer small modular reactor project ... about 600 megawatts of electricity",
    41: "renewables: Name of Project: Central Falls Hydroelectric Project",
    42: "renewables: the Robert C. Byrd Locks and Dam Hydroelectric Project No. 15094 ... the proposed 28.5-megawatt project",
    43: "renewables: the 37.5-megawatt (MW) Ripogenus Hydroelectric Project No. 2572 and the 67.9-MW Penobscot Mills "
        "Hydroelectric Project No. 2458",
    46: "renewables: the Kayuta Lake Hydroelectric Project No. 5000",
    47: "renewables: Name of Project: Chignik Hydroelectric Project",
    49: "renewables: the Sheldon Springs Hydroelectric Project No. 7186",
    50: "renewables: the Hollow Dam Hydroelectric Project No. 6972",
}
TAGS_WRONG = {
    21: "storage is the Associated Independent Spent Fuel Storage Installations, not the storage sector",
    24: "transmission is the applicant's name (Texas Eastern Transmission, LP); the document: to decommission and "
        "abandon in place 13.45 miles of its currently idle 24-inch-diameter lateral, under the Natural Gas Act",
    25: "storage is spent fuel storage casks (List of approved spent fuel storage casks), not the storage sector",
    30: "transmission is the applicant's name (Florida Gas Transmission Company, LLC); the document: a prior notice "
        "request under the Natural Gas Act for its SE Hialeah delivery facilities",
    31: "storage is the Three Mile Island Unit 2 independent spent fuel storage installation, not the storage sector",
    36: "transmission is the applicant's name (Florida Gas Transmission Company, LLC); the document: FGT's Madison "
        "Lateral, under the Natural Gas Act",
    37: "transmission is the applicant's name (Portland Natural Gas Transmission System); the document: certificated "
        "capacity of a gas pipeline, under the Natural Gas Act (gas, also held, is right)",
    38: "transmission is the applicant's name (Florida Gas Transmission Company, LLC); the document: delivery "
        "facilities of a gas pipeline, under the Natural Gas Act",
    40: "storage is spent fuel storage casks (List of approved spent fuel storage casks), not the storage sector",
    48: "hydrogen is hydrogen chloride (HCl), a hazardous air pollutant of plywood plants, not the hydrogen sector "
        "(emissions, also held, is right)",
}
TAGS_SILENT = {
    2: "hydrofluorocarbon leak repair in transport refrigeration: no tag of the list fits",
    4: "Regulation of Fuels, Fuel Additives, and Regulated Blendstocks: the correction names no fuel of the tag list",
    10: "a petition on contractors' diversity plans: no tag of the list fits",
    29: "the notice names the 950-kilowatt Barker Mill Upper Project and not its kind",
    39: "a notice of the membership of a personnel board: no sector",
}

# significance: a rating no document states. Each was read against warehouse/news/rubric.md.
SIGNIFICANCE_FLAGS = {
    4: "does not follow the rubric on the document: scored 4 (the rubric's 4 to 6: incremental but real, a filing, a "
       "permit) from the title alone; the document is the Office of the Federal Register's correction of an editorial "
       "error, removing duplicated paragraphs (c)(10) and (c)(20) of 40 CFR 1090.95 (the rubric's 1 to 3: minor)",
}
SIGNIFICANCE_NOTES = {
    7: "6 for the notice that a final environmental impact statement is available; the licence renewal itself is not decided here",
    23: "5 for a notice that closed meetings were held, which states no outcome",
    24: "2 on the title alone; the document states 13.45 miles of line abandoned and a cost of $39,600,000",
    28: "3 on the title alone; the document states the abandonment of an entire 119.33-mile system at $47.1 million",
}

# sector (the scorer's one sector): unsupported where the document names another sector of the scorer's list;
# contradicted where the sector held is one the document cannot mean.
SECTOR_UNSUPPORTED = {
    8: ("hydrogen", "the Greenup Hydroelectric Project No. 2614: a hydroelectric project, and no hydrogen anywhere in "
                    "the notice", "contradicted"),
    17: ("other", "the Potter Valley Hydroelectric Project No. 77: generation or renewables are in the list"),
    19: ("other", "the Moomaws Dam Hydroelectric Project No. 8005: generation or renewables are in the list"),
    27: ("other", "the 24-megawatt Emsworth Locks and Dam Hydroelectric Project No. 13757: generation or renewables are in the list"),
    32: ("other", "R.J. Fortier Hydropower, Inc., a water quality certification for its project: generation or "
                  "renewables are in the list"),
}

# why: unsupported where it states something the document does not, or describes the scorer's input, not the action.
WHY_UNSUPPORTED = {
    4: ("Fuel regulatory framework change affects refiners and blenders",
        "This rule is being published by the Office of the Federal Register to correct an editorial or technical error "
        "... remove the second instances of paragraphs (c)(10) and (c)(20): no framework changes and no refiner or "
        "blender is named (the scorer saw only the title)"),
    33: ("Routine pipeline capacity filing, minor scope",
         "to (1) replace and operate an approximately 7.5-mile segment of its existing ... Columbus branch line and (2) "
         "uprate the maximum allowable operating pressure ... to enhance the safety, security, and operational "
         "efficiency: the document speaks of no capacity"),
    42: ("An environmental assessment is a routine licensing step, with limited detail given on project size or outcome.",
         "The proposed 28.5-megawatt project ... concludes that licensing the project, with appropriate environmental "
         "protective measures, would not constitute a major federal action: the document gives the size and the "
         "outcome; the line describes the title the scorer saw"),
    45: ("Routine public engagement on largest US nuclear plant.",
         "Palo Verde, a three unit plant, is operated by the Arizona Public Service Company: the release does not say "
         "it is the largest"),
}

# The six sampled actions that have an impact read (policy_reads). field: (class, the read's words, the source's).
READS = {
    5: {"what_changes": ("supported", "", "issued an emergency order to keep a Colorado coal plant operational"),
        "affected_sectors": ("supported", "coal;power", "a Colorado coal plant ... reliable generation"),
        "affected_isos": ("supported", "SPP", "SPP is directed to take every step to employ economic dispatch of Craig Unit 1"),
        "affected_states": ("supported", "CO", "the Craig Station in Craig, Colorado"),
        "direction_supply": ("supported", "up", "to ensure that Unit 1 at the Craig Station ... is available to operate"),
        "direction_demand": ("no_direction", "none", ""),
        "direction_prices": ("unsupported", "down", "minimize costs to taxpayers ... access to affordable, reliable, and "
                             "secure electricity: the release speaks of the order's cost and of affordability, and "
                             "states no fall in prices, rates or bills"),
        "direction_buildout": ("no_direction", "none", ""),
        "timeline": ("supported", "", "in effect beginning on September 27, 2026, through December 25, 2026"),
        "plain_read": ("supported", "", "issued an emergency order to keep a Colorado coal plant operational")},
    7: {"what_changes": ("supported", "", "This final EIS evaluates the environmental impacts of the proposed subsequent license renewal"),
        "affected_sectors": ("supported", "nuclear;power", "H.B. Robinson Steam Electric Plant, Unit No. 2 ... License Renewal of Nuclear Plants"),
        "affected_isos": ("source_silent", "", ""),
        "affected_states": ("supported", "SC", "located in Darlington County, South Carolina"),
        "direction_supply": ("blank", "", ""), "direction_demand": ("blank", "", ""), "direction_prices": ("blank", "", ""),
        "direction_buildout": ("blank", "", ""),
        "timeline": ("supported", "", "is available as of March 12, 2026 ... The public comment period on the draft EIS ended on February 23, 2026"),
        "plain_read": ("blank", "", "")},
    18: {"what_changes": ("supported", "", "today selected four projects for $73 million in funding through DOE's Mine of the Future initiative"),
         "affected_sectors": ("supported", "minerals", "secure America's critical minerals supply chains"),
         "affected_isos": ("source_silent", "", ""),
         "affected_states": ("supported", "VA;WV;CO;AZ;MO;TX", "project locations: Julian, West Virginia, Idaho Springs, "
                             "Colorado, and Blacksburg, Virginia ... Sahuarita, Arizona ... Rolla, Missouri ... Navasota, Texas"),
         "direction_supply": ("supported", "up", "will help unleash America's vast mineral resources ... upgrade domestic mining capabilities"),
         "direction_demand": ("no_direction", "none", ""), "direction_prices": ("no_direction", "unclear", ""),
         "direction_buildout": ("supported", "up", "to establish domestic testing grounds for innovative mining technologies"),
         "timeline": ("supported", "", "September 9, 2026 ... selected the following projects for award negotiations"),
         "plain_read": ("supported", "", "selected four projects for $73 million in funding ... to establish domestic testing grounds")},
    21: {"what_changes": ("supported", "", "The application seeks NRC approval of the indirect transfer ... no physical changes or operational changes are being proposed"),
         "affected_sectors": ("supported", "nuclear;power", "nuclear reactors as regulated electric utilities"),
         "affected_isos": ("judgment", "PJM;ISO-NE", "the document names no grid operator; PJM and ISO-NE are the model's "
                           "inference from Virginia and Connecticut (the reader's prompt allows operators clearly "
                           "covered by the text), which the document can neither support nor contradict"),
         "affected_states": ("supported", "VA;SC;CT", "in Virginia and South Carolina, respectively ... in Connecticut"),
         "direction_supply": ("no_direction", "none", ""), "direction_demand": ("no_direction", "none", ""),
         "direction_prices": ("no_direction", "none", ""), "direction_buildout": ("no_direction", "none", ""),
         "timeline": ("supported", "", "Submit comments by September 28, 2026. A request for a hearing must be filed by September 16, 2026."),
         "plain_read": ("blank", "", "")},
    22: {"what_changes": ("supported", "", "the seventh Texas Energy Fund (TxEF) loan agreement for a 570 megawatt (MW) natural gas power plant in Sherman, Texas"),
         "affected_sectors": ("supported", "power;gas", "natural gas power plant"),
         "affected_isos": ("supported", "ERCOT", "the Electric Reliability Council of Texas (ERCOT) power region"),
         "affected_states": ("supported", "TX", "in Sherman, Texas"),
         "direction_supply": ("supported", "up", "projects that add new, dispatchable power to the ERCOT region"),
         "direction_demand": ("no_direction", "none", ""), "direction_prices": ("no_direction", "unclear", ""),
         "direction_buildout": ("supported", "up", "Rayburn Electric Cooperative will build the plant"),
         "timeline": ("supported", "", "The loan term runs from June 3, 2026, through June 3, 2046 ... generating power ... in 2028"),
         "plain_read": ("blank", "", "")},
    23: {"what_changes": ("blank", "", ""),
         "affected_sectors": ("supported", "nuclear", "entities involved in the nuclear fuel industry"),
         "affected_isos": ("source_silent", "", ""), "affected_states": ("source_silent", "", ""),
         "direction_supply": ("no_direction", "unclear", ""), "direction_demand": ("no_direction", "unclear", ""),
         "direction_prices": ("no_direction", "none", ""), "direction_buildout": ("no_direction", "unclear", ""),
         "timeline": ("blank", "", ""),
         "plain_read": ("supported", "", "a series of closed meetings were held to discuss the implementation of a "
                        "Voluntary Agreement ... Meeting 1: Reactors ... Meeting 3: Mining and Milling")},
}

# Fields where reading settles what code left open or got wrong.
OVERRIDES = {
    (1, "rin"): ("correct", "the print's heading holds RIN 2050-AH50; 2050-AH07 and 2050-AH39 are the RINs of two "
                            "earlier actions the text cites"),
    (22, "agency"): ("wrong", "Office of the Texas Governor | Greg Abbott ... Press Release: the Governor's office "
                              "issued it; the PUCT's news page lists it and the PUCT's chairman is quoted (the fault "
                              "session 154 found on its draw 11 and fixed in the connector)"),
    (35, "title"): ("correct", "the document's heading is 'NRC Kicks Off Environmental Review of Pioneer Construction "
                               "Permit Application', release No: 26-015-A; 'Media Advisory:' is the feed's prefix for an advisory"),
    (44, "docket"): ("wrong", "the print's bracket line holds four ids: Docket No. 030-37587; License No. 24-32636-01; "
                              "EAF-RIII-2024-0017; NRC-2026-1256. The row holds the first two, which are all the "
                              "Register's API record gives (the record leaves out the last two)"),
    (48, "agency"): ("correct", "ENVIRONMENTAL PROTECTION AGENCY 40 CFR Part 63: the document is a separate part of the "
                                "issue (Part V), whose cover lines the code read as the heading"),
    (48, "docket"): ("correct", "[EPA-HQ-OAR-2016-0243; FRL-5185.1-02-OAR], under the separate part's cover lines"),
}
NEWS_AGENCY_OK = {
    5: "Energy.gov September 25, 2026 ... U.S. Secretary of Energy Chris Wright today issued an emergency order",
    11: "No: IV-26-008 ... Nuclear Regulatory Commission staff will conduct an information session",
    18: "Energy.gov September 9, 2026 ... The U.S. Department of Energy's (DOE) Office of Critical Minerals and Energy Innovation",
    35: "No: 26-015-A ... The Nuclear Regulatory Commission is inviting public participation",
    45: "No: IV-26-006 ... Nuclear Regulatory Commission staff will conduct an information session",
}
