// Energy Research Warehouse (ERW) site, session 502: the ERW tables each view of the Grid tool reads, for its license line
// (components/tool/TableLicenses.tsx). Each list is what scripts/page_tables.py finds in the components the view draws
// (app/grid/page.tsx) and lib/grid.ts's load where the view calls it; tests/test_session502.py reads them again from the
// code and fails when a list and the code part.
import type { GridView } from "@/lib/gridtool";

const NETWORK = ["ba_supply_monthly", "caiso_battery_storage", "carbon_intensity_daily", "carbon_intensity_hourly", "eia930_all_demand",
  "eia930_all_generation", "eia930_all_interchange", "eia930_all_storage", "eia930_daily_demand", "eia930_daily_interchange",
  "eia930_event_hourly_interchange"];

export const GRID_VIEW_TABLES: Record<GridView, readonly string[]> = {
  network: NETWORK,
  mix: ["caiso_battery_storage", "caiso_grid_emergencies", "caiso_reliability_daily", "carbon_intensity_daily", "carbon_intensity_hourly",
    "carbon_intensity_monthly", "clean_energy_hourly", "clean_energy_summary", "datacenter_facilities", "eia930_all_demand",
    "eia930_all_generation", "eia930_all_interchange", "eia930_generation_latest", "energy_projects", "generation_mix_hourly_profile",
    "generation_mix_records", "grid_stress_yearly", "known_data_faults", "news_index", "price_board_latest", "price_board_peak_offpeak",
    "state_generation_mix_monthly", "storage_capacity", "storage_daily_cycle"],
  clean: ["caiso_battery_storage", "caiso_grid_emergencies", "caiso_reliability_daily", "carbon_intensity_daily", "carbon_intensity_hourly",
    "carbon_intensity_monthly", "clean_energy_hourly", "clean_energy_summary", "datacenter_facilities", "eia930_all_demand",
    "eia930_all_emissions", "eia930_all_generation", "eia930_generation_latest", "energy_projects", "generation_mix_hourly_profile",
    "generation_mix_records", "grid_stress_yearly", "known_data_faults", "news_index", "price_board_latest", "price_board_peak_offpeak",
    "state_generation_mix_monthly", "storage_capacity", "storage_daily_cycle"],
  gravity: NETWORK,
};
