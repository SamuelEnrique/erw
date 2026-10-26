#!/usr/bin/env python3
"""Redivis release v1, prepared (session 275): everything a person needs for one click, and nothing done on Redivis.

Energy Research Warehouse (ERW). docs/redivis/release-v1.md is the person's steps. This builds the package from what
the repository and this machine hold, makes no request and writes nothing to Redivis:

    python warehouse/redivis/release_v1.py                     docs/redivis/release-v1/: tables.csv, variables.csv, README.md
    python warehouse/redivis/release_v1.py --out-dir DIR       read the tables from DIR (a worktree reads the main checkout's)
    python warehouse/redivis/release_v1.py --check             the files agree with coverage and the license record (exit 1 if not)
    python warehouse/redivis/release_v1.py --target stanford --calls-only
                                                               session 1010: the README written again and the fetch columns
                                                               added to tables.csv, from the files as they are (no table read)

Which tables are in v1: every table that coverage.csv flags public and that is public on 21 October 2026, the public
day: not "license needed" in warehouse/metadata/license_status.csv without a recorded permission, not retired
(retired_tables.csv), not a consolidated table's old member (table_migrations.csv). The rest of the public dataset's
draft is named in tables.csv with its reason, so the person removes exactly those before the click. The metadata tables
the uploader adds (erw_coverage, erw_sources, erw_headers) are in v1 too.

    tables.csv     table, in_v1, reason, shape, rows, first, last, interval, description (the header's title line),
                   license_line (the header's own "License:" line), citation, publishers, and (session 1010) fetch_python,
                   fetch_stata, fetch_r: the one line that fetches the table in each of the ERW's packages
    variables.csv  table, name, kind (series variable or column), unit
    README.md      the dataset's README, for Redivis's dataset description
"""

import argparse
import csv
import datetime as dt
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
META = os.path.join(ROOT, "warehouse", "metadata")
DOCS = os.path.join(ROOT, "docs", "redivis", "release-v1")
PUBLIC_DAY = "2026-10-21"
DATASET = "energy_research_warehouse"
METADATA_TABLES = ("erw_coverage", "erw_sources", "erw_headers")
SERIES_FIRST = ["entity", "variable", "ts_utc", "value"]


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def header(path):
    out = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln in f:
            if not ln.startswith("#"):
                break
            out.append(ln[1:].strip())
    return out


def held(day=PUBLIC_DAY):
    """{table: reason} of the tables held from the public day: license needed, no permission recorded."""
    out = {}
    for r in rows(os.path.join(META, "license_status.csv")):
        if r["status"] == "license needed" and r["from"] <= day and not r.get("permission"):
            out[r["table"]] = f"license needed from {r['from']} ({r['publishers']}: {r['verdict']}); held whole for v1"
    return out


# Session 375: a public table the draft cannot hold for Redivis's storage (the account's free 10 GB is full, session
# 363). It is marked "held", not dropped: in v1 by its license, uploaded once the storage is settled (the owner's).
STORAGE_HELD = {
    "node_basis_daily": "held: Redivis storage (the account's free 10 GB is full; refused on 20 October 2026, session 363). "
                        "In v1 by its license once uploaded: python warehouse/redivis/upload.py node_basis_daily, after the storage is settled",
    # session 385: in the draft until 20 October, when the daily's upload was refused for storage (17:32 UTC) and the
    # uploader, which deletes a table before it uploads the new copy, left it out (Redivis answers 404 for it)
    "ercot_all_hub_prices_history": "held: Redivis storage (the account's free 10 GB is full; the upload of 20 October 2026, 17:32 UTC, "
                                    "was refused and the table is no longer in the draft, session 385). In v1 by its license once "
                                    "uploaded again: python warehouse/redivis/upload.py ercot_all_hub_prices_history, after the storage is settled",
}
# Session 489: the public tables of sessions 485 to 496 and 507, written on 21 October 2026 and never uploaded (an upload is a
# person's, and the storage is full). Held the same way: in v1 by their license once uploaded.
for _t in ("boem_renewable_leases", "egrid_power_plants", "eia861_utility_sales", "eia_aeo_electricity",
           "eia_seds_state_energy", "eia_steo_forecasts", "epa_ghgrp_power_co2", "nlr_atb_electricity_costs",
           "uswtdb_wind_turbines", "eia923_plant_fuel_annual", "eia861m_utility_sales_monthly",
           "eia_nuclear_outages_daily", "eia_nuclear_outages_facility_daily",
           "eia_gas_prices_state_monthly", "eia_gas_consumption_state_monthly", "eia_coal_prices_annual",
           "eia_gas_storage_state_monthly", "eia_state_capacity_annual", "eia_crude_production_state_monthly",
           "eia_gas_production_state_monthly", "eia_co2_state_annual", "eia_refinery_weekly",
           "eia_state_source_disposition_annual", "eia_net_metering_state_annual",
           "eia_nuclear_outages_generator_daily", "eia_gas_interstate_annual", "eia_crude_reserves_annual",
           "eia_gas_reserves_annual", "eia_coal_delivered_price_annual", "eia_petroleum_snd_monthly",
           "eia_product_supplied_monthly", "eia_wood_pellets_monthly",
           "eia_petroleum_stocks_monthly", "eia_gas_balance_annual",
           "eia_energy_efficiency_state_annual", "eia_meters_state_annual", "eia_power_co2_state_annual",
           "eia_coal_price_rank_annual", "eia_coal_trade_price_annual", "eia_drilling_monthly",
           "eia_gas_wells_annual", "eia930_subba_demand_hourly",
           "eia_heating_fuel_prices_weekly", "boem_ogor_lease_production_monthly",
           "eia930_subba_demand_hourly_2025", "eia_refinery_capacity_annual",
           "eia_refinery_inputs_monthly", "eia_refinery_production_monthly",
           "eia930_subba_demand_hourly_2024", "eia_padd_rail_barge_movements_monthly",
           "eia_gas_trade_country_monthly", "eia_gas_storage_capacity_monthly",
           "eia930_subba_demand_hourly_2023", "eia_ngl_production_monthly",
           "eia_oxygenate_production_monthly", "eia930_subba_demand_hourly_2022",
           "eia_crude_imports_detail_monthly", "eia930_subba_demand_hourly_2021", "eia930_subba_demand_hourly_2020", "eia930_subba_demand_hourly_2019", "utility_service_territories",
           "eia_coal_production_annual", "eia_coal_mine_production_annual", "eia861_utility_reliability", "ercot_cdr_reserve_margins", "ercot_transmission_projects", "eia861_delivery_only",
           "interconnection_agreements_signed", "interconnection_agreements_by_grid", "eia_petroleum_exports_by_destination", "eia_gas_consumers_state_annual", "eia861_utility_data", "eia861_demand_response", "eia861_dynamic_pricing",
           "eia861_advanced_meters", "eia861_net_metering", "ercot_cdr_units", "eia860_plants_annual", "eia_coal_receipts_annual", "eia861_short_form",
           "eia861_energy_efficiency",
           "eia861_operational_data",
           "eia861_distribution_systems",
           "eia861_distributed_generation",
           "eia860_generator_owners",
           "eia860_storage_generators",
           "eia860_solar_generators",
           "eia860_wind_generators",
           "eia_international_electricity_annual",
           "cer_electricity_trade",
           "frb_utility_output_monthly",
           "uspvdb_solar_facilities",
           "eia411_capacity_margins_annual",
           "eia860_multifuel_generators",
           "eia860_boilers",
           "eia860_cooling_systems",
           "eia860_emission_controls",
           "eia923_plant_fuel_monthly",
           "eia_gas_pipeline_projects",
           "eia923_fuel_receipts",
           "ercot_node_places",
           "eia_power_costs_annual",
           "eia_uranium_marketing_annual",
           "eia_world_electricity_annual",
           "cer_gas_trade",
           "ornl_eha_hydropower_plants",
           "eia_aeo_emm_regions",
           "lbnl_ppa_prices",
           "ornl_hydropower_pipeline",
           "ercot_node_transmission",
           "eia_world_oil_gas_annual",
           "nrc_power_reactors",
           "wb_commodity_prices_monthly",
           "eia_power_fuel_stocks_monthly",
           "eia_world_oil_monthly",
           "ornl_hydropower_relicensing",
           "ercot_node_planned_generation",
           "eia_world_coal_annual",
           "eia_world_energy_co2_annual",
           "ornl_npd_potential",
           "lbnl_solar_projects",
           "lbnl_hybrid_ppa_prices",
           "ornl_eha_hydropower_units",
           "lbnl_wind_capacity_factors",
           "ercot_node_wires_utilities",
           "onrr_production_monthly", "onrr_production_annual", "onrr_revenue_monthly",
           "lbnl_wind_costs", "lbnl_wind_turbine_orders",
           "eia_primary_energy_monthly",
           "usgs_mcs_critical_minerals",
           "blm_ca_renewable_rows",
           "eia_coal_distribution_quarterly",
           "eia_uranium_production_quarterly", "eia_uranium_facilities",
           "eia_ieo_projections",
           "usace_nid_dams",
           "eia_capacity_factors_annual", "eia_capacity_factors_monthly", "eia_heat_rates_annual",
           "egrid_subregions_annual",
           "doe_useer_employment",
           "nrc_new_reactor_applications", "nrc_advanced_reactor_preapplicants",
           "usbr_hydropower_monthly",
           "noaa_cpc_degree_days_daily",
           "boem_offshore_platforms",
           "doe_oe417_events",
           "eaglei_county_outages_daily",
           "epa_rfs_rins_monthly",
           "epa_rfs_fuel_annual",
           "eia_biofuel_plants",
           "msha_coal_mines",
           "msha_coal_production_quarterly",
           "fhwa_motor_fuel_monthly",
           "afdc_vehicle_registrations_annual",
           "irena_capacity_annual",
           "irs_soi_energy_credits_annual",
           "eia_state_to_state_capacity",
           "noaa_cpc_oni_monthly",
           "wfigs_wildfires",
           "gfz_kp_index_3h",
           "epa_ghg_inventory_annual",
           "scripps_co2_mlo_monthly",
           "doe_lead_energy_burden",
           "afdc_station_counts_annual",
           "noaa_ncei_storm_events",
           "nrc_event_notifications",
           "doe_lng_export_applications",
           "noaa_climdiv_state_monthly",
           "ornl_tedb_transportation_annual",
           "doe_grip_selections",
           "aeso_alberta_load_hourly",
           "eia_cbecs_commercial_buildings",
           "eia_lng_liquefaction_projects",
           "eia_mecs_manufacturing",
           "eia_recs_households",
           "cer_pipeline_throughput",
           "desnz_uk_electricity_quarterly",
           "desnz_uk_renewables_quarterly",
           "ieso_generation_fuel_hourly",
           "eurostat_electricity_monthly",
           "eurostat_electricity_trade_annual",
           "desnz_uk_gas_quarterly",
           "ssb_norway_electricity_monthly",
           "smard_germany_monthly",
           "cbs_netherlands_electricity_monthly",
           "scb_sweden_electricity_monthly",
           "statfi_finland_electricity_monthly",
           "energy_charts_central_europe",
           "statee_estonia_electricity_monthly",
           "singstat_singapore_electricity",
           "csp_latvia_electricity_monthly",
           "cso_ireland_electricity_monthly",
           "eia_petroleum_stocks_state_monthly",
           "bfe_switzerland_electricity_monthly",
           "ens_denmark_electricity_monthly",
           "cence_costarica_generation_monthly",
           "econtrol_austria_electricity_monthly",
           "ilr_luxembourg_electricity",
           "hagstofa_iceland_power_annual",
           "eehc_egypt_electricity_annual",
           "statcan_generation_class_annual",
           "statcan_power_disposition_annual",
           "epe_brazil_consumption_monthly",
           "eia_gas_other_uses_state_annual",
           "elexon_gb_demand_daily",
           "energinet_dk_production_hourly",
           "statec_lu_power_capacity_annual",
           "statec_lu_electricity_trade_annual",
           "statec_lu_electricity_generation_annual",
           "statbel_be_electricity_production_annual",
           "ine_es_dwellings_electricity_2021",
           "statat_austria_electricity_annual",
           "eurostat_renewable_shares_annual",
           "eurostat_electricity_consumption_annual",
           "dst_dk_electricity_supply_annual",
           "wapa_energy_sales_annual",
           "desnz_uk_fuel_used_generation_annual",
           "desnz_uk_mpp_capacity_countries_annual",
           "desnz_uk_capacity_by_connection_annual",
           "desnz_uk_derated_capacity_annual",
           "desnz_uk_co2_intensity_annual",
           "desnz_uk_plant_loads_annual",
           "desnz_uk_storage_annual",
           "desnz_uk_interconnector_flows_annual",
           "desnz_uk_power_stations",
           "nspower_ns_load_hourly",
           "desnz_gb_regional_gas_consumption_annual",
           "desnz_gb_regional_consumption_annual",
           "desnz_regional_renewable_capacity_annual",
           "desnz_regional_renewables_annual",
           "bchydro_ba_load_hourly",
           "desnz_uk_nations_electricity_annual",
           "asub_aland_electricity_sales_annual",
           "aedg_alaska_generation_monthly",
           "stat_kz_kazakhstan_electricity_annual",
           "cosit_iraq_electricity_annual",
           "stat_tj_tajikistan_electricity_annual",
           "edf_sei_islands_electricity_annual",
           "asub_aland_electricity_annual",
           "statai_anguilla_electricity_monthly",
           "eso_cayman_electricity_annual",
           "asli_liechtenstein_electricity_annual",
           "nawec_gambia_electricity_monthly",
           "ope_pf_electricity_annual",
           "enercal_nc_electricity_annual",
           "cisos_cook_electricity_quarterly",
           "siea_solomon_electricity_annual",
           "je_jersey_electricity_annual",
           "cbs_curacao_electricity_annual",
           "dbedt_hawaii_electricity_annual",
           "sbs_samoa_electricity_annual",
           "vmme_paraguay_electricity_annual",
           "bcrp_peru_hydrocarbons_monthly",
           "bcrp_peru_electricity_monthly",
           "abs_suriname_electricity_annual",
           "nbs_maldives_electricity",
           "arse_burkina_electricity_annual",
           "eec_eswatini_electricity_annual",
           "gastat_saudi_electricity_annual",
           "derk_bih_electricity_annual",
           "dfe_ni_electricity_monthly",
           "nsi_bulgaria_electricity_monthly",
           "eru_czech_electricity",
           "inseed_togo_electricity_annual",
           "arsel_cameroon_electricity_annual",
           "instat_madagascar_electricity_monthly",
           "sors_serbia_electricity_annual",
           "ask_kosovo_electricity_monthly",
           "nve_norway_reservoirs_weekly",
           "statgl_greenland_electricity_annual",
           "ncsi_oman_electricity_annual",
           "hagstova_faroe_electricity_annual",
           "slu_cso_electricity_annual",
           "grenada_cso_electricity_annual",
           "nso_malawi_electricity_sales_annual",
           "fbos_fiji_electricity_annual",
           "zimstat_zimbabwe_generation_monthly",
           "ewa_bahrain_electricity_annual",
           "epa_ghgrp_facility_emissions",
           "epa_lmop_landfill_projects",
           "epa_tri_energy_releases_annual",
           "eurostat_gas_imports_monthly",
           "eurostat_renewable_capacity_annual",
           "eurostat_oil_monthly",
           "eurostat_crude_imports_monthly",
           "eurostat_crude_imports_by_field_monthly",
           "statsbots_botswana_electricity_monthly",
           "eurostat_solid_fuels_monthly",
           "eurostat_hard_coal_imports_annual",
           "statbank_moldova_electricity_monthly",
           "eurostat_electricity_capacity_annual",
           "fema_disaster_declarations",
           "ieso_ontario_demand_hourly",
           "lbnl_tracking_the_sun",
           "nhc_hurdat2_track_points",
           "noaa_ncei_billion_disasters",
           "nrc_license_actions",
           "owid_ember_electricity_annual",
           "eia_shale_gas_reserves_annual",
           "eia_gas_heat_content_monthly",
           "eia_crude_quality_monthly",
           "ons_brazil_balance_hourly",
           "ree_spain_balance_monthly",
           "dosm_malaysia_electricity_monthly",
           "censtatd_hk_electricity",
           "aneel_siga_plants",
           "epra_kenya_electricity_annual",
           "statcan_electricity_trade_monthly",
           "eurostat_gas_balance_monthly",
           "eia_refinery_utilization_monthly",
           "eia_gas_for_others_annual",
           "statcan_petroleum_products_monthly",
           "statcan_energy_balance_annual",
           "eia_net_imports_monthly",
           "eurostat_electricity_production_annual",
           "statcan_generating_capacity_annual",
           "sne_panama_electricity_annual",
           "sne_panama_generation_monthly",
           "statsmu_mauritius_electricity_annual",
           "eia_lng_storage_annual",
           "eia_gas_plant_processing_annual",
           "eia_crude_tank_farm_stocks_monthly",
           "eia_gas_storage_type_monthly",
           "energy_charts_portugal_power",
           "energy_charts_italy_power",
           "rte_eco2mix_france_halfhourly",
           "usbr_crsp_reservoirs_daily",
           "usbr_mead_powell_daily",
           "usdm_drought_state_weekly",
           "blm_oil_gas_statistics_annual",
           "cec_total_system_generation_annual",
           "eia_seds_residential_annual",
           "noaa_uscrn_solar_monthly",
           "usgs_comcat_earthquakes_south_central",
           "usgs_streamflow_daily",
           "bpa_ba_hourly",
           "wb_electricity_access_annual",
           "census_bps_state_annual",
           "afdc_ev_charging_state_annual",
           "census_cbp_hosting_annual",
           "statcan_electricity_generation_monthly",
           "emi_nz_generation_demand_monthly",
           "census_c30_construction_monthly",
           "energy_charts_southeast_europe_daily",
           "census_qss_utilities_hosting_quarterly",
           "energy_charts_belgium_hourly",
           "statcan_oil_gas_supply_monthly",
           "ntd_transit_energy_annual",
           "epa_needs_units",
           "bsee_offshore_incidents",
           "nrc_rop_findings",
           "interconnection_durations", "interconnection_durations_summary",
           "grid_peak_vs_capacity"):  # 510 to 672 the same way
    STORAGE_HELD[_t] = ("held: not yet on Redivis (written 21 October 2026, session 489; the account's free 10 GB is full, "
                        f"session 363). In v1 by its license once uploaded: python warehouse/redivis/upload.py {_t}, after the "
                        "storage is settled")


def plan(day=PUBLIC_DAY):
    """[(table, in_v1, reason)] over coverage, in coverage's order."""
    cov = rows(os.path.join(META, "coverage.csv"))
    retired = {r["table"] for r in rows(os.path.join(META, "retired_tables.csv"))}
    migrated = {r["old_table"] if "old_table" in r else r[list(r)[0]] for r in rows(os.path.join(META, "table_migrations.csv"))}
    hold = held(day)
    out = []
    for r in cov:
        t = r["table"]
        if r["license"] != "public":
            continue   # an internal table is never in the public dataset (upload.py routes it to the private one)
        if t in retired:
            out.append((t, "no", "retired (warehouse/metadata/retired_tables.csv)"))
        elif t in migrated:
            out.append((t, "no", "a consolidated table's old member (warehouse/metadata/table_migrations.csv)"))
        elif t in hold:
            out.append((t, "no", hold[t]))
        elif t in STORAGE_HELD:
            out.append((t, "held", STORAGE_HELD[t]))
        else:
            out.append((t, "yes", "public, and public on the public day"))
    return out


def plan_stanford(day=PUBLIC_DAY):
    """Session 664 (chain 043): [(table, in_v1, reason)] for the Stanford dataset, datapages.erw:b9wm. A table is in it by its
    ERW verdict in docs/licenses.md (public), as the uploader's Stanford target sends it; a public table not yet in that
    draft (the target's manifest) is "held". Tables of any other verdict are never in that dataset, so they are not listed."""
    sys.path.insert(0, HERE)
    import upload  # the target's own gate and manifest, so the list is the uploader's
    erw = upload.erw_verdicts()
    man = os.path.join(ROOT, upload.CONFIG["targets"]["stanford"]["manifest"])
    sent = {r["table"] for r in rows(man)} if os.path.exists(man) else set()
    out = []
    for r in rows(os.path.join(META, "coverage.csv")):
        t = r["table"]
        if erw.get(t) != "public":
            continue
        if t in sent:
            out.append((t, "yes", "public by its ERW verdict (docs/licenses.md), and in the draft"))
        else:
            out.append((t, "held", "public by its ERW verdict, not yet in the draft: python warehouse/redivis/upload.py "
                                   f"--target stanford --prove-by-listing --tables {t}"))
    return out


STANFORD = {"dataset": "datapages.erw", "address": "https://stanford.redivis.com/datasets/b9wm-3hb080mtm",
            "doi": "10.57761/4f55-6d55", "docs": os.path.join(ROOT, "docs", "redivis", "release-v1-stanford")}
HELD_WHY = "the account's storage is full, and the table is added once it is settled."


def use_stanford():
    """Session 664: the package for the Stanford dataset, written to docs/redivis/release-v1-stanford/ (the old one stays)."""
    global DATASET, DOCS, HELD_WHY, plan
    DATASET, DOCS = STANFORD["dataset"], STANFORD["docs"]
    HELD_WHY = "it is not yet in the draft, and is added by the uploader's Stanford target before the release."
    plan = plan_stanford


def verdicts(path=os.path.join(ROOT, "docs", "licenses.md")):
    """{table: (publishers, verdict today)} from docs/licenses.md, "Every table" (session 205's record)."""
    out, on = {}, False
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if ln.startswith("## "):
                on = ln.strip() == "## Every table"
                continue
            m = re.match(r"^\| `([a-z0-9_]+)` \| ([^|]*) \| ([^|]*) \|", ln) if on else None
            if m:
                out[m.group(1)] = (m.group(2).strip(), m.group(3).strip())
    return out


def citation(table, sources, publishers):
    reps = [s for s in sources if table in [x.strip() for x in re.split(r"[;,]", s.get("tables", ""))]]
    names = sorted({s["publisher"] for s in reps}) or ([publishers] if publishers else [])
    reports = sorted({s["report"] for s in reps})
    head = "; ".join(names) if names else "Energy Research Warehouse (ERW)"
    rep = (" " + "; ".join(reports) + ".") if reports else ""
    return (f"{head}.{rep} Via the Energy Research Warehouse (ERW), table `{table}`, Redivis dataset `{DATASET}`, version v1 "
            "(released <date of the click>).")


def shape(cols):
    if cols[:4] == SERIES_FIRST:
        return "series"
    if cols[:2] == ["entity_id", "entity_type"]:
        return "entities"
    if "event_id" in cols:
        return "events"
    return "other"


def variables(path, cols, kind):
    """[(name, kind, unit)]: a series table's variables with their units (read in chunks), else its columns."""
    if kind != "series":
        return [(c, "column", "") for c in cols]
    seen = set()
    n = len(header(path))
    for ch in pd.read_csv(path, skiprows=n, usecols=["variable", "unit"], dtype=str, keep_default_na=False, chunksize=500_000):
        seen |= set(zip(ch["variable"], ch["unit"]))
    return [(v, "series variable", u) for v, u in sorted(seen)]


def build(out_dir, day=PUBLIC_DAY):
    cov = {r["table"]: r for r in rows(os.path.join(META, "coverage.csv"))}
    sources = rows(os.path.join(META, "sources.csv"))
    pubs = {r["table"]: r["publishers"] for r in rows(os.path.join(META, "license_tables.csv"))}
    record = verdicts()
    tables, variables_out, missing = [], [], []
    for t, in_v1, reason in plan(day):
        c = cov[t]
        path = os.path.join(out_dir, t + ".csv")
        head = header(path) if os.path.exists(path) else []
        title = (head[0] if head else "").replace("Energy Research Warehouse (ERW): ", "", 1)
        lic = next((h for h in head if h.startswith("License:")), "")
        if not lic and t in record:   # no license line in the header: the license record's verdict for the table
            who, verdict = record[t]
            lic = f"License: public. The publishers' own terms ({who}), as the ERW read them: {verdict} (docs/licenses.md)."
        cols, kind = [], ""
        if os.path.exists(path):
            with open(path, encoding="utf-8", errors="replace") as f:
                for ln in f:
                    if not ln.startswith("#"):
                        cols = next(csv.reader([ln]))
                        break
            kind = shape(cols)
            if in_v1 in ("yes", "held"):
                variables_out += [dict(table=t, name=n, kind=k, unit=u) for n, k, u in variables(path, cols, kind)]
        elif in_v1 == "yes":
            missing.append(t)
        tables.append(dict(table=t, in_v1=in_v1, reason=reason, shape=kind, rows=c["n_rows"], first=c["ts_min"], last=c["ts_max"],
                           interval=c["interval"], description=title, license_line=lic, citation=citation(t, sources, pubs.get(t, "")),
                           publishers=pubs.get(t, "")))
    for m in METADATA_TABLES:
        tables.append(dict(table=m, in_v1="yes", reason="metadata the uploader adds (warehouse/redivis/upload.py)", shape="metadata",
                           rows="", first="", last="", interval="", description={"erw_coverage": "warehouse/metadata/coverage.csv: every table, its range, rows, license and sources",
                                                                                 "erw_sources": "warehouse/metadata/sources.csv: the source registry",
                                                                                 "erw_headers": "every provenance header line of every table in the dataset"}[m],
                           license_line="License: public (the ERW's own metadata).", citation=f"Energy Research Warehouse (ERW), table `{m}`, Redivis dataset `{DATASET}`, version v1.",
                           publishers="Energy Research Warehouse (ERW)"))
    return tables, variables_out, missing


def readme(tables, day=PUBLIC_DAY):
    v1 = [t for t in tables if t["in_v1"] == "yes" and t["shape"] != "metadata"]
    out = [t for t in tables if t["in_v1"] == "no"]
    stored = [t for t in tables if t["in_v1"] == "held"]
    stored_names = ", ".join("`" + t["table"] + "`" for t in stored)
    stored_line = (f" {len(stored)} public table{'s' if len(stored) != 1 else ''} ({stored_names}) "
                   f"{'are' if len(stored) != 1 else 'is'} in version 1 by license but not yet in the dataset: {HELD_WHY}") if stored else ""
    by_shape = {}
    for t in v1:
        by_shape[t["shape"]] = by_shape.get(t["shape"], 0) + 1
    return "\n".join([
        "# Energy Research Warehouse (ERW), version 1",
        "",
        "The live, citable record of the US energy system: prices, flows, projects, deals and policy across power, natural gas, oil, nuclear, renewables, "
        "storage and transmission, with the global prices and events that move US markets. Every source is reshaped into three standard table shapes "
        "so that tables can be joined and compared: `series` (one row per observation: entity, variable, ts_utc, value), `entities` (one row per "
        "physical or corporate thing) and `events` (one row per deal, filing or announcement). Timestamps are UTC; power is MW and prices are USD per "
        "MWh unless a `unit` column says otherwise. The data standard: https://github.com/SamuelEnrique/erw/blob/main/docs/datastandard.md",
        "",
        f"**Version 1 holds {len(v1)} tables** ({', '.join(f'{n} {s}' for s, n in sorted(by_shape.items()))}) and three metadata tables "
        "(`erw_coverage`, `erw_sources`, `erw_headers`). Every table's description is its provenance header: the source report, its address, when "
        "it was retrieved, the method, and its license line.",
        "",
        "## What is not in it",
        "",
        f"{len(out)} tables of the warehouse's public draft are not in version 1: a table whose publisher's terms ask for permission or a license "
        f"that has not been recorded is held from {day} (the ERW's license record, https://github.com/SamuelEnrique/erw/blob/main/docs/licenses.md), "
        "and retired tables and the old members of consolidated tables are not tables of the warehouse. Tables licensed for internal use are never "
        "in this dataset." + stored_line,
        "",
        "## How to cite",
        "",
        "Cite the organization that published the data, then the ERW table and this version. For example:",
        "",
        "> U.S. Energy Information Administration (EIA). Spot prices. Via the Energy Research Warehouse (ERW), table `eia_fuel_spot_prices`, "
        f"Redivis dataset `{DATASET}`, version v1.",
        "",
        "Each table's own citation is in `docs/redivis/release-v1/tables.csv` in the repository.",
        "",
        "## Read it in Python, Stata or R",
        "",
        "The ERW's three packages read this dataset with the same six calls (tables, coverage, fetch, cite, license, standard), the same "
        "column types and the same citation (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/packages.md). Each needs a Redivis "
        "token in `REDIVIS_API_TOKEN`. Install:",
        "",
        "```",
        'pip install "erw-energy[redivis] @ git+https://github.com/SamuelEnrique/erw.git#subdirectory=package"',
        'net install erw, from("https://raw.githubusercontent.com/SamuelEnrique/erw/main/packages/stata/") replace',
        'remotes::install_github("SamuelEnrique/erw", subdir = "packages/r/erw")',
        "```",
        "",
        "Then, for example, Henry Hub's daily price in 2025:",
        "",
        "```",
        'erw.fetch("eia_fuel_spot_prices", entity="eia:henry_hub", start="2025-01-01", end="2026-01-01", backend="redivis")',
        "erw fetch eia_fuel_spot_prices, entity(eia:henry_hub) start(2025-01-01) end(2026-01-01) backend(redivis) clear",
        'erw_fetch("eia_fuel_spot_prices", entity = "eia:henry_hub", start = "2025-01-01", end = "2026-01-01", backend = "redivis")',
        "```",
        "",
        "Each table's own line in each package is in `tables.csv` (`fetch_python`, `fetch_stata`, `fetch_r`).",
        "",
        "## How it is made",
        "",
        "One connector per source pulls, reshapes and validates; the validator is the gate a table passes before upload. Uploads write a draft only; "
        "a version is released by a person after reading what the draft changes. Code, methods and the session reports: "
        "https://github.com/SamuelEnrique/erw",
        "",
        "## Credit",
        "",
        "The Energy Research Warehouse is adapted, with permission, from the infrastructure and documents of the Item Response Warehouse "
        "(github.com/ben-domingue/irw).",
        "",
    ])


# Session 1010 (chain 070): the one line that fetches a table in each package (docs/methods/packages.md, "One line a table")
FETCH = {"fetch_python": 'erw.fetch("{t}")', "fetch_stata": "erw fetch {t}, clear", "fetch_r": 'erw_fetch("{t}")'}
COLS = ["table", "in_v1", "reason", "shape", "rows", "first", "last", "interval", "description", "license_line", "citation",
        "publishers", *FETCH]


def with_calls(t):
    """A tables.csv row with its fetch lines; a metadata table's are empty (it is read as any table, by its name)."""
    return {**t, **{k: (v.format(t=t["table"]) if t.get("shape") != "metadata" else "") for k, v in FETCH.items()}}


def calls_only(docs=DOCS):
    """Session 1010: the README written again and the fetch columns added, from tables.csv as it is (no table read)."""
    tables = rows(os.path.join(docs, "tables.csv"))
    out = [with_calls({k: t.get(k, "") for k in COLS[:12]}) for t in tables]
    with open(os.path.join(docs, "tables.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    with open(os.path.join(docs, "README.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(readme(out))
    return out


def write(out_dir, docs=DOCS):
    tables, vars_, missing = build(out_dir)
    tables = [with_calls(t) for t in tables]   # session 1010
    os.makedirs(docs, exist_ok=True)
    with open(os.path.join(docs, "tables.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(tables)
    with open(os.path.join(docs, "variables.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["table", "name", "kind", "unit"], lineterminator="\n")
        w.writeheader()
        w.writerows(vars_)
    with open(os.path.join(docs, "README.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(readme(tables))
    return tables, vars_, missing


def check(docs=DOCS):
    """The written list against today's plan: the same tables, the same in_v1. Returns the problems."""
    have = {r["table"]: r["in_v1"] for r in rows(os.path.join(docs, "tables.csv"))}
    want = {t: v for t, v, _ in plan()} | {m: "yes" for m in METADATA_TABLES}
    return [f"{t}: tables.csv says {have.get(t)}, the record says {want.get(t)}" for t in sorted(set(have) | set(want)) if have.get(t) != want.get(t)]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", default=os.path.join(ROOT, "warehouse", "output"), help="the folder that holds the tables")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--target", choices=["stanford"], help="session 664: the package for the Stanford dataset "
                                                          "(docs/redivis/release-v1-stanford/)")
    ap.add_argument("--calls-only", action="store_true", help="session 1010: the README and the fetch columns, from tables.csv")
    a = ap.parse_args(argv)
    if a.target:
        use_stanford()
    if a.calls_only:
        out = calls_only(DOCS)
        print(f"{os.path.relpath(DOCS, ROOT)}: README.md written again; tables.csv has the fetch lines of {len(out)} tables")
        return 0
    where = os.path.relpath(DOCS, ROOT).replace(os.sep, "/")
    if a.check:
        bad = check(DOCS)
        for b in bad:
            print(b)
        print(f"release v1: {len(bad)} difference(s) between {where}/tables.csv and the license record")
        return 1 if bad else 0
    tables, vars_, missing = write(a.out_dir, DOCS)
    v1 = sum(1 for t in tables if t["in_v1"] == "yes")
    print(f"{where}: {v1} tables in v1 (with the three metadata tables), {len(tables) - v1} public tables held out; "
          f"{len(vars_)} variables and columns; written {dt.datetime.now(dt.timezone.utc):%Y-%m-%dT%H:%MZ}")
    for t in missing:
        print(f"MISSING: {t} is in v1 but not in {a.out_dir}: its variables are not listed")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
