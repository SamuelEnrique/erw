#!/usr/bin/env python3
"""Build the ERW coverage table: docs/coverage.md and warehouse/metadata/coverage.csv.

Energy Research Warehouse (ERW). One row per table in warehouse/output: the
ERW equivalent of the IRW's metadata.csv (github.com/ben-domingue/irw). Every
value is read from the tables themselves (rows, provenance header) or from
erw_validate, so the files are regenerated, never edited by hand. The daily
workflow runs this after the validator.

    python warehouse/metadata/build_coverage.py

coverage.csv columns: table, iso, market, n_nodes, interval, ts_min, ts_max,
n_rows, source_report, last_run, validator_status, license, sector, derived, tier.

tier (session 28, Ben Domingue's review, item 6) is the table's provenance tier,
one of TIERS (docs/datastandard.md, "Provenance tiers"): source (every value as the
publisher published it, reshaped only), derived (computed by ERW code from other
tables with a documented method, no model) or model_extracted (at least one column
written by a model reading text: extraction, scoring or research). Set by the first
matching rule in TIER_RULES, else "derived" for a derived table, else "source"; a
table built from a model_extracted table (its "Derived from:" line) is
model_extracted too. A table whose rows name a model (a model_id column) or whose
header names a Claude model, but which no rule makes model_extracted, fails the
build: a model's output is never labelled as a source's.

derived (session 9) is "yes" for a table computed by the ERW from other ERW
tables (its header has a "Derived from:" line), else "no". A derived table's
license is the most restrictive license of its input tables (Decision 23); the
build recomputes it and fails if the table's header says otherwise.

sector (session 7) is one or more of SECTORS, ";"-separated, set per table by
the first matching rule in SECTOR_RULES. A table no rule matches fails the build:
every new table gets a sector on purpose, not by default.

Tables not on this machine (session 14): coverage describes the warehouse, and
Redivis holds every table, but a machine may hold only some of them. The CI
runner starts without the tables (they left git in session 9) and restores only
the rolling-window ones, so the ERCOT yearly history, the derived tables and, on
most days, the queues are absent there. A table that is in the previous
coverage.csv but not in warehouse/output is carried over unchanged (its CSV row
and its line in docs/coverage.md, with its own last_run), and named in a note
under the table; it is never dropped. Retiring a table is a human edit.

Absent inputs (session 18): a derived table built without some of its inputs says so in an
"Absent inputs:" header line (energy_projects, when a queue could not be pulled); each such
line is repeated in a note under the table in docs/coverage.md.

license (session 5 ruling) is "internal" if any of the table's sources is
licensed for internal use only, otherwise "public". Per-source licenses come
from warehouse/metadata/sources.csv, the source registry the connectors keep;
the rule itself is stated in docs/datastandard.md. A table whose source is not
in the registry fails the build rather than being guessed public.
"""

import glob
import itertools
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "validate"))
import erw_validate  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
DOC = os.path.join(ROOT, "docs", "coverage.md")
CSV = os.path.join(HERE, "coverage.csv")
SOURCES = os.path.join(HERE, "sources.csv")

ISO_LABEL = {"ercot": "ERCOT", "caiso": "CAISO", "nyiso": "NYISO", "miso": "MISO",
             "spp": "SPP", "isone": "ISO-NE", "pjm": "PJM"}
# EIA-930 balancing authority codes, labelled by the ISO they are
BA_LABEL = {"ciso": "CAISO", "erco": "ERCOT", "isne": "ISO-NE", "miso": "MISO", "nyis": "NYISO",
            "pjm": "PJM", "swpp": "SPP", "us48": "US48"}
# Session 29: the consolidated tables and the members they replaced (warehouse/metadata/table_migrations.csv)
MIGRATIONS = os.path.join(HERE, "table_migrations.csv")
MIGRATED = (pd.read_csv(MIGRATIONS, dtype=str, keep_default_na=False).set_index("old_table")["new_table"].to_dict()
            if os.path.exists(MIGRATIONS) else {})
CSV_COLS = ["table", "iso", "market", "n_nodes", "interval", "ts_min", "ts_max", "n_rows",
            "source_report", "last_run", "validator_status", "license", "sector", "derived", "tier"]
TIERS = ["source", "derived", "model_extracted"]
# Session 28: first match wins (docs/datastandard.md, "Provenance tiers")
TIER_RULES = [
    ("model_extracted", r"^(energy_deals|datacenter_projects|policy_reads)(_evidence)?$"),  # extraction from news
    ("model_extracted", r"^energy_companies$"),           # the Thesis Builder's research and the deal parties
    ("model_extracted", r"^news_(stories|index)$"),       # the scores and headlines are the model's
    ("model_extracted", r"^policy_actions$"),             # significance, sector and why are the model's
    ("derived", r"^(energy_projects|datacenter_queue_positions|storage_capacity)$"),  # ERW code over source tables
    # session 30: the Haiku shadow scores are a model's; the cost ledger prices Anthropic's usage counts
    ("model_extracted", r"^news_scores_shadow$"),
    ("derived", r"^api_cost_ledger$"),
    ("derived", r"^known_data_faults$"),  # session 103: the ERW's own register of its sources' faults
    ("derived", r"^grid_stress_days$"),  # session 306: ERW code over the hub prices and CAISO's notices
    ("derived", r"^eia_annual_crosscheck_ba$"),  # session 323: ERW code over EIA-923's sums and EIA-930's hours
    ("derived", r"^eia930_demand_growth$"),  # session 2298: ERW code (warehouse/derived/demand_growth.py) over EIA-930's workbooks
    ("derived", r"^interconnection_durations$"),  # session 671: ERW code over the Queued Up file (an entities table)
    ("derived", r"^interconnection_agreements_signed$"),  # session 854: the same, the requests with a signed agreement
    # session 345: NLR's JEDI workbooks' own formulas, evaluated by ERW code for each state the model lists, per MW
    ("derived", r"^nlr_jedi_multipliers$"),
    ("derived", r"^ercot_node_prices_hourly$"),  # session 358: ERCOT's saved price files reshaped by ERW code, internal by the owner's rule
    # session 138: tariff and Commission figures read by a model, each kept only with its line found on the page
    ("model_extracted", r"^texas_delivery_charges$"),
    ("model_extracted", r"^texas_transmission_matrix$"),  # session 140: the Commission's transmission charge matrices, read the same way
    # session 139: statements of large load waiting for power, collected by an AI research agent with web search, each
    # kept only with its sentence found in the document
    ("model_extracted", r"^large_load_statements$"),
    # session 154: proceedings and orders collected from public dockets by an AI research agent, each kept only with its
    # sentence found in the document; and the one-line reads a model wrote from that sentence and the text around it
    ("model_extracted", r"^large_load_rules(_internal)?$"),
    ("model_extracted", r"^large_load_rule_reads$"),
    # session 155: durations the ERW's code computes between dated copies of public queues (no model reads anything)
    ("derived", r"^large_load_waits$"),
    # session 255: the statements whose source document is public, as facts with a link (the figures are the research
    # agent's, each proved by code in large_load_statements), and the license verdict the ERW's code gives each document
    ("model_extracted", r"^large_load_public$"),
    ("derived", r"^large_load_document_verdicts$"),
]
# erw.filter(sector=...) vocabulary (session 7)
SECTORS = ["power", "gas", "oil", "products", "lng", "coal", "uranium", "carbon", "capacity",
           "metals", "equities", "news", "deals", "datacenters", "platform"]  # session 30: platform (operating costs)
# (table name pattern, sectors), first match wins
SECTOR_RULES = [
    (r"^(caiso|ercot|isone|miso|nyiso|spp)_(dam|rtm)_", "power"),
    # session 29: the consolidated price tables (the EIA-930 and trader ones match the rules below)
    (r"^iso_(dam|rtm)_hub_prices$", "power"),
    (r"^ercot_all_hub_prices_history$", "power"),
    (r"^pjm_(dam|rtm)_", "power"),
    (r"^eia930_all_emissions$", "power;carbon"),  # session 32: EIA-930 CO2 estimates
    (r"^eia930_", "power"),
    (r"^ferc714_area_demand_\d{4}$", "power"),  # session 484: FERC Form 714 hourly demand by planning area (PUDL)
    (r"^eia861_utility_sales$", "power"),  # session 485: EIA-861 retail sales, revenue and customers by utility
    (r"^utility_service_territories$", "power"),  # session 667: EIA-861 service territories, utility by county
    (r"^interconnection_agreements_(signed|by_grid)$", "power"),  # session 854: signed agreements, not yet operating (Queued Up)
    (r"^interconnection_durations(_summary)?$", "power"),  # session 671: request to operation, completed projects (Queued Up)
    (r"^grid_peak_vs_capacity$", "power;capacity"),  # session 672: each grid's peak against its generators' capacity
    (r"^egrid_power_plants$", "power;carbon"),  # session 486: EPA eGRID, every plant's generation and emissions
    (r"^nlr_atb_electricity_costs$", "power"),  # session 487: NLR (NREL) ATB, projected technology costs
    (r"^eia_aeo_electricity$", "power"),  # session 490: EIA's Annual Energy Outlook, electricity Tables 8 and 9
    (r"^eia_steo_forecasts$", "power;gas"),  # session 491: EIA's Short-Term Energy Outlook, prices and the mix
    (r"^epa_ghgrp_power_co2$", "power;carbon"),  # session 492: EPA GHGRP, power plants' reported CO2 by year
    (r"^boem_renewable_leases$", "power"),  # session 493: BOEM's offshore renewable energy leases and grants
    (r"^uswtdb_wind_turbines$", "power"),  # session 496: USGS's U.S. Wind Turbine Database
    (r"^eia_seds_state_energy$", "power;gas;oil;coal"),  # session 507: EIA's State Energy Data System
    (r"^eia923_plant_fuel_annual$", "power;gas;oil;coal"),  # session 510: Form EIA-923, each plant's generation and fuel by year
    (r"^eia861m_utility_sales_monthly$", "power"),  # session 511: Form EIA-861M, the sampled utilities' monthly sales
    (r"^eia_nuclear_outages_daily$", "power;uranium"),  # session 513: EIA's U.S. nuclear outages, a day
    (r"^ferc714_respondents$", "power"),  # session 514: FERC Form 714's respondents, from PUDL
    (r"^eia_nuclear_outages_facility_daily$", "power;uranium"),  # session 516: EIA's nuclear outages by plant, a day
    (r"^eia_gas_prices_state_monthly$", "gas"),  # session 517: EIA's natural gas prices by state, a month
    (r"^eia_gas_consumption_state_monthly$", "gas"),  # session 518: EIA's natural gas consumption by state, a month
    (r"^eia_coal_prices_annual$", "coal"),  # session 519: EIA's coal market sales price by state or region, a year
    (r"^eia_coal_production_annual$", "coal"),  # session 685: EIA's coal production by state, rank and mine type, a year
    (r"^eia_coal_mine_production_annual$", "coal"),
    (r"^eia_coal_receipts_annual$", "coal;power"),  # session 875: coal receipts at power plants, mine to plant  # session 694: EIA's coal production and employees by mine, a year
    (r"^ercot_cdr_reserve_margins$", "power"),  # session 851: ERCOT's CDR, load, capacity and reserve margin by season
    (r"^ercot_transmission_projects$", "power"),
    (r"^ercot_cdr_units$", "power"),
    (r"^eia860_plants_annual$", "power"),  # session 873: EIA-860's plants: place, BA, grid voltage, wires owner  # session 872: the CDR's unit details: code, county, zone, capacity  # session 852: ERCOT's TPIT, every transmission project
    (r"^eia861_utility_reliability$", "power"),
    (r"^eia861_delivery_only$", "power"),
    (r"^eia861_utility_data$", "power"),
    (r"^eia861_(demand_response|dynamic_pricing)$", "power"),
    (r"^eia861_(advanced_meters|net_metering)$", "power"),
    (r"^eia861_energy_efficiency$", "power"),  # session 881
    (r"^eia861_operational_data$", "power"),  # session 882
    (r"^eia861_distribution_systems$", "power"),  # session 883
    (r"^eia861_distributed_generation$", "power"),  # session 883
    (r"^eia860_generator_owners$", "power"),  # session 885
    (r"^eia860_storage_generators$", "power"),  # session 885
    (r"^eia860_solar_generators$", "power"),  # session 885
    (r"^eia860_wind_generators$", "power"),  # session 885
    (r"^eia_international_electricity_annual$", "power"),  # session 886
    (r"^cer_electricity_trade$", "power"),  # session 887
    (r"^frb_utility_output_monthly$", "power"),  # session 889
    (r"^uspvdb_solar_facilities$", "power"),  # session 890
    (r"^eia411_capacity_margins_annual$", "power"),  # session 895
    (r"^eia860_multifuel_generators$", "power"),  # session 896
    (r"^eia860_boilers$", "power"),  # session 896
    (r"^eia860_cooling_systems$", "power"),  # session 896
    (r"^eia860_emission_controls$", "power"),  # session 896
    (r"^eia923_plant_fuel_monthly$", "power"),  # session 897
    (r"^eia_gas_pipeline_projects$", "gas"),  # session 899
    (r"^eia923_fuel_receipts$", "power"),  # session 900
    (r"^ercot_node_places$", "power"),  # session 901
    (r"^eia_power_costs_annual$", "power"),  # session 903
    (r"^eia_uranium_marketing_annual$", "power;uranium"),  # session 904
    (r"^eia_world_electricity_annual$", "power"),  # session 909
    (r"^cer_gas_trade$", "gas"),  # session 910
    (r"^ornl_eha_hydropower_plants$", "power"),  # session 911
    (r"^eia_aeo_emm_regions$", "power"),  # session 913
    (r"^lbnl_ppa_prices$", "power"),  # session 915
    (r"^ornl_hydropower_pipeline$", "power"),  # session 916
    (r"^ercot_node_transmission$", "power"),  # session 917
    (r"^eia_world_oil_gas_annual$", "oil;gas"),  # session 923
    (r"^nrc_power_reactors$", "power;uranium"),  # session 925
    (r"^wb_commodity_prices_monthly$", "oil;gas;coal;metals"),  # session 926
    (r"^eia_power_fuel_stocks_monthly$", "power;coal;oil"),  # session 927
    (r"^eia_world_oil_monthly$", "oil"),  # session 929
    (r"^ornl_hydropower_relicensing$", "power"),  # session 930
    (r"^ercot_node_planned_generation$", "power"),  # session 931
    (r"^eia_world_coal_annual$", "coal"),  # session 937
    (r"^eia_world_energy_co2_annual$", "carbon"),  # session 937
    (r"^ornl_npd_potential$", "power"),  # session 938
    (r"^lbnl_solar_projects$", "power"),  # session 939
    (r"^lbnl_hybrid_ppa_prices$", "power"),  # session 940
    (r"^ornl_eha_hydropower_units$", "power"),  # session 943
    (r"^lbnl_wind_capacity_factors$", "power"),  # session 944
    (r"^ercot_node_wires_utilities$", "power"),  # session 945
    (r"^onrr_production_(monthly|annual)$", "oil;gas;coal"),  # session 951
    (r"^onrr_revenue_monthly$", "oil;gas;coal"),  # session 951
    (r"^lbnl_wind_(costs|turbine_orders)$", "power"),  # session 952
    (r"^eia_primary_energy_monthly$", "power;gas;oil;coal"),  # session 953
    (r"^usgs_mcs_critical_minerals$", "metals"),  # session 954
    (r"^blm_ca_renewable_rows$", "power"),  # session 955
    (r"^eia_coal_distribution_quarterly$", "coal"),  # session 957
    (r"^eia_uranium_(production_quarterly|facilities)$", "uranium"),  # session 958
    (r"^eia_ieo_projections$", "power;carbon"),  # session 978
    (r"^lbnl_hybrid_plants$", "power"),  # session 979 (internal: its file states no CC BY)
    (r"^usace_nid_dams$", "power"),  # session 982
    (r"^eia_(capacity_factors_(annual|monthly)|heat_rates_annual)$", "power"),  # session 984
    (r"^egrid_subregions_annual$", "power;carbon"),  # session 985
    (r"^doe_useer_employment$", "power;gas;oil;coal"),  # session 2000: energy jobs (USEER)
    (r"^nrc_(new_reactor_applications|advanced_reactor_preapplicants)$", "power;uranium"),  # session 2001
    (r"^usbr_hydropower_monthly$", "power"),  # session 2003: Reclamation's plants
    (r"^noaa_cpc_degree_days_daily$", "power;gas"),  # session 2006: CPC's degree days
    (r"^boem_offshore_platforms$", "oil;gas"),  # session 2007: BOEM's platforms
    (r"^doe_oe417_events$", "power"),  # session 2028: DOE-417's disturbance events
    (r"^eaglei_county_outages_daily$", "power"),  # session 2029: EAGLE-I's county outages, a day's peak
    (r"^epa_rfs_rins_monthly$", "products;carbon"),  # session 2030: EPA's RFS, RINs and volumes a month by D code
    (r"^epa_rfs_fuel_annual$", "products;carbon"),  # session 2030: EPA's RFS, a year by D code and fuel
    (r"^eia_biofuel_plants$", "products"),  # session 2031: EIA's biofuels plant capacity, a plant and year a row
    (r"^msha_coal_mines$", "coal"),  # session 2034: MSHA's coal mines
    (r"^msha_coal_production_quarterly$", "coal"),  # session 2034: MSHA's coal production, hours and employees a quarter
    (r"^fhwa_motor_fuel_monthly$", "products"),  # session 2035: FHWA's monthly motor fuel by state
    (r"^afdc_vehicle_registrations_annual$", "power;products"),  # session 2036: AFDC's vehicle registrations by state and fuel
    (r"^irena_capacity_annual$", "power"),  # session 2085: IRENA's installed capacity by country and technology
    (r"^irs_soi_energy_credits_annual$", "power"),  # session 2087: the IRS's residential energy credits by state
    (r"^eia_state_to_state_capacity$", "gas"),  # session 2090: EIA's state-to-state pipeline capacity
    (r"^noaa_cpc_oni_monthly$", "power;gas"),  # session 2092: NOAA CPC's Oceanic Nino Index
    (r"^wfigs_wildfires$", "power"),  # session 2134: NIFC's WFIGS wildfires of 1,000 acres or more
    (r"^gfz_kp_index_3h$", "power"),  # session 2135: GFZ Potsdam's planetary Kp, every three hours from 1932
    (r"^epa_ghg_inventory_annual$", "carbon;power;oil;gas"),  # session 2136: EPA's Inventory of U.S. Greenhouse Gas Emissions and Sinks, 1990 to 2022
    (r"^scripps_co2_mlo_monthly$", "carbon"),  # session 2137: the Scripps CO2 Program's Mauna Loa CO2, a month from 1958
    (r"^doe_lead_energy_burden$", "power;gas"),  # session 2140: DOE's LEAD Tool, households' energy burden by county and income
    (r"^afdc_station_counts_annual$", "power"),  # session 2141: AFDC's alternative fueling station counts by state, a year from 2007
    (r"^noaa_ncei_storm_events$", "power"),  # session 2042: NOAA's storm events
    (r"^nrc_event_notifications$", "power;uranium"),  # session 2043: the NRC's event reports
    (r"^doe_lng_export_applications$", "gas;lng"),  # session 2044: DOE's LNG export applications
    (r"^noaa_climdiv_state_monthly$", "power;gas"),  # session 2045: NOAA's statewide climate
    (r"^ornl_tedb_transportation_annual$", "oil;products;power"),  # session 2048: ORNL's Transportation Energy Data Book
    (r"^doe_grip_selections$", "power"),  # session 2050: DOE's GRIP selections
    (r"^aeso_alberta_load_hourly$", "power"),  # session 2071: the AESO's Alberta internal load
    (r"^eia_cbecs_commercial_buildings$", "power;gas;oil"),  # session 2017: EIA's commercial buildings survey (CBECS 2018)
    (r"^eia_ice_electricity_daily$", "power"),  # session 2014: ICE's hub indices as EIA republishes them (internal)
    (r"^eia_lng_liquefaction_projects$", "gas"),  # session 2021: EIA's U.S. liquefaction capacity (LNG export projects)
    (r"^eia_mecs_manufacturing$", "power;gas;oil;coal"),  # session 2016: EIA's manufacturing survey (MECS)
    (r"^eia_recs_households$", "power;gas;oil"),  # session 2017: EIA's residential survey (RECS 2020)
    (r"^cer_pipeline_throughput$", "oil;gas"),  # session 2169: the CER's pipeline throughput and capacity, the cross-border lines
    (r"^desnz_uk_electricity_quarterly$", "power"),  # session 2168: DESNZ's Energy Trends 5.1, UK electricity by fuel
    (r"^desnz_uk_renewables_quarterly$", "power"),  # session 2174: DESNZ's Energy Trends 6.1, UK renewable capacity and generation
    (r"^ieso_generation_fuel_hourly$", "power"),  # session 2224: the IESO's Ontario generation by fuel, an hour, from 2020
    (r"^eurostat_electricity_monthly$", "power"),  # session 2225: Eurostat's monthly electricity, net production by fuel and the flows, from 2016
    (r"^eurostat_electricity_trade_annual$", "power"),  # session 2432: Eurostat's annual electricity imports and exports by partner, European countries
    (r"^desnz_uk_gas_quarterly$", "gas"),  # session 2226: DESNZ's Energy Trends 4.1, the UK's natural gas supply and consumption
    (r"^ssb_norway_electricity_monthly$", "power"),  # session 2227: Statistics Norway's table 14091, Norway's electricity balance, a month from 1993
    (r"^smard_germany_monthly$", "power"),  # session 2230: SMARD's Germany generation by source and grid load, a month from 2015
    (r"^cbs_netherlands_electricity_monthly$", "power"),  # session 2231: CBS's table 84575NED, the Netherlands' electricity balance, a month from 1976
    (r"^scb_sweden_electricity_monthly$", "power"),  # session 2236: SCB's table TAB1011, Sweden's electricity supply by type of production, a month from 1974
    (r"^statfi_finland_electricity_monthly$", "power"),  # session 2273: Statistics Finland's table 12su, Finland's electricity supply and consumption, a month from 1992
    (r"^energy_charts_central_europe$", "power"),  # session 2272: Energy-Charts, Austria's, Switzerland's and Czechia's public net production and load, hourly
    (r"^statee_estonia_electricity_monthly$", "power"),  # session 2278: Statistics Estonia table KE21, Estonia's electricity production, imports and exports, monthly
    (r"^singstat_singapore_electricity$", "power"),  # session 2308: SingStat Table Builder M890831 and M890841, Singapore's electricity generation and consumption
    (r"^csp_latvia_electricity_monthly$", "power"),  # session 2314: CSP table ENB010m, Latvia's electricity production, imports and exports, monthly
    (r"^cso_ireland_electricity_monthly$", "power"),  # session 2320: CSO table MSM01, Ireland's gross and net electricity output, monthly
    (r"^eia_petroleum_stocks_state_monthly$", "products"),  # session 2342: EIA petroleum/stoc/st, product stocks at refineries, bulk terminals and gas plants by state, monthly
    (r"^bfe_switzerland_electricity_monthly$", "power"),  # session 2343: SFOE ENSTAT electricity balance of Switzerland, monthly
    (r"^ens_denmark_electricity_monthly$", "power"),  # session 2348: the Danish Energy Agency's monthly electricity supply statistics, Denmark and its two areas
    (r"^cence_costarica_generation_monthly$", "power"),  # session 2387: CENCE EnergiaMensualOficial, Costa Rica's official monthly generation by plant
    (r"^econtrol_austria_electricity_monthly$", "power"),  # session 2391: E-Control's monthly electricity statistics (el_dataset_mn), Austria
    (r"^ilr_luxembourg_electricity$", "power"),  # session 2392: ILR's electricity sector statistics, Luxembourg
    (r"^hagstofa_iceland_power_annual$", "power"),  # session 2397: Statistics Iceland's public power plants, capacity and generation
    (r"^eehc_egypt_electricity_annual$", "power"),  # session 2435: EEHC's annual reports, Egypt's capacity, peak load and generation by fiscal year
    (r"^statcan_generation_class_annual$", "power"),  # session 2440: Statistics Canada 25-10-0020-01, generation by class of producer
    (r"^statcan_power_disposition_annual$", "power"),  # session 2441: Statistics Canada 25-10-0021-01, annual supply and disposition of electric power
    (r"^epe_brazil_consumption_monthly$", "power"),  # session 2446: EPE's yearbook raw data, Brazil's monthly consumption by state, class and sector
    (r"^eia_gas_other_uses_state_annual$", "gas"),  # session 2164: EIA's gas vehicle, lease and plant, pipeline fuel and deliveries by state
    (r"^elexon_gb_demand_daily$", "power"),  # session 2162: Elexon's BMRS, Great Britain's daily demand outturn
    (r"^energinet_dk_production_hourly$", "power"),  # session 2217: Energinet, Denmark's production, consumption and exchanges an hour
    (r"^desnz_uk_plant_loads_annual$", "power"),  # session 2728: DESNZ's DUKES 5.10, the UK's maximum load, load factors and efficiency (OGL v3.0)
    (r"^desnz_uk_storage_annual$", "power"),  # session 2720: DESNZ's DUKES 5.16, the UK's electricity storage a year (OGL v3.0)
    (r"^desnz_uk_interconnector_flows_annual$", "power"),  # session 2715: DESNZ's DUKES 5.13, the UK's interconnector flows a year (OGL v3.0)
    (r"^desnz_uk_power_stations$", "power"),  # session 2714: DESNZ's DUKES 5.11, the major power producers' power stations in the UK (OGL v3.0)
    (r"^nspower_ns_load_hourly$", "power"),  # session 2708: NS Power's OASIS hourly total net Nova Scotia load (internal)
    (r"^desnz_gb_regional_gas_consumption_annual$", "gas"),  # session 2698: DESNZ's gas consumption and meters by GB country and region, weather corrected (OGL v3.0)
    (r"^desnz_gb_regional_consumption_annual$", "power"),  # session 2693: DESNZ's electricity consumption and meters by GB country and region (OGL v3.0)
    (r"^desnz_regional_renewable_capacity_annual$", "power"),  # session 2692: DESNZ's installed renewable capacity by UK region and technology (OGL v3.0)
    (r"^desnz_regional_renewables_annual$", "power"),  # session 2684: DESNZ's renewable generation by UK region and technology (OGL v3.0)
    (r"^bchydro_ba_load_hourly$", "power"),  # session 2679: BC Hydro's balancing authority load an hour (internal)
    (r"^desnz_uk_nations_electricity_annual$", "power"),  # session 2678: DESNZ's electricity generation and supply for each UK nation (OGL v3.0)
    (r"^asub_aland_electricity_sales_annual$", "power"),  # session 2670: ASUB's PxWeb table MI010, Aland's electricity sales by distributor and sector (CC BY 4.0)
    (r"^aedg_alaska_generation_monthly$", "power"),  # session 2665: the Alaska Energy Data Gateway's monthly generation by service area and fuel (CC BY 4.0)
    (r"^stat_kz_kazakhstan_electricity_annual$", "power"),  # session 2664: the Bureau of National Statistics of Kazakhstan's fuel and energy balance, the electricity column
    (r"^cosit_iraq_electricity_annual$", "power"),  # session 2661: COSIT's electricity projects statistics, Iraq's production, purchases, sales and losses
    (r"^stat_tj_tajikistan_electricity_annual$", "power"),  # session 2659: the Agency on Statistics of Tajikistan's electricity output, trade and consumption (CC BY 4.0)
    (r"^edf_sei_islands_electricity_annual$", "power"),  # session 2656: EDF SEI's annual production by source on the French island grids (Licence Ouverte)
    (r"^asub_aland_electricity_annual$", "power"),  # session 2651: ASUB's PxWeb table MI009, Aland's electricity supply by origin (CC BY 4.0)
    (r"^statai_anguilla_electricity_monthly$", "power"),  # session 2642: the Anguilla Statistics Department's Energy Statistics, Table 2.4.2-1, electricity generation a month (ANGLEC)
    (r"^eso_cayman_electricity_annual$", "power"),  # session 2633: ESO's Compendium of Statistics 2024, Table 20.01, Grand Cayman's electricity capacity, production and consumption by class
    (r"^asli_liechtenstein_electricity_annual$", "power"),  # session 2622: the Amt fuer Statistik Liechtenstein's Energie 2025, Tabelle 5, electricity production, trade and consumption since 1985
    (r"^nawec_gambia_electricity_monthly$", "power"),  # session 2617: NAWEC's Annual Activity Report 2022, Table 3, the Gambia's electricity a month by source
    (r"^ope_pf_electricity_annual$", "power"),  # session 2609: the Observatoire Polynesien de l'Energie's energy balance, edition 2024, French Polynesia's electricity a year
    (r"^enercal_nc_electricity_annual$", "power"),  # session 2608: Enercal's activity report 2024-2025, New Caledonia's net production by plant, public purchases by source and transmission sales
    (r"^cisos_cook_electricity_quarterly$", "power"),  # session 2603: the Cook Islands Statistics Office's Energy Statistics tables, electricity and renewable energy generated by island a quarter
    (r"^siea_solomon_electricity_annual$", "power"),  # session 2602: Solomon Power's Annual Report 2025, Energy Produced, the Solomon Islands' production by station
    (r"^je_jersey_electricity_annual$", "power"),  # session 2594: the Government of Jersey's Energy Trends 2025, the electricity column of its energy balances
    (r"^cbs_curacao_electricity_annual$", "power"),  # session 2591: CBS Curacao's Manufacturing page, Curacao's electricity production (Aqualectra)
    (r"^dbedt_hawaii_electricity_annual$", "power"),  # session 2580: DBEDT's State of Hawaii Data Book 2025, tables 17.07, 17.10 and 17.13, Hawaii's electricity by island
    (r"^sbs_samoa_electricity_annual$", "power"),  # session 2574: SBS's Electricity Statistics 2025, tables E1 and E3, Samoa's production by source and EPC's sales by category
    (r"^vmme_paraguay_electricity_annual$", "power"),  # session 2572: VMME's Balance Energetico Nacional 2024, cuadro 3, Paraguay's electricity balance
    (r"^bcrp_peru_hydrocarbons_monthly$", "oil;gas"),  # session 2567: BCRPData's Produccion minera e hidrocarburos (INEI, MINEM), Peru's crude oil, natural gas liquids and natural gas a month
    (r"^bcrp_peru_electricity_monthly$", "power"),  # session 2566: BCRPData's Produccion de electricidad por departamento (MINEM), Peru's production a month by department
    (r"^abs_suriname_electricity_annual$", "power"),  # session 2563: ABS's Milieustatistieken 2024, tables 7.1, 7.4, 7.8 and 7.9, Suriname's demand, generation and capacity (EBS, Staatsolie)
    (r"^nbs_maldives_electricity$", "power"),  # session 2562: NBS's Statistical Yearbook 2026, tables 12.2 and 12.1, the Maldives' production by island and Male's use by sector
    (r"^arse_burkina_electricity_annual$", "power"),  # session 2561: ARSE's activity report 2024, table 15, Burkina Faso's production by producer and imports
    (r"^eec_eswatini_electricity_annual$", "power"),  # session 2560: EEC's Integrated Annual Report 2025, Eswatini's energy sold, sent out, generated and imported
    (r"^gastat_saudi_electricity_annual$", "power"),  # session 2552: GASTAT's Electrical Energy Statistics 2024, Saudi Arabia's capacity, peak load, energy and sales
    (r"^derk_bih_electricity_annual$", "power"),  # session 2547: DERK's report on activities 2025, Annex C, Bosnia and Herzegovina's balance by utility
    (r"^dfe_ni_electricity_monthly$", "power"),  # session 2544: DfE's Electricity Consumption and Renewable Generation in Northern Ireland, figures 6 to 9
    (r"^nsi_bulgaria_electricity_monthly$", "power"),  # session 2539: NSI's Production and deliveries of electricity, Bulgaria a month
    (r"^eru_czech_electricity$", "power"),  # session 2538: ERU's annual report on the Czech electricity system 2025, tables 3.1 to 3.3
    (r"^inseed_togo_electricity_annual$", "power"),  # session 2535: INSEED's Annuaire Statistique National 2024, tables 25.2 and 25.7, Togo's purchases, production and sales
    (r"^arsel_cameroon_electricity_annual$", "power"),  # session 2533: ARSEL's activity report 2025, Cameroon's production, purchases and transmission flows
    (r"^instat_madagascar_electricity_monthly$", "power"),  # session 2532: INSTAT TBE 63 table 21, JIRAMA's electricity production and consumption a month
    (r"^sors_serbia_electricity_annual$", "power"),  # session 2525: SORS's Energy Balances 2024, Serbia's balance of electricity
    (r"^ask_kosovo_electricity_monthly$", "power"),  # session 2524: ASK's tab01, Kosovo's electricity production and consumption a month
    (r"^nve_norway_reservoirs_weekly$", "power"),  # session 2516: NVE's reservoir statistics, Norway's hydropower reservoirs a week
    (r"^statgl_greenland_electricity_annual$", "power"),  # session 2510: Statistics Greenland ENX3VVE and ENX4NUK, renewable electricity and Nukissiorfiit's sales
    (r"^ncsi_oman_electricity_annual$", "power"),  # session 2504: NCSI's Energy Statistics 2026, Oman's electricity by governorate and by source
    (r"^hagstova_faroe_electricity_annual$", "power"),  # session 2502: Statistics Faroe Islands UO03020 and UO03030, SEV's production by source and sales
    (r"^slu_cso_electricity_annual$", "power"),  # session 2497: CSO Saint Lucia, LUCELEC's electricity output and consumption
    (r"^grenada_cso_electricity_annual$", "power"),  # session 2496: CSO Grenada, electricity produced and consumed by category
    (r"^nso_malawi_electricity_sales_annual$", "power"),  # session 2493: NSO Malawi's Statistical Year Book 2023, table 10.1, ESCOM's units sold by type of user
    (r"^fbos_fiji_electricity_annual$", "power"),  # session 2492: FBoS table 3.7[A] and Electricity 2024 Appendix III, Energy Fiji Ltd's production and sales
    (r"^zimstat_zimbabwe_generation_monthly$", "power"),  # session 2491: ZIMSTAT's Index of Electricity Generation, Appendix A, Zimbabwe's generation a month
    (r"^ewa_bahrain_electricity_annual$", "power"),  # session 2490: EWA's Statistical Book 2024, Bahrain's electricity sent out, capacity, load and consumption
    (r"^epa_ghgrp_facility_emissions$", "carbon;power;oil;gas"),  # session 2072: EPA's GHGRP, every sector
    (r"^epa_lmop_landfill_projects$", "power;gas"),  # session 2127: EPA's LMOP, landfills and landfill gas energy projects
    (r"^epa_tri_energy_releases_annual$", "power;oil;gas;coal"),  # session 2121: EPA's Toxics Release Inventory, the energy industries
    (r"^eurostat_gas_imports_monthly$", "gas;lng"),  # session 2213: Eurostat's gas and LNG imports by partner, a month
    (r"^eurostat_renewable_capacity_annual$", "power"),  # session 2123: Eurostat's renewable and waste capacity by European country
    (r"^eurostat_oil_monthly$", "oil"),  # session 2363: Eurostat's monthly oil supply, seven products by European country
    (r"^eurostat_crude_imports_monthly$", "oil"),  # session 2369: Eurostat's monthly crude oil imports by partner, European countries
    (r"^eurostat_crude_imports_by_field_monthly$", "oil"),  # session 2427: Eurostat's monthly crude oil imports by field of production, the EU
    (r"^eurostat_solid_fuels_monthly$", "coal"),  # session 2364: Eurostat's monthly solid fuels supply by European country
    (r"^eurostat_hard_coal_imports_annual$", "coal"),  # session 2426: Eurostat's annual hard coal imports by partner, European countries
    (r"^makstat_macedonia_electricity_monthly$", "power"),  # session 2357: MakStat's electricity in MWh by months, North Macedonia
    (r"^statbank_moldova_electricity_monthly$", "power"),  # session 2358: StatBank's electricity by months, Moldova
    (r"^eurostat_electricity_capacity_annual$", "power"),  # session 2356: Eurostat's electricity capacity by fuel group and operator by European country
    (r"^fema_disaster_declarations$", "power;gas;oil"),  # session 2056: FEMA's disaster declarations (OpenFEMA)
    (r"^ieso_ontario_demand_hourly$", "power"),  # session 2070: the IESO's Ontario demand
    (r"^lbnl_tracking_the_sun$", "power"),  # session 2015: Berkeley Lab's Tracking the Sun, summarised (written in session 2020)
    (r"^nhc_hurdat2_track_points$", "power;oil;gas"),  # session 2059: NHC's HURDAT2 best tracks
    (r"^noaa_ncei_billion_disasters$", "power"),  # session 2073: NOAA's billion-dollar disasters
    (r"^nrc_license_actions$", "power;uranium"),  # session 2064: the NRC's renewed licenses and power uprates
    (r"^owid_ember_electricity_annual$", "power;carbon"),  # session 2126: Ember's electricity demand and emissions through Our World in Data
    (r"^cea_india_psp_annual$", "power"),  # session 2295: CEA's energy power supply position, India, a fiscal year by state and region
    (r"^kpx_korea_generation_annual$", "power"),  # session 2297: KPX's EPSIS, South Korea's generation by source a year
    (r"^kpx_korea_demand_monthly$", "power"),  # session 2297: KPX's EPSIS, South Korea's mean daily peak and base demand a month
    (r"^statnett_norway_daily$", "power"),  # session 2350: Statnett's operational data, Norway's production and consumption a day
    (r"^svk_sweden_production_hourly$", "power"),  # session 2351: Svenska kraftnat's Mimer, Sweden's production an hour by type, 2020 to 18 March 2025
    (r"^eia_shale_gas_reserves_annual$", "gas"),  # session 2250: EIA's shale gas proved reserves and their changes, 2007 to 2021
    (r"^eia_gas_heat_content_monthly$", "gas"),  # session 2245: EIA's heat content of gas delivered to consumers by state, a month
    (r"^eia_crude_quality_monthly$", "oil"),  # session 2244: EIA's crude oil input qualities (API gravity, sulfur), a month
    (r"^ons_brazil_balance_hourly$", "power"),  # session 2240: ONS's open data, Brazil's balance an hour by subsystem
    (r"^ree_spain_balance_monthly$", "power"),  # session 2239: REE's REData, Spain's electrical energy balance a month
    (r"^dosm_malaysia_electricity_monthly$", "power"),  # session 2322: DOSM (data.gov.my), Malaysia's electricity supply and consumption a month by sector
    (r"^censtatd_hk_electricity$", "power"),  # session 2323: C&SD's Hong Kong Energy Statistics, electricity consumption by user a month, generation and trade a quarter
    (r"^aneel_siga_plants$", "power"),  # session 2324: ANEEL's SIGA, Brazil's generation plants (central generation; operating, under construction, planned)
    (r"^epra_kenya_electricity_annual$", "power"),  # session 2325: EPRA's statistics reports, Kenya's capacity by technology and consumption by customer category, a fiscal year
    (r"^statcan_electricity_trade_monthly$", "power"),  # session 2328: Statistics Canada 25-10-0016-01, electricity receipts, deliveries and availability by province, a month (the U.S. trade among them)
    (r"^eurostat_gas_balance_monthly$", "gas"),  # session 2329: Eurostat's supply, transformation and consumption of natural gas, a month (nrg_cb_gasm)
    (r"^eia_refinery_utilization_monthly$", "oil;products"),  # session 2334: EIA's refinery utilization and capacity by PADD and refining district, a month (petroleum/pnp/unc)
    (r"^ceb_srilanka_electricity_annual$", "power"),  # session 2371: CEB's Statistical Digest, Sri Lanka's stations, capacity, generation and maximum demand (internal)
    (r"^erb_zambia_electricity_annual$", "power"),  # session 2420: ERB's Statistical Bulletin 2025, Zambia's generation by station, consumption, trade and capacity
    (r"^statsbots_botswana_electricity_monthly$", "power"),  # session 2421: Statistics Botswana's electricity stats brief, generation, imports and distribution a month
    (r"^erc_mongolia_electricity_annual$", "power"),  # session 2422: ERC Mongolia's Statistics on Energy Performance 2020, generation, imports, capacity and sales by grid
    (r"^esco_georgia_electricity_monthly$", "power"),  # session 2423: ESCO's actual electricity balance of Georgia a month (in place of Cambodia)
    (r"^energycom_ghana_electricity_annual$", "power"),  # session 2373: Ghana's Energy Commission bulletin, generation by source, imports and exports, peak load, a year (internal)
    (r"^eia_gas_for_others_annual$", "gas"),  # session 2377: EIA's natural gas delivered for the account of others by state and sector, a year (natural-gas/cons/acct)
    (r"^statcan_petroleum_products_monthly$", "oil;products"),  # session 2378: Statistics Canada 25-10-0081-01, petroleum products by supply and disposition, a month
    (r"^statcan_energy_balance_annual$", "power;gas;oil;coal"),  # session 2383: Statistics Canada 25-10-0029-01, supply and demand of primary and secondary energy, a year
    (r"^sne_panama_electricity_annual$", "power"),  # session 2407: Panama's Secretaria Nacional de Energia, gross generation by plant type, net production, maximum demand and load factor, a year (internal)
    (r"^sne_panama_generation_monthly$", "power"),  # session 2407: Panama's Secretaria Nacional de Energia, total gross generation a month (internal)
    (r"^amm_guatemala_generation_monthly$", "power"),  # session 2408: Guatemala's AMM, generation by fuel, imports, exports and the SNI's demand, a month (internal)
    (r"^statsmu_mauritius_electricity_annual$", "power"),  # session 2409: Statistics Mauritius, Energy and Water Statistics, generation by source, capacity, peak demand and sales, a year (internal)
    (r"^eia_net_imports_monthly$", "oil;products"),  # session 2412: EIA's U.S. net imports of crude oil and petroleum products by country, a month (petroleum/move/neti)
    (r"^eurostat_electricity_production_annual$", "power"),  # session 2413: Eurostat's gross electricity production by fuel, all producers, a year (nrg_bal_peh, GEP)
    (r"^statcan_generating_capacity_annual$", "power"),  # session 2418: Statistics Canada 25-10-0022-01, installed generating capacity by type and class of producer, by province, a year
    (r"^eia_lng_storage_annual$", "gas;lng"),  # session 2292: EIA's LNG peak-shaving storage additions and withdrawals by state
    (r"^eia_gas_plant_processing_annual$", "gas;products"),  # session 2287: EIA's gas plant processing (gas processed, liquids extracted), a year
    (r"^eia_crude_tank_farm_stocks_monthly$", "oil"),  # session 2286: EIA's crude stocks at tank farms and pipelines, Cushing among them
    (r"^eia_gas_storage_type_monthly$", "gas"),  # session 2283: EIA's underground gas storage by type (salt, non-salt), a month
    (r"^energy_charts_portugal_power$", "power"),  # session 2282: Energy-Charts, Portugal's production by type and load
    (r"^energy_charts_italy_power$", "power"),  # session 2281: Energy-Charts, Italy's production by type and load
    (r"^ren_portugal_balance_annual$", "power"),  # session 2280: REN's Data Hub, Portugal's electricity balance a year (internal)
    (r"^rte_eco2mix_france_halfhourly$", "power"),  # session 2238: RTE's eco2mix, France every half hour
    (r"^pse_poland_balance_15min$", "power"),  # session 2252: PSE's power balance of Poland, a quarter hour
    (r"^energy_charts_belgium_hourly$", "power"),  # session 2253: Energy-Charts' Belgian public net production by type and load, an hour
    (r"^usbr_crsp_reservoirs_daily$", "power"),  # session 2221: Reclamation's CRSP power reservoirs above Lake Powell, a day
    (r"^usbr_mead_powell_daily$", "power"),  # session 2211: Reclamation's Lake Mead and Lake Powell, a day
    (r"^usdm_drought_state_weekly$", "power"),  # session 2058: the U.S. Drought Monitor by state
    (r"^blm_oil_gas_statistics_annual$", "oil;gas"),  # session 2106: BLM's federal onshore leases, permits and wells by state and fiscal year
    (r"^cec_total_system_generation_annual$", "power"),  # session 2109: the Energy Commission's in-state generation, imports and total system power
    (r"^eia_seds_residential_annual$", "power;gas;oil"),  # session 2108: SEDS's residential expenditures by source and state
    (r"^noaa_uscrn_solar_monthly$", "power"),  # session 2107: NOAA USCRN's monthly solar radiation near CAISO's and ERCOT's solar
    (r"^treasury_1603_awards$", "power;deals"),  # session 2112: the Treasury's Section 1603 awards
    (r"^usaspending_doe_obligations$", "power;deals"),  # session 2188: USAspending.gov, DOE's budget, obligations and award obligations by category, a fiscal year
    (r"^usgs_comcat_earthquakes_south_central$", "oil;gas"),  # session 2120: the USGS earthquake catalog, OK, KS, TX and NM
    (r"^usgs_streamflow_daily$", "power"),  # session 2113: the USGS's daily mean discharge below large hydropower plants
    (r"^bpa_ba_hourly$", "power"),  # session 2148: BPA's balancing authority load and generation, five-minute values to the hour
    (r"^nrcs_snotel_swe_daily$", "power"),  # session 2149: NRCS SNOTEL's daily snow water equivalent above the West's reservoirs
    (r"^wb_electricity_access_annual$", "power"),  # session 2150: the World Bank's access to electricity by country
    (r"^census_bps_state_annual$", "power"),  # session 2154: the Census Bureau's building permits by state, a year
    (r"^afdc_ev_charging_state_annual$", "power"),  # session 2155: AFDC's EV charging stations and ports by state, each December
    (r"^census_cbp_hosting_annual$", "power;datacenters"),  # session 2160: CBP's data processing and hosting (NAICS 518210) by state
    (r"^statcan_electricity_generation_monthly$", "power"),  # session 2176: Statistics Canada's monthly generation by province, class and type
    (r"^emi_nz_generation_demand_monthly$", "power"),  # session 2254: EMI's New Zealand grid generation and demand, nationally and by island, a month
    (r"^census_c30_construction_monthly$", "power;datacenters"),  # session 2258: the Census Bureau's construction spending by type and owner, a month (data centers, power)
    (r"^energy_charts_southeast_europe_daily$", "power"),  # session 2259: Energy-Charts' Hungary, Romania, Greece and Bulgaria, production by type and load, a day
    (r"^census_qss_utilities_hosting_quarterly$", "power;gas;datacenters"),  # session 2264: the Census Bureau's QSS benchmark, utilities' and hosting's revenue, a quarter
    (r"^statcan_oil_gas_supply_monthly$", "oil;gas"),  # session 2179: Statistics Canada's crude oil and natural gas supply and disposition, by province, a month
    (r"^ntd_transit_energy_annual$", "power;products"),  # session 2182: the FTA's National Transit Database fuel and energy, an agency, mode and year
    (r"^epa_needs_units$", "power"),  # session 2183: EPA's NEEDS for the 2025 reference case, one row a generating unit
    (r"^bsee_offshore_incidents$", "oil;gas"),  # session 2177: BSEE's offshore incidents, one row an incident
    (r"^nrc_rop_findings$", "power;uranium"),  # session 2178: the NRC's ROP findings and violations, one row a finding
    (r"^wb_iea_electricity_annual$", "power"),  # session 2150: the IEA's electricity per person and renewable share, via the World Bank
    (r"^eia861_short_form$", "power"),  # session 876: EIA-861S, the small utilities' sales  # session 869: EIA-861's meters and net metering by utility  # session 868: EIA-861's programs by utility  # session 867: EIA-861's utility data: NERC region, RTOs, activities  # session 853: EIA-861's delivery-only companies (Texas's wires utilities)  # session 695: EIA-861's distribution reliability (SAIDI, SAIFI, CAIDI) by utility
    (r"^eia_gas_storage_state_monthly$", "gas"),  # session 525: EIA's natural gas in underground storage by state, a month
    (r"^eia_state_capacity_annual$", "power"),  # session 526: EIA's state electricity profiles, net summer capacity
    (r"^eia_crude_production_state_monthly$", "oil"),  # session 527: EIA's crude oil field production by state, a month
    (r"^eia_gas_production_state_monthly$", "gas"),  # session 528: EIA's natural gas production by state, a month
    (r"^eia_co2_state_annual$", "power;gas;oil;coal;carbon"),  # session 530: EIA's energy-related CO2 by state, sector and fuel
    (r"^eia_refinery_weekly$", "oil;products"),  # session 543: EIA's weekly refinery inputs and utilization
    (r"^eia_state_source_disposition_annual$", "power"),  # session 544: EIA's state electricity supply and disposition
    (r"^eia_net_metering_state_annual$", "power"),  # session 545: EIA's net-metered capacity and customers by state
    (r"^eia_nuclear_outages_generator_daily$", "power;uranium"),  # session 548: EIA's nuclear outages by reactor, a day
    (r"^eia_gas_interstate_annual$", "gas"),  # session 550: EIA's interstate and international gas movements by state
    (r"^eia_crude_reserves_annual$", "oil"),  # session 551: EIA's crude oil proved reserves by state
    (r"^eia_gas_reserves_annual$", "gas"),  # session 552: EIA's dry natural gas proved reserves by state
    (r"^eia_coal_delivered_price_annual$", "coal"),  # session 553: EIA's delivered coal price by state and sector
    (r"^eia_petroleum_snd_monthly$", "oil;products"),  # session 555: EIA's petroleum supply and disposition, a month
    (r"^eia_product_supplied_monthly$", "oil;products"),  # session 556: EIA's petroleum products supplied, a month
    (r"^eia_wood_pellets_monthly$", "power"),  # session 558: EIA's densified biomass (wood pellets), a month
    (r"^eia_petroleum_stocks_monthly$", "oil;products"),  # session 559: EIA's petroleum product stocks, a month
    (r"^eia_gas_balance_annual$", "gas"),  # session 557: EIA's natural gas supply and disposition by state, a year
    (r"^eia_energy_efficiency_state_annual$", "power"),  # session 560: EIA's energy efficiency programs by state, a year
    (r"^eia_meters_state_annual$", "power"),  # session 570: EIA's meters by state, technology and sector, a year
    (r"^eia_power_co2_state_annual$", "power;carbon"),  # session 571: EIA's power plants' CO2 by state and fuel, a year
    (r"^eia_coal_price_rank_annual$", "coal"),  # session 572: EIA's coal sales price by state or region and rank, a year
    (r"^eia_coal_trade_price_annual$", "coal"),  # session 573: EIA's price of coal exports and imports, a year
    (r"^eia_drilling_monthly$", "oil;gas"),  # session 603: EIA's drilling activity, a month
    (r"^eia_gas_wells_annual$", "gas"),  # session 604: EIA's producing natural gas wells by state, a year
    (r"^eia930_subba_demand_hourly$", "power"),  # session 602: EIA-930's demand by sub-region, hourly
    (r"^eia930_subba_demand_hourly_\d{4}$", "power"),  # session 612: the same, a whole year a table
    (r"^eia_heating_fuel_prices_weekly$", "products"),  # session 605: EIA's weekly heating oil and propane prices
    (r"^boem_ogor_lease_production_monthly$", "oil;gas"),  # session 611: BOEM's offshore production by lease, a month
    (r"^eia_refinery_capacity_annual$", "products"),  # session 614: EIA's refinery capacity, a year
    (r"^eia_refinery_inputs_monthly$", "products"),  # session 615: EIA's refinery and blender net input, a month
    (r"^eia_refinery_production_monthly$", "products"),  # session 618: EIA's refinery and blender net production, a month
    (r"^eia_padd_rail_barge_movements_monthly$", "oil;products"),  # session 622: EIA's movements between PADDs by rail, tanker and barge
    (r"^eia_gas_trade_country_monthly$", "gas"),  # session 625: EIA's natural gas exports and imports by country, a month
    (r"^eia_gas_storage_capacity_monthly$", "gas"),  # session 626: EIA's underground natural gas storage capacity, a month
    (r"^eia_ngl_production_monthly$", "products"),  # session 629: EIA's natural gas plant field production of NGLs, a month
    (r"^eia_oxygenate_production_monthly$", "products"),  # session 631: EIA's oxygenate plant production, a month
    (r"^eia_petroleum_exports_by_destination$", "oil;products"),
    (r"^eia_gas_consumers_state_annual$", "gas"),  # session 861: EIA's number of natural gas consumers by state and sector  # session 860: EIA's crude and product exports by destination
    (r"^eia_crude_imports_detail_monthly$", "oil"),  # session 636: EIA's crude oil imports by origin, destination and grade
    (r"^pjm_rpm_capacity_prices$", "capacity"),
    # session 65: capacity prices of the four markets that pay capacity apart, and the day-ahead ancillary services
    (r"^iso_all_capacity_prices$", "capacity"),
    (r"^(ercot|caiso|nyiso|isone|miso|spp)_as_prices$", "power"),  # session 85: four more grids
    (r"^ercot_as_quantities$", "power"),  # session 74: the DAM Ancillary Service Plan
    (r"^ferc_eqr_contracts$", "power"),  # session 83: FERC Electric Quarterly Report contracts (internal)
    (r"^eia_fuel_spot_prices$", "oil;gas"),
    (r"^eia_(product_spot|retail_fuel)_prices$", "products"),
    (r"^eia_petroleum_(trade|stocks)_weekly$", "oil;products"),
    (r"^eia_lng_exports_monthly$", "lng"),
    (r"^(carb|rggi)_auction_allowance_prices$", "carbon"),
    # session 207: the FRED tables are retired (warehouse/metadata/retired_tables.csv); their rules are gone with them
    # session 132: the price board's added series
    (r"^eia_regional_retail_fuel_prices$", "products"),   # weekly retail gasoline and diesel by region, state and city
    (r"^eia_crude_stream_prices$", "oil"),                 # monthly crude prices by stream and area
    (r"^eia_power_plant_fuel_costs$", "coal;gas;power"),   # monthly cost of coal and gas delivered to power plants (EIA-923)
    (r"^frb_treasury_yields$", "equities"),                # US Treasury yields at 2, 10 and 30 years (session 207: from the Board's own H.15 download, was fred_treasury_yields): the vocabulary has no sector for interest rates, and financial markets is the nearest
    (r"^imf_commodity_prices$", "uranium;metals"),         # IMF monthly prices: uranium, lithium, cobalt, nickel, copper
    (r"^carb_lcfs_credit_prices$", "carbon"),              # California's Low Carbon Fuel Standard credit price, weekly
    # session 134: supply and trade
    (r"^eia_gas_storage_weekly$", "gas"),                 # weekly working gas in storage, the Lower 48 and its regions
    (r"^eia_petroleum_supply_weekly$", "oil;products"),   # weekly stocks, crude production, refinery utilization and inputs, trade
    (r"^eia_gas_trade_monthly$", "gas;lng"),              # monthly pipeline flows with Mexico and Canada, LNG exports by terminal
    (r"^eia_basin_production_monthly$", "oil;gas"),       # monthly crude and gas production by region (the Outlook's history)
    (r"^cftc_cot_positions$", "oil;gas;products"),        # managed money positions in four energy futures, weekly
    # session 136: day-ahead energy cleared, by operator
    (r"^(ercot|caiso|nyiso|isone|spp)_dam_cleared_energy$", "power"),
    # session 138: hourly load by zone or area, from the operators
    (r"^(ercot_zone|nyiso_zone|isone_zone|caiso_area)_load_hourly$", "power"),
    # session 138: Texas wires utilities' delivery charges for a load at transmission voltage (internal)
    (r"^texas_delivery_charges$", "power"),
    # session 140: the Commission's transmission charge matrices (internal); the load zone and zone price histories
    (r"^texas_transmission_matrix$", "power"),
    (r"^(ercot_zone_prices_history|iso_zone_prices_history|isone_zone_prices_history)$", "power"),
    # session 144: ERCOT's hourly wind and solar output with the high sustained limit, and the monthly estimate from it
    (r"^ercot_wind_solar_(hsl_hourly|hsl_monthly|output_hourly)$", "power"),
    # session 149: ISO-NE's monthly delivered and undelivered energy of its dispatchable wind and solar plants (internal)
    (r"^isone_ddg_undelivered_monthly$", "power"),
    # session 139: the large-load statements pilot (internal)
    (r"^large_load_statements$", "power"),
    (r"^large_load_rule(s|s_internal|_reads)$", "power;datacenters"),  # session 154: rules in motion for large loads
    (r"^large_load_waits$", "power;datacenters"),  # session 155: measured waits of large loads, from dated copies of queues (internal)
    (r"^large_load_(public|document_verdicts)$", "power;datacenters"),  # session 255: the statements whose document is public, and each document's license verdict (internal until ruled)
    (r"^policy_action_tags$", "news"),  # session 154: tags of the policy actions held, by a written rule
    (r"^news_", "news"),
    # session 8
    (r"^eia860m_(operating|planned|retired)_generators$", "power"),
    (r"^[a-z]+_interconnection_queue$", "power"),
    (r"^eia_retail_electricity_prices$", "power"),
    (r"^eia_crude_(first_purchase_prices|imports_by_country)$", "oil"),
    (r"^eia_padd_crude_pipeline_flows$", "oil"),
    (r"^portwatch_chokepoint_transits$", "oil;lng"),
    # session 9, derived
    (r"^ercot_peak_premium_(annual|monthly)$", "power"),
    # session 15: the deal tracker (tool 6)
    (r"^energy_deals(_evidence)?$", "deals"),
    # session 16: the project map (tool 3) and the datacenter power tracker (tool 4)
    (r"^energy_projects$", "power"),
    (r"^datacenter_projects(_evidence)?$", "power;datacenters"),
    # session 22: the tracker's combined table and its operator and queue inputs
    (r"^datacenter_(facilities|operator_sites|queue_positions)$", "power;datacenters"),
    # session 17: written only if ERCOT publishes a request-level list (warehouse/connectors/ercot_large_load.py)
    (r"^ercot_large_load_queue$", "power;datacenters"),
    (r"^ercot_large_load_status$", "power;datacenters"),  # session 106: the figures ERCOT's monthly status update states in words
    (r"^nyiso_load_queue$", "power;datacenters"),  # session 140: NYISO's load interconnection requests, by zone
    # session 18: the energy mix explorer (21), the curtailment tracker (22), consumption by sector (23)
    (r"^(eia_state_generation_monthly|state_generation_mix_monthly)$", "power"),
    (r"^((caiso|spp)_curtailment_daily|ercot_wind_solar_hsl_daily|iso_curtailment_monthly)$", "power"),
    # session 23: CAISO battery output (Today's Outlook), for the Automated Analysis storage template
    (r"^caiso_battery_storage$", "power"),
    (r"^caiso_fuel_supply$", "power"),  # session 73: CAISO's own supply by fuel source, hourly
    # session 133: the energy mix's added pulls
    (r"^caiso_fuel_supply_history$", "power"),            # CAISO's own supply by fuel, June 2018 to May 2025 (the hydro gap's months are read here)
    (r"^eia860m_retired_generators_all$", "power"),       # every retired generator EIA lists (installed capacity by fuel, month by month)
    (r"^nrc_reactor_status$", "power;uranium"),           # the NRC's daily power level of each reactor
    (r"^(caiso|ercot)_wind_solar_forecast$", "power"),    # wind and solar, forecast a day ahead and actual, hourly
    (r"^caiso_grid_emergencies$", "power"),  # session 58: CAISO's Flex Alerts and emergencies
    (r"^ercot_grid_notices$", "power"),
    (r"^eia_annual_(generation|crosscheck)_ba$", "power"),  # session 323: EIA-923's annual generation by BA, and EIA-930 against it  # session 322: ERCOT's EEAs, conservation appeals, watches and control-room notices
    (r"^caiso_reliability_daily$", "power"),  # session 58: how tight was it (derived)
    (r"^flex_alert_(effects|model)$", "power"),  # session 60: the Flex Alert scorecard (derived)
    (r"^caiso_dam_alert_day_hub_prices$", "power"),  # session 60: day-ahead hub prices on alert days
    (r"^ai_power_regions$", "power;carbon"),  # session 62: where the next gigawatts for AI can come from (derived)
    # session 24: the policy monitor (tool 12)
    (r"^policy_(actions|reads)(_evidence)?$", "news"),
    # session 24: NWS weather at the ISO load centers, the /grid overlay
    (r"^weather_(obs|forecast)_hourly$", "power"),
    # session 25: companies found by the Thesis Builder (tool 27), the seed of the company database (tool 10)
    (r"^energy_companies$", "deals"),
    (r"^eia_retail_sales_monthly$", "power"),
    (r"^eia_sector_energy_consumption_monthly$", "power;gas;oil;coal"),
    # session 19: the trader view (24)
    (r"^([a-z]+_trader_daily|iso_rt_top_intervals)$", "power"),
    # session 30: price board v2 (derived), the Haiku shadow scores and the API cost ledger (internal)
    (r"^price_board_(latest|peak_offpeak)$", "power"),
    (r"^price_board_spreads$", "power;gas;oil"),
    (r"^price_board_stats$", "power;gas;oil;products"),  # session 127: the board, version 4 (latest, moves and one-year range of every price held, and the spreads)
    (r"^eia_all_futures_prices$", "oil;gas;products"),   # session 127: EIA's NYMEX futures, 2019 to 5 April 2024
    (r"^price_board_carbon$", "carbon"),
    (r"^news_scores_shadow$", "news"),
    (r"^api_cost_ledger$", "platform"),
    # session 31: battery storage (EIA-930 BAT, its daily cycle, the EIA-860M battery units)
    (r"^storage_(daily_cycle|capacity|buildout_monthly|owners_monthly)$", "power"),  # session 72: the build-out (session 69); session 87: the owners
    (r"^shoulder_hours_monthly$", "power"),  # session 75: the shoulder hours
    # session 32: carbon intensity per BA (derived from the EIA-930 CO2 estimates)
    (r"^carbon_intensity_(hourly|daily|monthly)$", "power;carbon"),  # session 34: monthly
    # session 36B: the Historical Event Analyzer's event windows (prices, demand, generation, intensity)
    (r"^event_window_daily$", "power;carbon"),
    (r"^event_study_estimates$", "power"),  # session 47: the event studies of event_window_daily
    # session 37: the cost-of-power model (market-based wholesale cost per ISO hub; carbon beside price)
    (r"^cost_of_power_(monthly|hourly_profile)$", "power"),
    (r"^cost_of_power_carbon$", "power;carbon"),
    (r"^merchant_revenue_monthly$", "power;gas"),  # session 51: the seller's side (solar, wind, batteries, peaker)
    (r"^battery_stack_(monthly|stress_daily|review_monthly)$", "power"),  # session 67: the battery revenue stack (energy and ancillary); session 86: the grids in review
    (r"^(battery_sourced_ranges|grid_stress_days)$", "power"),  # session 306: the battery's published cost cases; the grids' stress days by one rule
    (r"^nlr_jedi_multipliers$", "power"),  # session 345: JEDI's jobs, earnings and output per MW of a power plant, by state
    (r"^impact_tax_rules$", "power;oil;gas"),  # session 346: the severance rules of TX, LA and NM, and the property tax of a plant (none held)
    (r"^iso_queue_statistics$", "power"),  # session 348: the six queues' entries, withdrawals, completions and waits by entry year
    # session 49: interchange and the grid network; a year of hub prices; the 2018 EIA-930 baseline; station weather
    (r"^(eia930_all_interchange|grid_network_(nodes|links))$", "power"),
    # session 68: EIA's daily total interchange of every BA, the two stories' hourly flows, who supplies a grid
    (r"^(eia930_daily_total_interchange|eia930_event_hourly_interchange|ba_supply_monthly)$", "power"),
    (r"^eia930_daily_demand$", "power"),  # session 109: EIA's daily demand of every balancing authority (the replay's share of demand)
    (r"^iso_hub_prices_history$", "power"),
    (r"^eia930_all_history$", "power"),
    (r"^noaa_isd_hourly$", "power"),
    (r"^noaa_grid_weather_(stations|hourly|daily)$", "power"),  # session 126: each grid's weighted weather, and its stations
    (r"^noaa_station_weather_hourly$", "power"),                # session 129: the stations' own measured hours
    (r"^census_metro_population$", "power"),                    # session 129: the Census Bureau's metropolitan populations, the stations' weights
    (r"^rrc_lease_production_monthly$", "oil;gas"),
    # session 102: the tables of sessions 94 to 100, which could not be put in coverage during the freeze
    (r"^generation_mix_(hourly_profile|records)$", "power;carbon"),  # session 94: the energy mix by hour and its records
    (r"^interconnection_queue_summary$", "power"),  # session 95: the queue by grid and technology
    (r"^hub_price_comparison$", "power;carbon"),  # session 96: where power is cheap (price, spread and carbon intensity)
    (r"^caiso_curtailment_(intervals|profile)$", "power"),  # session 98: CAISO curtailment by interval, and its profile
    (r"^ferc_eqr_(buyer_names|buyer_doubtful|party_totals)$", "power"),  # session 99: who is buying (internal)
    (r"^ferc_eqr_(contracts_history|contract_terms|party_mw|quarter_changes)$", "power"),  # session 125: earlier quarters and the terms read from them (internal)
    (r"^spp_as_quantities$", "power"),  # session 100: SPP reserve MW cleared day-ahead
    (r"^known_data_faults$", "platform"),  # session 103: known faults in source data (every sector's sources)
    (r"^ercot_hub_prices_daily$", "power"),  # session 114: ERCOT hub prices by day (derived), for Ask ERCOT
    (r"^ercot_storage_dam_awards_monthly$", "power"),  # session 115: storage resources' day-ahead awards by month (derived)
    (r"^ercot_storage_dam_offers_(daily|monthly)$", "power"),  # session 116: their day-ahead offers, by day and by month (derived)
    (r"^(ercot_sced_esr_hourly|ercot_rtm_node_prices)$", "power"),  # session 120: storage resources in real time by hour; node prices for the week ERCOT lists
    (r"^ercot_storage_(rt_monthly|node_basis)$", "power"),  # session 120: the fleet in real time beside its day-ahead awards, and its nodes against the hub (derived)
    (r"^grid_stress_yearly$", "power"),  # session 123: evening ramp, lowest net load, fuels in the tightest hours, dark and calm stretches, by grid and year (derived)
    (r"^clean_energy_(hourly|summary)$", "power;carbon"),  # session 122: the carbon-free share of each grid's generation by hour, month and year (derived)
    (r"^ercot_as_prices_(daily|monthly)$", "power"),  # session 148: ERCOT reserve prices by day and by month (derived), for Ask ERCOT
    (r"^ercot_rtm_price_adders$", "power"),  # session 244: ERCOT's real-time reserve price adders by hour (the ORDC's scarcity signal), from June 2014
    (r"^scarcity_hours_by_grid$", "power"),  # session 254: each grid's own scarcity signal beside the USD 1,000 price count, by hour, 36 months (derived)
    (r"^price_years_by_window$", "power"),  # session 357: each economics page's figure under every window of years held (derived)
    (r"^(node_basis_(daily|summary)|ercot_node_prices_hourly)$", "power"),  # session 358: ERCOT's settlement points against the hub, by day and month (derived), and their hourly prices (internal)
    (r"^ercot_4cp_intervals$", "power"),  # session 359: ERCOT's four coincident-peak intervals by year
]


def load_licenses():
    if not os.path.exists(SOURCES):
        raise FileNotFoundError(f"{SOURCES} is missing; the connectors write it")
    reg = pd.read_csv(SOURCES, dtype=str, keep_default_na=False)
    return dict(zip(reg["source"], reg["license"]))


def iso_of(table):
    members = [old for old, new in MIGRATED.items() if new == table]
    if members:  # session 29: a consolidated table spans its members' ISOs
        return ";".join(sorted({iso_of(m) for m in members}))
    parts = table.split("_")
    if table == "price_board_carbon":  # session 30: CARB and RGGI, no ISO
        return "none"
    if table == "shoulder_hours_monthly":  # session 75
        return "CAISO;ERCOT"
    if table in ("storage_buildout_monthly", "storage_owners_monthly"):  # session 72 (session 69): the seven grids, and the US outside them; session 87
        return "CAISO;ERCOT;ISO-NE;MISO;NYISO;PJM;SPP"
    if table == "price_board_stats":  # session 127: the five grids whose hub prices are public and not paused (no MISO)
        return "CAISO;ERCOT;ISO-NE;NYISO;SPP"
    if table.startswith("price_board_") or table.startswith("cost_of_power_") or table == "merchant_revenue_monthly":  # session 30; session 37 the same six
        return "CAISO;ERCOT;ISO-NE;MISO;NYISO;SPP"
    if table in ("eia930_daily_total_interchange", "eia930_event_hourly_interchange", "ba_supply_monthly", "eia930_daily_demand"):  # session 68: every BA EIA reports
        return "CAISO;ERCOT;ISO-NE;MISO;NYISO;PJM;SPP"
    if table in ("eia930_all_interchange", "grid_network_nodes", "grid_network_links", "eia930_daily_interchange",  # session 49: every BA EIA reports
                 "lbnl_interconnection_queue", "ai_power_regions"):  # session 62: the seven ISOs (Berkeley Lab also non-ISO West and Southeast)
        return "CAISO;ERCOT;ISO-NE;MISO;NYISO;PJM;SPP"
    if table == "battery_stack_review_monthly":  # session 86: the two grids in review
        return "NYISO;SPP"
    if table in ("battery_stack_monthly", "battery_stack_stress_daily"):  # session 67: ERCOT and CAISO (session 246: the stress days too; ERCOT alone until then)
        return "CAISO;ERCOT"
    if table == "price_years_by_window":  # session 357: the public grids of the three economics pages
        return "CAISO;ERCOT;SPP"
    if table in ("node_basis_daily", "node_basis_summary"):  # session 358: ERCOT's settlement points
        return "ERCOT"
    if table == "iso_all_capacity_prices":  # session 65: the markets with a capacity auction (ERCOT and CAISO have none)
        return "ISO-NE;MISO;NYISO;PJM"
    if table == "iso_hub_prices_history":  # session 49: the five ISOs' main hubs (ERCOT's history is its own table)
        return "CAISO;ISO-NE;MISO;NYISO;SPP"
    if table == "iso_zone_prices_history":  # session 140: NYISO's zones, CAISO's ZP26 and SPP South (ISO-NE's are isone_zone_prices_history, internal)
        return "CAISO;NYISO;SPP"
    if table in ("eia930_all_history", "noaa_isd_hourly", "noaa_grid_weather_stations", "noaa_grid_weather_hourly", "noaa_grid_weather_daily",
                 "eia930_demand_weather", "noaa_station_weather_hourly"):  # session 49: the seven ISO BAs, and their weather stations; session 126: their weighted weather and demand with it taken out
        return "CAISO;ERCOT;ISO-NE;MISO;NYISO;PJM;SPP"
    if table == "eia930_demand_growth":  # session 2298: the seven ISO BAs and the Lower 48 (it was read as "DEMAND")
        return "CAISO;ERCOT;ISO-NE;MISO;NYISO;PJM;SPP;US48"
    if table == "census_metro_population":  # session 129: metropolitan areas, no ISO
        return "none"
    if table == "rrc_lease_production_monthly":  # session 49: Texas leases, no ISO
        return "none"
    if table in ("event_window_daily", "event_study_estimates"):  # session 36B Uri in ERCOT; session 36C COVID-19 in the seven ISO BAs and US48; session 47 its event studies
        return "CAISO;ERCOT;ISO-NE;MISO;NYISO;PJM;SPP;US48"
    if table == "storage_daily_cycle":  # session 34: CAISO's rows from caiso_battery_storage, with the EIA-930 BAs
        return "CAISO;ERCOT;ISO-NE;MISO;SPP;US48"
    if table == "eia930_all_storage":  # session 31: the BAs with an EIA-930 BAT series
        return "ERCOT;ISO-NE;MISO;SPP;US48"
    if table in ("eia930_all_emissions", "carbon_intensity_hourly", "carbon_intensity_daily",
                 "carbon_intensity_monthly"):  # session 32; monthly session 34
        return "CAISO;ERCOT;ISO-NE;MISO;NYISO;PJM;SPP;US48"
    if table == "storage_capacity":  # session 31: the national EIA-860M battery inventory
        return "none"
    if parts[0] == "eia930":
        return BA_LABEL.get(parts[1], parts[1].upper())
    if parts[0] in ("eia", "carb", "rggi", "fred", "eia860m", "portwatch", "energy", "datacenter", "api"):
        return "none"  # not an ISO series ("n/a" would read back as missing)
    return ISO_LABEL.get(parts[0], parts[0])


def sector_of(table):
    for pat, sectors in SECTOR_RULES:
        if re.match(pat, table):
            bad = [s for s in sectors.split(";") if s not in SECTORS]
            if bad:
                raise ValueError(f"{table}: sectors {bad} are not in {SECTORS}")
            return sectors
    raise ValueError(f"{table}: no sector rule in build_coverage.SECTOR_RULES matches; add one")


def derived_from(header):
    """Input tables of a derived table, from its 'Derived from:' header line; None if not derived."""
    for h in header:
        h = h.lstrip("#").strip()
        if h.startswith("Derived from:"):
            # session 29: an input named by its old name is read as the consolidated table it moved into
            return list(dict.fromkeys(MIGRATED.get(t.strip(), t.strip()) for t in h.split(":", 1)[1].split(";")
                                      if t.strip()))
    return None


def declared_license(header):
    """A table may declare its own license in a 'License: public|internal' header line
    (session 7: news_index is public although its outlets' text is internal)."""
    for h in header:
        h = h.lstrip("#").strip()  # header lines arrive with their leading '# '
        m = re.match(r"\s*License: (public|internal)[.\s]", h + " ")
        if m:
            return m.group(1)
    return None


def last_run(header):
    """Run id of the run that last wrote the file, from its 'Retrieved:' line, as ISO UTC."""
    for h in header:
        m = re.search(r"Retrieved: (\d{8}T\d{6}Z)", h)
        if m:
            t = pd.to_datetime(m.group(1), format="%Y%m%dT%H%M%SZ", utc=True)
            return t.strftime("%Y-%m-%dT%H:%M:%SZ")
    return ""


def events_row(path, header, df, licenses, status):
    """Coverage for an events table (session 6): times from event_date, counts of sources."""
    table = os.path.splitext(os.path.basename(path))[0]
    d = df["event_date"].where(df["event_date"].str.contains("T"), df["event_date"] + "T00:00:00Z")
    ts = pd.to_datetime(d, format=erw_validate.TS_FMT, utc=True)
    sources = sorted(df["source"].unique())
    unknown = [s for s in sources if s not in licenses]
    if unknown:
        raise ValueError(f"{table}: sources {unknown[:5]} are not in {SOURCES}; cannot set its license")
    license_ = declared_license(header) or (
        "internal" if any(licenses[s] == "internal" for s in sources) else "public")
    return {
        "table": table, "iso": "none", "market": "", "n_nodes": len(sources), "interval": "event",
        "ts_min": ts.min().strftime("%Y-%m-%dT%H:%M:%SZ"), "ts_max": ts.max().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n_rows": len(df), "source_report": f"{len(sources)} outlets", "last_run": last_run(header),
        "validator_status": status, "license": license_, "sector": sector_of(table),
        "_variable": "events: " + ", ".join(sorted(df["event_type"].unique())),
        "_nodes": f"{len(sources)} sources",
    }


def entities_row(path, header, df, licenses, status):
    """Coverage for an entities table (session 8): a snapshot, so ts_min and ts_max are the
    retrieval time of the snapshot; n_nodes counts entities."""
    table = os.path.splitext(os.path.basename(path))[0]
    got = pd.to_datetime(df["retrieved_at"], format=erw_validate.TS_FMT, utc=True)
    sources = sorted(df["source"].unique())
    unknown = [s for s in sources if s not in licenses]
    if unknown:
        raise ValueError(f"{table}: sources {unknown} are not in {SOURCES}; cannot set its license")
    license_ = declared_license(header) or (
        "internal" if any(licenses[s] == "internal" for s in sources) else "public")
    vint = sorted(df["vintage"].unique()) if "vintage" in df else []
    return {
        "table": table, "iso": iso_of(table), "market": "", "n_nodes": int(df["entity_id"].nunique()),
        "interval": "snapshot", "ts_min": got.min().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ts_max": got.max().strftime("%Y-%m-%dT%H:%M:%SZ"), "n_rows": len(df),
        "source_report": ";".join(sources), "last_run": last_run(header),
        "validator_status": status, "license": license_, "sector": sector_of(table),
        "_variable": "entities: " + ", ".join(sorted(df["entity_type"].unique()))
                     + (f"; vintage {', '.join(vint)}" if vint else ""),
        "_nodes": f"{df['entity_id'].nunique()} entities",
    }


# Session 36A: a series file larger than this is read for coverage in one streamed pyarrow pass over the columns
# coverage needs, never whole (the emissions table is 4.3 million rows, the ERCOT history 3 million); its validator
# status still comes from erw_validate.validate, the gate
LARGE_BYTES = 100 * 1024 * 1024
FACT_COLS = ["entity", "variable", "ts_utc", "source", "node", "market", "freq"]


def series_facts(path):
    """(header lines, facts) of a series file from one streamed pass: rows, ts_utc min and max (ISO strings, which
    sort as times once the validator has passed them), and the distinct values of FACT_COLS."""
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.csv as pcsv
    header, cols = [], None
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                header.append(line.rstrip("\r\n"))
                continue
            cols = line.strip().split(",")
            break
    want = [c for c in FACT_COLS if c in cols]
    reader = pcsv.open_csv(path, read_options=pcsv.ReadOptions(skip_rows=len(header), block_size=1 << 24),
                           convert_options=pcsv.ConvertOptions(include_columns=want,
                                                               column_types={c: pa.string() for c in want}))
    seen = {c: set() for c in want}
    n, tmin, tmax = 0, None, None
    for b in reader:
        n += b.num_rows
        for c in want:
            seen[c] |= set(pc.unique(b.column(c)).to_pylist())
        mm = pc.min_max(b.column("ts_utc")).as_py()
        tmin = mm["min"] if tmin is None or mm["min"] < tmin else tmin
        tmax = mm["max"] if tmax is None or mm["max"] > tmax else tmax
    return header, {"n": n, "ts_min": tmin, "ts_max": tmax, **seen}


def is_series(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                return line.startswith("entity,variable,ts_utc,")
    return False


def large_series_row(path, header, facts, report, licenses):
    """The series row of table_row, from series_facts instead of a whole frame (session 36A)."""
    n_err, n_warn = len(report["errors"]), len(report["warnings"])
    status = "pass" if not n_err else f"blocked ({n_err} errors)"
    if n_warn:
        status += f", {n_warn} warnings"
    table = os.path.splitext(os.path.basename(path))[0]
    sources = sorted(facts["source"])
    unknown = [s for s in sources if s not in licenses]
    if unknown:
        raise ValueError(f"{table}: sources {unknown} are not in {SOURCES}; cannot set its license")
    license_ = declared_license(header) or (
        "internal" if any(licenses[s] == "internal" for s in sources) else "public")
    nodes = sorted(n for n in facts.get("node", set()) if n)
    return {
        "table": table, "iso": iso_of(table),
        "market": ";".join(sorted(m for m in facts["market"] if m)) if "market" in facts else "",
        "n_nodes": len(nodes) if nodes else len(facts["entity"]),
        "interval": ";".join(sorted(facts["freq"])) if "freq" in facts else "",
        "ts_min": facts["ts_min"], "ts_max": facts["ts_max"], "n_rows": facts["n"],
        "source_report": ";".join(sources), "last_run": last_run(header), "validator_status": status,
        "license": license_, "sector": sector_of(table), "_derived_from": derived_from(header),
        "_variable": ", ".join(sorted(facts["variable"])),
        "_nodes": ", ".join(nodes) if nodes else ", ".join(sorted(facts["entity"])),
    }


# Session 36A: the validator's own reports of this run (erw_validate.py --json, written by run_daily.sh just before
# coverage), keyed by absolute path. A table's report is reused only when the file has not changed since the reports
# were written; otherwise, or without reports, the table is validated here as before.
REPORTS = {}


def load_reports(path):
    import json
    if not path or not os.path.exists(path):
        return {}
    # the validator's start (run_daily.sh touches <reports>.started just before it runs): a file changed after that may
    # have been validated before the change, so only files older than the start are reused; without the marker, none is
    marker = path + ".started"
    if not os.path.exists(marker):
        return {}
    at = os.path.getmtime(marker)
    out = {}
    for r in json.load(open(path, encoding="utf-8")):
        f = os.path.abspath(r["file"])
        if r.get("verdict") in ("pass", "blocked") and os.path.exists(f) and os.path.getmtime(f) <= at:
            out[f] = r
    return out


def report_of(path):
    return REPORTS.get(os.path.abspath(path)) or erw_validate.validate(path)


def table_row(path, licenses):
    if os.path.getsize(path) > LARGE_BYTES and is_series(path):  # session 36A: validated, then streamed
        report = report_of(path)
        header, facts = series_facts(path)
        return large_series_row(path, header, facts, report, licenses)
    # session 29: validate first, then read, so a large table (the ERCOT history) is never held twice
    report = report_of(path)
    header, df = erw_validate.read(path)
    if list(df.columns[:2]) == ["entity_id", "entity_type"]:
        n_err, n_warn = len(report["errors"]), len(report["warnings"])
        status = "pass" if not n_err else f"blocked ({n_err} errors)"
        return entities_row(path, header, df, licenses, status + (f", {n_warn} warnings" if n_warn else ""))
    if "event_id" in df.columns:
        n_err, n_warn = len(report["errors"]), len(report["warnings"])
        status = "pass" if not n_err else f"blocked ({n_err} errors)"
        return events_row(path, header, df, licenses, status + (f", {n_warn} warnings" if n_warn else ""))
    n_err, n_warn = len(report["errors"]), len(report["warnings"])
    status = "pass" if not n_err else f"blocked ({n_err} errors)"
    if n_warn:
        status += f", {n_warn} warnings"
    table = os.path.splitext(os.path.basename(path))[0]
    ts = pd.to_datetime(df["ts_utc"], format=erw_validate.TS_FMT, utc=True)
    sources = sorted(df["source"].unique())
    unknown = [s for s in sources if s not in licenses]
    if unknown:
        raise ValueError(f"{table}: sources {unknown} are not in {SOURCES}; cannot set its license")
    license_ = declared_license(header) or (
        "internal" if any(licenses[s] == "internal" for s in sources) else "public")
    nodes = sorted(n for n in df["node"].unique() if n) if "node" in df else []
    return {
        "table": table,
        "iso": iso_of(table),
        "market": ";".join(sorted(m for m in df["market"].unique() if m)) if "market" in df else "",
        "n_nodes": len(nodes) if nodes else int(df["entity"].nunique()),
        "interval": ";".join(sorted(df["freq"].unique())) if "freq" in df else "",
        "ts_min": ts.min().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ts_max": ts.max().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n_rows": len(df),
        "source_report": ";".join(sorted(df["source"].unique())),
        "last_run": last_run(header),
        "validator_status": status,
        "license": license_,
        "sector": sector_of(table),
        "_derived_from": derived_from(header),
        # for the markdown only
        "_variable": ", ".join(sorted(df["variable"].unique())),
        "_nodes": ", ".join(nodes) if nodes else ", ".join(sorted(df["entity"].unique())),
    }


# Session 272 (the owner's ruling of 14 October 2026): a public selection of an internal table. Its own header declares it
# public, and only the rows and columns the rule lets through are in it, so its internal input does not make it internal.
PUBLIC_SELECTIONS = {
    "large_load_public": "the large-load statements whose document is public, as facts with a link and no quoted text (session 255's rule)",
}


def apply_derived(rows):
    """Mark derived tables and check their license against their inputs (Decision 23)."""
    by = {r["table"]: r for r in rows}
    # Session 33: an input absent on this machine but in the previous coverage (it is carried over below, as CARB is on
    # the GitHub runner, where its server answers HTTP 202) keeps its license from there. On 2026-09-29 the daily run
    # failed here: price_board_carbon carries its CARB rows forward, and its input was not in warehouse/output.
    prev = {}
    if os.path.exists(CSV):
        p = pd.read_csv(CSV, dtype=str, keep_default_na=False)
        prev = dict(zip(p["table"], p["license"]))
    lic = lambda t: by[t]["license"] if t in by else prev[t]  # noqa: E731
    for r in rows:
        inputs = r.pop("_derived_from", None)
        r["derived"] = "yes" if inputs is not None else "no"
        if inputs is None:
            continue
        missing = [t for t in inputs if t not in by and t not in prev]
        if missing:
            raise ValueError(f"{r['table']}: input tables {missing} are not in warehouse/output nor in the previous "
                             "coverage")
        want = "internal" if any(lic(t) == "internal" for t in inputs) else "public"
        if r["table"] in PUBLIC_SELECTIONS and r["license"] == "public":
            continue  # session 272: public by the owner's ruling, whatever its input
        if r["license"] != want:
            raise ValueError(f"{r['table']}: license {r['license']}, but its inputs make it {want}")
    return rows


def header_of(table):
    path = os.path.join(OUT, table + ".csv")
    with open(path, encoding="utf-8") as f:
        return [ln.lstrip("#").strip() for ln in itertools.takewhile(lambda ln: ln.startswith("#"), f)]


def tier_by_rule(table, derived):
    for tier, pat in TIER_RULES:
        if re.match(pat, table):
            return tier
    return "derived" if derived == "yes" else "source"


def apply_tiers(rows):
    """Session 28: the provenance tier of every table built here (see the module docstring)."""
    by = {r["table"]: r for r in rows}
    inputs = {}
    for r in rows:
        r["tier"] = tier_by_rule(r["table"], r["derived"])
        # the "Derived from:" inputs, separated by ";" or "," (datacenter_facilities uses commas)
        line = next((h for h in header_of(r["table"]) if h.startswith("Derived from:")), "")
        inputs[r["table"]] = [MIGRATED.get(t.strip(), t.strip()) for t in re.split(r"[;,]", line.split(":", 1)[1])
                              if t.strip()] if line else []  # session 29: old names through the map
    changed = True
    while changed:  # a table built from a model_extracted one is model_extracted
        changed = False
        for r in rows:
            if r["tier"] != "model_extracted" and any(by.get(t, {}).get("tier") == "model_extracted"
                                                       for t in inputs[r["table"]]):
                r["tier"], changed = "model_extracted", True
    for r in rows:
        header = header_of(r["table"])
        with open(os.path.join(OUT, r["table"] + ".csv"), encoding="utf-8") as f:
            cols = next(ln for ln in f if not ln.startswith("#")).rstrip(chr(13) + chr(10)).split(",")
        names_model = "model_id" in cols or any(re.search(r"(?<![a-z])claude-[a-z]", h) for h in header)
        if names_model and r["tier"] != "model_extracted":
            raise ValueError(f"{r['table']}: its rows or header name a model, but its tier is {r['tier']}; "
                             "add it to build_coverage.TIER_RULES as model_extracted")
    return rows


RETIRED_FILE = os.path.join(ROOT, "warehouse", "metadata", "retired_tables.csv")


def retired_tables():
    """Session 207: tables the ERW no longer stores (retired_tables.csv: FRED's copies, on the owner's ruling of 12
    October 2026). A retired table's row leaves coverage for good and is not carried over; its file, if a machine
    still has one, is not a table of the warehouse."""
    if not os.path.exists(RETIRED_FILE):
        return set()
    return set(pd.read_csv(RETIRED_FILE, dtype=str, keep_default_na=False)["table"])


def carried_over(present):
    """Rows of the previous coverage for tables not in warehouse/output on this machine:
    (CSV rows, {table: its line in docs/coverage.md})."""
    if not os.path.exists(CSV):
        return [], {}
    prev = pd.read_csv(CSV, dtype=str, keep_default_na=False)
    # session 29: a table consolidated into another is gone for good, not carried over (table_migrations.csv);
    # session 207: so is a retired table (retired_tables.csv)
    gone = prev[~prev["table"].isin(present) & ~prev["table"].isin(set(MIGRATED) | retired_tables())].to_dict("records")
    md = {}
    if os.path.exists(DOC):
        with open(DOC, encoding="utf-8") as f:
            for line in f:
                m = re.match(r"^\| `([a-z0-9_]+)` \|", line)
                if m:
                    md[m.group(1)] = line.rstrip("\n")
    lost = [r["table"] for r in gone if r["table"] not in md]
    if lost:
        raise ValueError(f"cannot carry over {lost}: no line for them in {os.path.relpath(DOC, ROOT)}")
    return gone, md


MD_COLS = ["Table", "ISO", "Market", "Variable", "Nodes", "Interval",
           "First interval (UTC)", "Last interval (UTC)", "Rows", "Source report",
           "Last run (UTC)", "Validator", "License", "Sector", "Derived", "Tier",
           "Method"]  # session 674: the table's method note, linked
_NOTES = {}


def method_notes():
    """Session 674: {table: its note, relative to docs/}. A note named after its table (docs/methods/<table>.md), else a
    note whose line beginning "Tables: " names the table in backticks (a note of one source with several tables)."""
    if not _NOTES:
        paths = sorted(glob.glob(os.path.join(ROOT, "docs", "methods", "*.md")))
        for p in paths:
            _NOTES[os.path.basename(p)[:-3]] = f"methods/{os.path.basename(p)}"
        for p in paths:
            with open(p, encoding="utf-8") as f:
                for ln in f:
                    if ln.startswith("Tables: "):
                        for t in re.findall(r"`([a-z0-9_]+)`", ln):
                            _NOTES.setdefault(t, f"methods/{os.path.basename(p)}")
    return _NOTES


def method_cell(table):
    note = method_notes().get(table)
    return f"[{note[len('methods/'):-3]}]({note})" if note else ""


def with_method(line):
    """Session 674: a coverage.md table line written before the Method column, given its cell (other lines unchanged)."""
    m = re.match(r"^\| `([a-z0-9_]+)` \|", line)
    if m and len(re.findall(r"(?<!\\)\|", line)) == len(MD_COLS):   # one bar short: no Method cell yet
        return line + f" {method_cell(m.group(1))} |"
    return line


def md_line(r):
    """A built row as its line of docs/coverage.md."""
    cells = [f"`{r['table']}`", r["iso"], r["market"], r["_variable"],
             f"{r['n_nodes']}: {r['_nodes']}", r["interval"],
             r["ts_min"].replace("T", " ").rstrip("Z"), r["ts_max"].replace("T", " ").rstrip("Z"),
             f"{r['n_rows']:,}", r["source_report"].replace(";", "; "),
             r["last_run"].replace("T", " ").rstrip("Z"), r["validator_status"], r["license"], r["sector"].replace(";", ", "), r["derived"], r["tier"],
             method_cell(r["table"])]
    return "| " + " | ".join(str(c).replace("|", "\\|") for c in cells) + " |"


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Build docs/coverage.md and warehouse/metadata/coverage.csv")
    ap.add_argument("--reports", help="session 36A: erw_validate.py --json output of this run, reused for unchanged files")
    ap.add_argument("--only", help="session 119: rebuild only the rows of the tables whose name matches this regular "
                                   "expression; every other row is carried over from the coverage as it stands, word for "
                                   "word. For a job that changed one table (the cost ledger after the Roundup) and loads it")
    args = ap.parse_args()
    REPORTS.update(load_reports(args.reports))
    if args.reports:
        print(f"validator reports reused for {len(REPORTS)} unchanged tables ({args.reports})")
    licenses = load_licenses()
    files = sorted(glob.glob(os.path.join(OUT, "*.csv")))
    retired = [p for p in files if os.path.basename(p)[:-4] in retired_tables()]
    if retired:  # session 207: a retired table's file still on a machine is left out, and said
        print(f"retired tables left out of coverage (warehouse/metadata/retired_tables.csv): {', '.join(os.path.basename(p)[:-4] for p in retired)}")
        files = [p for p in files if p not in retired]
    if args.only:
        files = [p for p in files if re.search(args.only, os.path.basename(p)[:-4])]
        if not files:
            print(f"FAILED: --only {args.only!r} matches no table in {os.path.relpath(OUT, ROOT)}; coverage left as it is", file=sys.stderr)
            return 1
        print(f"--only {args.only}: rebuilding {len(files)} row(s): {', '.join(os.path.basename(p)[:-4] for p in files)}; every other row is carried over")
    rows = apply_tiers(apply_derived([table_row(p, licenses) for p in files]))
    carried, carried_md = carried_over({r["table"] for r in rows})
    for r in carried:  # session 28: a row carried from a coverage.csv written before the tier column
        if not r.get("tier"):
            r["tier"] = tier_by_rule(r["table"], r.get("derived", "no"))
            carried_md[r["table"]] = carried_md[r["table"]] + f" {r['tier']} |"
    if carried:
        print(f"carried over from the previous coverage (not in warehouse/output here): "
              f"{len(carried)} tables: {', '.join(r['table'] for r in carried)}")
    out_rows = sorted([{c: r[c] for c in CSV_COLS} for r in rows] + carried, key=lambda r: r["table"])
    pd.DataFrame(out_rows, columns=CSV_COLS).to_csv(CSV, index=False, lineterminator="\n")
    if args.only:
        # session 119: docs/coverage.md keeps every line but the rebuilt tables' own (a table new to it goes in at its
        # place in the alphabet); the notes under the table describe a whole build and are left as that build wrote them
        with open(DOC, encoding="utf-8") as f:
            doc = f.read().split("\n")
        name_of = lambda ln: (re.match(r"^\| `([a-z0-9_]+)` \|", ln) or [None, None])[1]  # noqa: E731
        todo = {r["table"]: md_line(r) for r in rows}
        out_doc = []
        gone_for_good = set(MIGRATED) | retired_tables()
        for i, ln in enumerate(doc):  # session 674: the Method column, once, on a page written before it
            if ln.startswith("| Table |") and "| Method |" not in ln:
                doc[i] = "| " + " | ".join(MD_COLS) + " |"
                doc[i + 1] = "|" + "|".join("---" for _ in MD_COLS) + "|"
            elif ln.endswith("written by a model reading text)."):
                doc[i] = ln + " `Method` links the table's method note under `docs/methods/`, where one names it."
            else:
                doc[i] = with_method(ln)
        for ln in doc:
            n = name_of(ln)
            if n is not None:
                for new in sorted(k for k in todo if k < n):
                    out_doc.append(todo.pop(new))
                if n in todo:
                    ln = todo.pop(n)
                elif n in gone_for_good and n not in {r["table"] for r in carried}:  # session 207: a retired table's line goes with its row
                    continue
            out_doc.append(ln)
        last = max((i for i, ln in enumerate(out_doc) if name_of(ln) is not None), default=None)
        if last is not None and todo:  # session 2134: a table after the alphabet's last goes in after the last line
            out_doc[last + 1:last + 1] = [todo.pop(k) for k in sorted(todo)]
        if todo:
            raise ValueError(f"--only: no place in {os.path.relpath(DOC, ROOT)} for {sorted(todo)}")
        with open(DOC, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(out_doc))
        print(f"wrote the rows of {', '.join(r['table'] for r in rows)} in {os.path.relpath(DOC, ROOT)} and {os.path.relpath(CSV, ROOT)}: "
              f"{len(out_rows)} tables ({len(rows)} built here, {len(carried)} carried over as they stood)")
        return 0

    md_cols = MD_COLS
    lines = [
        "# ERW coverage",
        "",
        "What the Energy Research Warehouse (ERW) holds today: one row per table in "
        "`warehouse/output/`. The machine-readable copy is `warehouse/metadata/coverage.csv`, the "
        "ERW equivalent of the metadata table the IRW (Item Response Warehouse) calls "
        "`metadata.csv`.",
        "",
        "**Generated, do not edit by hand.** Rebuilt by the daily workflow, or with "
        "`python warehouse/metadata/build_coverage.py`. Every value comes from the table's own "
        "rows, its provenance header, or `erw_validate.py`. Interval timestamps are interval "
        "starts; day-ahead tables can run past today because a published next-day auction is "
        "included. `License` is `public` or `internal` (internal: licensed for internal use "
        "only, such as PJM data; never shown on the public site). `Sector` is what "
        "`erw.filter(sector=...)` matches: power, gas, oil, products, lng, coal, uranium, "
        "carbon, capacity, metals, equities, news. `Derived` is yes for a table the ERW computes "
        "from other ERW tables (method in `docs/methods/`). `Tier` is the provenance tier "
        "(`docs/datastandard.md`): `source` (as the publisher published it), `derived` (computed by ERW "
        "code, no model) or `model_extracted` (at least one column written by a model reading text). `Method` links the table's method note under `docs/methods/`, where one names it.",
        "",
        "| " + " | ".join(md_cols) + " |",
        "|" + "|".join("---" for _ in md_cols) + "|",
    ]
    built = {r["table"]: r for r in rows}
    for name in sorted(list(built) + [r["table"] for r in carried]):
        if name not in built:
            lines.append(with_method(carried_md[name]))
            continue
        lines.append(md_line(built[name]))
    # session 29: a member of a consolidated table counts as present when its consolidated table is
    def present(name):
        return os.path.exists(os.path.join(OUT, name + ".csv")) or (
            name in MIGRATED and os.path.exists(os.path.join(OUT, MIGRATED[name] + ".csv")))
    missing = [f"{label} {m.upper()}" for iso, label in ISO_LABEL.items() for m in ("dam", "rtm")
               if not glob.glob(os.path.join(OUT, f"{iso}_{m}_*.csv"))
               and not any(present(o) for o in MIGRATED if o.startswith(f"{iso}_{m}_"))]
    missing += [f"EIA-930 {BA_LABEL[b]} {fam}" for b in BA_LABEL for fam in ("demand", "generation")
                if not present(f"eia930_{b}_{fam}")]
    if carried:
        lines += ["", f"Carried over unchanged from the previous coverage, because this run's "
                  f"`warehouse/output/` does not hold them (the daily CI runner restores only the "
                  f"rolling-window tables; every table is on Redivis): {len(carried)} tables, "
                  + ", ".join(f"`{r['table']}`" for r in carried) + "."]
    # session 18: a derived table built without some of its inputs names them in an
    # "Absent inputs:" header line (energy_projects when a queue could not be pulled)
    absent_notes = []
    for name in sorted(built):
        with open(os.path.join(OUT, name + ".csv"), encoding="utf-8") as f:
            header = list(itertools.takewhile(lambda ln: ln.startswith("#"), f))
        for h in header:
            h = h.lstrip("#").strip()
            if h.startswith("Absent inputs:"):
                absent_notes.append(f"`{name}` was built without some inputs. {h}")
    if absent_notes:
        lines += ["", "Absent inputs (session 18): " + " ".join(absent_notes)]
    lines += ["", "Markets and series with no table: " + (", ".join(missing) if missing else "none") +
              ". PJM prices need a PJM API key, which the ERW does not have yet. Why anything else "
              "is missing is in `warehouse/metadata/run_status.csv` and the connector's run log in "
              "`warehouse/output/logs/`.", ""]
    with open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print(f"wrote {os.path.relpath(DOC, ROOT)} and {os.path.relpath(CSV, ROOT)}: {len(out_rows)} tables "
          f"({len(rows)} built here, {len(carried)} carried over)")


if __name__ == "__main__":
    sys.exit(main() or 0)
