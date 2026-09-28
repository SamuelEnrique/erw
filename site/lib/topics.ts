// Energy Research Warehouse (ERW) site: the ten email topics (session 23), mapped from the news scorer's sectors
// (warehouse/news/score.py SECTORS). The same map is in warehouse/news/topics.py, which filters each subscriber's
// email; the website digest stays complete.
export const TOPICS: { id: string; label: string; sectors: string[] }[] = [
  { id: "power_prices", label: "Power prices", sectors: ["power_prices", "generation"] },
  { id: "gas_lng", label: "Gas and LNG", sectors: ["gas", "lng"] },
  { id: "oil", label: "Oil", sectors: ["oil", "transport"] },
  { id: "nuclear", label: "Nuclear", sectors: ["nuclear"] },
  { id: "renewables_storage", label: "Renewables and storage", sectors: ["renewables", "storage", "hydrogen"] },
  { id: "transmission_grid", label: "Transmission and grid", sectors: ["transmission", "interconnection", "grid_conditions"] },
  { id: "datacenters_ai", label: "Datacenters and AI power", sectors: ["datacenter_power"] },
  { id: "deals_capital", label: "Deals and capital", sectors: ["deal", "ppa", "capital", "company"] },
  { id: "policy", label: "Policy", sectors: ["policy"] },
  { id: "geopolitics", label: "Geopolitics", sectors: ["geopolitics"] },
];
export const TOPIC_IDS = TOPICS.map((t) => t.id);
