"""Window D's data request 50: the live set's load day and first date for ferc_eqr_contracts. Reads only, over
SUPABASE_DB_URL (no write). Prints the catalogue's row for the table and the events rows' loaded_at and event_date span."""
import os

import psycopg

url = None
for ln in open(".env", encoding="utf-8"):
    if ln.startswith("SUPABASE_DB_URL="):
        url = ln.split("=", 1)[1].strip().strip('"')
con = psycopg.connect(url, connect_timeout=30)
con.read_only = True
cur = con.cursor()
cur.execute("select column_name from information_schema.columns where table_name = 'catalogue' order by ordinal_position")
cols = [r[0] for r in cur.fetchall()]
print("catalogue columns:", cols)
cur.execute("select * from catalogue where table_name = 'ferc_eqr_contracts'" if "table_name" in cols else
            "select * from catalogue where name = 'ferc_eqr_contracts'")
for r in cur.fetchall():
    print(dict(zip(cols, r)))
cur.execute("select column_name from information_schema.columns where table_name = 'events'")
ecols = [r[0] for r in cur.fetchall()]
tcol = "table_name" if "table_name" in ecols else "tbl" if "tbl" in ecols else None
print("events table column:", tcol)
if tcol:
    cur.execute(f"select count(*), min(event_date), max(event_date), min(loaded_at), max(loaded_at) from events where {tcol} = 'ferc_eqr_contracts'")
    print("rows, first event_date, last event_date, first loaded_at, last loaded_at:", cur.fetchone())
con.close()
