"""The ten email topics (session 23), mapped from the news scorer's sectors (warehouse/news/score.py SECTORS).

The same map is in site/lib/topics.ts (the /subscribe checkboxes). email_digest.py filters each subscriber's top
stories to the topics they chose; the website digest stays complete. The scorer's "other" stays unmapped (human
ruling, session 23: stories scored other stay other), so it reaches only the full email.
"""

TOPICS = {
    "power_prices": ("Power prices", ["power_prices", "generation"]),
    "gas_lng": ("Gas and LNG", ["gas", "lng"]),
    "oil": ("Oil", ["oil", "transport"]),
    "nuclear": ("Nuclear", ["nuclear"]),
    "renewables_storage": ("Renewables and storage", ["renewables", "storage", "hydrogen"]),
    "transmission_grid": ("Transmission and grid", ["transmission", "interconnection", "grid_conditions"]),
    "datacenters_ai": ("Datacenters and AI power", ["datacenter_power"]),
    "deals_capital": ("Deals and capital", ["deal", "ppa", "capital", "company"]),
    "policy": ("Policy", ["policy"]),
    "geopolitics": ("Geopolitics", ["geopolitics"]),
}
ALL = list(TOPICS)
SECTOR_TOPIC = {sec.replace("_", " "): t for t, (_, secs) in TOPICS.items() for sec in secs}


def topic_of(sector_label):
    """The topic of a sector as the brief prints it ("power prices", "datacenter power"); None for other."""
    return SECTOR_TOPIC.get((sector_label or "").strip().replace("_", " "))
