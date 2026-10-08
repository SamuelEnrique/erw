#!/usr/bin/env python3
"""Session 154: what a person read in the 50 source documents, for the fields code cannot settle.

Energy Research Warehouse (ERW). Keys are the draw numbers of runs/session154/audit/sample.csv (seed 154). Every
class here can be checked by a second person against the saved document: the source's words are quoted. The fields
audit_check.py settles by code (date, agency, type, title, abstract, docket, RIN, document number, address of a Register
row) are not repeated here, except where reading overrules the code.

Classes of an extracted field: correct, wrong, missing, not_in_source, source_silent.
Classes of a model field: supported, unsupported, contradicted, judgment, blank (the reader's own check dropped the
field, so the table holds nothing to check), no_direction (none or unclear: no claim a document can settle).
"""

# states: (class, the source's words or a note). The standard: the state where the project, plant or plan the action
# concerns is, as the document says it. A contact's address, a filing room and Washington, DC do not count.
STATES = {
    1: ("source_silent", "names Idaho only in a contact's address and in the history of a laboratory"),
    2: ("source_silent", "Rio Piedras, Puerto Rico: not a state"),
    3: ("missing", "all located in Luzerne County, Pennsylvania"),
    4: ("source_silent", ""), 5: ("source_silent", ""), 6: ("source_silent", ""),
    7: ("correct", "VA comes from the licensee's name, Virginia Electric and Power Company; the document names no state "
                   "otherwise (North Anna and Surry are in Virginia)"),
    8: ("wrong", "header and metering facilities in Jefferson County, Texas (Texas Header Project): the row's LA is the "
                 "applicant's name, Kinder Morgan Louisiana Pipeline LLC"),
    9: ("source_silent", ""), 10: ("correct", "California, the commission's state"), 11: ("correct", "Southeast Texas"),
    12: ("missing", "Station 35 located in Harris County, Texas; ... Beauregard and Allen Parishes, Louisiana"),
    13: ("wrong", "units in the State of West Virginia: the row holds VA;WV, and the document names no Virginia"),
    14: ("missing", "located in Yavapai, Coconino, Maricopa and Pinal Counties, Arizona"),
    15: ("missing", "in Spokane, Lincoln, and Stevens counties, Washington, and in Kootenai and Benewah counties, Idaho"),
    16: ("source_silent", "the notice names no state"),
    17: ("missing", "in George and Jefferson Davis Counties, Mississippi, and Richland Parish, Louisiana"),
    18: ("source_silent", ""), 19: ("missing", "natural gas pipeline located in Whatcom County, Washington"),
    20: ("correct", "New York Independent System Operator and the New York transmission owners"),
    21: ("correct", "Albuquerque, New Mexico; Livermore, California"),
    22: ("missing", "natural gas pipeline in Rowan, Fleming, and Mason Counties, Kentucky"),
    23: ("missing", "on the Sacandaga River in the town of Wells, Hamilton County, New York"),
    24: ("correct", "project in Randolph County, Arkansas ... plants in northern Texas and Arkansas"),
    25: ("missing", "NMP1 is located in Oswego County, New York."),
    26: ("source_silent", ""), 27: ("missing", "a mandatory hearing Sept. 22 in Port Lavaca, Texas"),
    28: ("missing", "in Dothan, Alabama"), 29: ("missing", "on the Blue Earth River in Blue Earth County, Minnesota"),
    30: ("missing", "the New Hampshire Department of Environmental Services (New Hampshire DES)"),
    31: ("source_silent", ""),
    32: ("missing", "in Panola, Shelby, San Augustine, Sabine, Jasper, Newton, and San Jacinto counties, Texas, and "
                    "Beauregard Parish, Louisiana"),
    33: ("source_silent", ""), 34: ("correct", "California Department of Water Resources and Los Angeles"),
    35: ("missing", "one pressurized-water reactor located in Van Buren County, Michigan"),
    36: ("missing", "on Boulder Creek, in Matanuska-Susitna Borough, Alaska"),
    37: ("source_silent", "the notice names no state"), 38: ("correct", "the Cleveland, Ohio area"),
    39: ("source_silent", ""), 40: ("correct", "Oak Ridge, Roane County, Tennessee"),
    41: ("missing", "is in Two Rivers, Wisconsin"), 42: ("source_silent", ""), 43: ("source_silent", ""),
    44: ("correct", "National Petroleum Reserve in Alaska"), 45: ("source_silent", ""),
    46: ("missing", "on the Blue Earth River, in Blue Earth County, Minnesota"),
    47: ("source_silent", "a list of amendments at plants in several states; the title and summary name none"),
    48: ("source_silent", ""), 49: ("source_silent", ""), 50: ("source_silent", ""),
}

# sector_tags (a keyword rule of the connector, not a model field, though the brief lists it with them).
# supported: every tag held is the document's; missing: the document's plain sector, one of the tag list, is not
# tagged; wrong: a tag held is not the document's sector.
TAGS_MISSING = {
    3: "gas: an application under section 7(c) of the Natural Gas Act",
    6: "nuclear: streamline licensing for new nuclear projects",
    8: "gas: a prior notice request ... under the Natural Gas Act",
    12: "gas: firm transportation capacity from the existing Transco mainline",
    14: "gas: the Phoenix Lateral's maximum allowable operating pressure, under the Natural Gas Act",
    15: "renewables: the Spokane River Hydroelectric Project No. 2545",
    17: "gas: compressor station facilities ... Certificate of Public Convenience and Necessity",
    19: "gas: the border crossing facility and natural gas pipeline",
    23: "renewables: the Lake Algonquin Hydroelectric Project No. 7274",
    27: "nuclear: application to build an advanced reactor",
    29: "renewables: the Rapidan Dam Hydroelectric Project No. 3071",
    32: "gas: the Texas Gateway Project ... Certificate of Public Convenience and Necessity",
    34: "renewables: the 1,350-megawatt South SWP Hydroelectric Project No. 2426",
    36: "renewables: the Boulder Creek Hydropower Project",
    37: "renewables: the Balch Hydroelectric Project No. 175",
    41: "nuclear: the Point Beach nuclear plant",
    46: "renewables: the Rapidan Hydroelectric Project No. 3071",
}
TAGS_WRONG = {
    22: "transmission is the applicant's name (Columbia Gulf Transmission, LLC); the document: 42 miles of new "
        "30-inch-diameter natural gas pipeline",
    31: "storage is spent fuel storage casks (List of approved spent fuel storage casks), not the storage sector",
}
TAGS_SILENT = {16: "the notice does not name the project's kind", 30: "the notice does not name the project's kind",
               45: "loan guarantees for energy projects: no tag of the list fits"}

# significance: a rating no document states. Each was read against warehouse/news/rubric.md.
SIGNIFICANCE_FLAGS = {
    32: "does not follow the rubric on the document: scored 1 from a title the Register's record cuts at the "
        "applicant's name; the document is a notice of intent to prepare an environmental impact statement for a "
        "pipeline project in seven Texas counties and one Louisiana parish (the rubric's 4 to 6: a filing, a permit)",
}
SIGNIFICANCE_NOTES = {
    7: "4 for a withdrawn licence amendment request; like notices in the sample (42, 43) score 2",
    8: "2 on the title alone; the document states a 2.5 billion cubic feet per day meter station to the Golden Pass "
       "terminal and a cost of about $39,000,000",
    11: "6 for a $200 million grant; the rubric's 7 to 8 names hundreds of millions of dollars",
}

# sector (the scorer's one sector): unsupported where the document names another sector of the scorer's list.
SECTOR_UNSUPPORTED = {
    23: ("other", "the Lake Algonquin Hydroelectric Project No. 7274: generation or renewables are in the list"),
    29: ("other", "the Rapidan Dam Hydroelectric Project No. 3071: generation or renewables are in the list"),
    36: ("other", "the Boulder Creek Hydropower Project: generation or renewables are in the list"),
}

# why: unsupported where it states something the document does not, or describes the scorer's input, not the action.
WHY_UNSUPPORTED = {
    14: ("Routine pipeline expansion filing under blanket authority.",
         "to formally update the Phoenix Lateral's recognized maximum allowable operating pressure ... does not involve "
         "any construction or additional cost"),
    17: ("Early-stage environmental scoping for a new gas pipeline project.",
         "the installation, replacement, modification, and operation of compressor station facilities"),
    32: ("Minimal detail pipeline filing notice.",
         "Notice of Intent To Prepare an Environmental Impact Statement for the Proposed Texas Gateway Project, Request "
         "for Comments on Environmental Issues, and Schedule for Environmental Review (the scorer saw only the title "
         "the Register's record holds: 'Gulf South Pipeline Company, LLC;')"),
    36: ("Duplicate procedural comment period extension notice.",
         "Docket No. DI26-3-000, the Boulder Creek Hydropower Project: its own proceeding; the notice of the same title "
         "and day (federalregister:2026-08353) is Docket No. DI26-4-000"),
}

# The nine sampled actions that have an impact read (policy_reads). field: (class, the read's words, the source's).
READS = {
    1: {"what_changes": ("blank", "", ""), "affected_sectors": ("supported", "nuclear", "advanced reactors under DOE's jurisdiction"),
        "affected_isos": ("source_silent", "", ""),
        "affected_states": ("unsupported", "ID", "the read's span is a contact's address: Idaho Operations Office, 1955 N "
                            "Freemont Avenue, Idaho Falls, ID 83415; the rule covers facilities and activities under the "
                            "responsibility of DOE's Office of Nuclear Energy, and names no state it applies to"),
        "direction_supply": ("no_direction", "unclear", ""), "direction_demand": ("no_direction", "unclear", ""),
        "direction_prices": ("no_direction", "unclear", ""),
        "direction_buildout": ("supported", "up", "expedite the review, approval, and deployment of advanced reactors"),
        "timeline": ("supported", "", "no later than February 20, 2026 ... criticality in each of the three reactors by July 4, 2026"),
        "plain_read": ("supported", "", "the removal of several sections and requirements ... expedite the review")},
    5: {"what_changes": ("supported", "", "is proposing a Clean Water Act (CWA) regulation to revise the technology-based effluent limitations"),
        "affected_sectors": ("supported", "power;coal;emissions", "steam electric power plants, particularly coal-fired power plants"),
        "affected_isos": ("source_silent", "", ""), "affected_states": ("source_silent", "", ""),
        "direction_supply": ("no_direction", "none", ""), "direction_demand": ("no_direction", "none", ""),
        "direction_prices": ("unsupported", "down", "is estimated to reduce costs by $446 to $1,090 million dollars annually at "
                             "a 3 percent discount rate: the plants' compliance costs; the text read says nothing of prices"),
        "direction_buildout": ("no_direction", "none", ""),
        "timeline": ("supported", "", "Comments must be received on or before June 17, 2026."),
        "plain_read": ("supported", "", "reduce costs by $446 to $1,090 million dollars annually")},
    6: {"what_changes": ("supported", "", "narrowing environmental reviews to impacts within the agency's statutory authority"),
        "affected_sectors": ("supported", "nuclear", "new nuclear projects"), "affected_isos": ("source_silent", "", ""),
        "affected_states": ("source_silent", "", ""), "direction_supply": ("no_direction", "unclear", ""),
        "direction_demand": ("no_direction", "none", ""), "direction_prices": ("no_direction", "none", ""),
        "direction_buildout": ("supported", "up", "expanding opportunities to streamline licensing for new nuclear projects"),
        "timeline": ("supported", "", "will accept public comments until Aug. 21"),
        "plain_read": ("supported", "", "expands the use of categorical exclusions for certain actions, including some new reactor projects")},
    11: {"what_changes": ("blank", "", ""),
         "affected_sectors": ("supported", "power;transmission", "more than 400 miles of transmission and distribution lines"),
         "affected_isos": ("source_silent", "", "served by electric utilities outside the ERCOT region: no operator is named"),
         "affected_states": ("supported", "TX", "Southeast Texas"), "direction_supply": ("no_direction", "none", ""),
         "direction_demand": ("no_direction", "none", ""),
         "direction_prices": ("supported", "none", "with zero impact to customer bills"),
         "direction_buildout": ("supported", "up", "strengthen more than 400 miles of transmission and distribution lines and upgrade more than 9,000 structures"),
         "timeline": ("supported", "", "the release states no date; we are fast-tracking critical grid upgrades"),
         "plain_read": ("supported", "", "The $200 million grant will fund two projects")},
    25: {"what_changes": ("blank", "", ""), "affected_sectors": ("supported", "nuclear;power", "Nine Mile Point Nuclear Station, Unit 1"),
         "affected_isos": ("source_silent", "", ""), "affected_states": ("supported", "NY", "NMP1 is located in Oswego County, New York."),
         "direction_supply": ("blank", "", ""), "direction_demand": ("blank", "", ""), "direction_prices": ("blank", "", ""),
         "direction_buildout": ("blank", "", ""),
         "timeline": ("supported", "", "must be filed by June 29, 2026 ... no later than 60 days from the date of publication"),
         "plain_read": ("blank", "", "")},
    40: {"what_changes": ("blank", "", ""), "affected_sectors": ("supported", "nuclear", "high-assay low enriched uranium (HALEU) fuel"),
         "affected_isos": ("source_silent", "", ""), "affected_states": ("supported", "TN", "Oak Ridge, Roane County, Tennessee"),
         "direction_supply": ("blank", "", ""), "direction_demand": ("blank", "", ""), "direction_prices": ("blank", "", ""),
         "direction_buildout": ("blank", "", ""),
         "timeline": ("supported", "", "made publicly available on February 12, 2026 ... until December 8, 2025"),
         "plain_read": ("supported", "", "a first-of-its-kind fabrication operation in the United States ... final recommendation ... is that the NRC issue the license")},
    44: {"what_changes": ("supported", "", "would establish pre-defined criteria for defined and repeatable common activities"),
         "affected_sectors": ("supported", "oil;gas;leasing", "oil and gas production sites ... oil and gas lease sales"),
         "affected_isos": ("source_silent", "", ""), "affected_states": ("supported", "AK", "National Petroleum Reserve in Alaska"),
         "direction_supply": ("supported", "up", "to expeditiously develop oil and gas resources within the NPR-A"),
         "direction_demand": ("no_direction", "none", ""), "direction_prices": ("no_direction", "unclear", ""),
         "direction_buildout": ("supported", "up", "a streamlined permitting process for qualifying production sites"),
         "timeline": ("supported", "", "on or before November 9, 2026 ... receives it by October 8, 2026"),
         "plain_read": ("supported", "", "proposing to streamline its decision-making process")},
    45: {"what_changes": ("blank", "", ""),
         "affected_sectors": ("unsupported", "power;gas;oil;nuclear;renewables;emissions",
                              "the text read names energy infrastructure and air pollutants, including anthropogenic "
                              "greenhouse gas emissions; the words nuclear, oil, renewable and power do not occur in it, "
                              "and gas only in greenhouse gas"),
         "affected_isos": ("source_silent", "", ""), "affected_states": ("source_silent", "", ""),
         "direction_supply": ("blank", "", ""), "direction_demand": ("blank", "", ""), "direction_prices": ("blank", "", ""),
         "direction_buildout": ("blank", "", ""),
         "timeline": ("supported", "", "effective October 28, 2025 ... no later than December 29, 2025"),
         "plain_read": ("supported", "", "expands the definition, criteria, and requirements of certain eligible projects")},
    49: {"what_changes": ("blank", "", ""), "affected_sectors": ("supported", "nuclear", "fusion machines under the NRC's byproduct material framework"),
         "affected_isos": ("source_silent", "", ""), "affected_states": ("source_silent", "", ""),
         "direction_supply": ("no_direction", "unclear", ""), "direction_demand": ("no_direction", "unclear", ""),
         "direction_prices": ("no_direction", "unclear", ""),
         "direction_buildout": ("supported", "up", "a deregulatory action of high interest for stakeholders ... net averted costs to the industry"),
         "timeline": ("supported", "", "Submit comments by May 27, 2026 ... at least one public meeting"),
         "plain_read": ("supported", "", "technology-inclusive to accommodate the wide variety of anticipated fusion machine designs")},
}

# Fields of the seven news rows and two Register rows where reading settles what code left open or got wrong.
OVERRIDES = {
    (2, "event_date"): ("wrong", "No: I-26-001 February 10, 2026 (the row holds 2026-02-11: the feed's stamp is Wed, 11 "
                                 "Feb 2026 02:30:00 GMT, the evening of 10 February in Washington)"),
    (10, "event_date"): ("correct", "July 09, 2026"),
    (27, "title"): ("correct", "the document's heading is 'NRC to Hold Mandatory Hearing on Proposed Long Mott Generating "
                               "Station', release No: 26-029-A; 'NRC Advisory:' is the feed's prefix for an advisory"),
    (32, "title"): ("wrong", "the printed title goes on: Notice of Intent To Prepare an Environmental Impact Statement for "
                             "the Proposed Texas Gateway Project, Request for Comments on Environmental Issues, and "
                             "Schedule for Environmental Review; the Register's API record cuts it at 'Gulf South "
                             "Pipeline Company, LLC;' and the row holds the record's title"),
    (11, "agency"): ("wrong", "Office of the Texas Governor | Greg Abbott ... Press Release: the Governor's office issued "
                              "it; the PUCT's news page lists it and the PUCT's chairman is quoted"),
}
NEWS_AGENCY_OK = {2: "No: I-26-001 ... The Nuclear Regulatory Commission has proposed", 6: "No: 26-072 ... The Nuclear Regulatory Commission has proposed",
                  10: "the California Public Utilities Commission (CPUC), on cpuc.ca.gov", 27: "No: 26-029-A ... The NRC will hold",
                  28: "No: II-26-008 ... The Nuclear Regulatory Commission will meet", 41: "No: III-26-005 ... Nuclear Regulatory Commission staff"}
