"""Window D's data request 51 (c): on the live set, a count only (no row read out): game_scores rows (check false) for which
a game_plays row has the same level_date, preset and score and a ts within 120 seconds. Read only over SUPABASE_DB_URL."""
import psycopg

url = None
for ln in open(".env", encoding="utf-8"):
    if ln.startswith("SUPABASE_DB_URL="):
        url = ln.split("=", 1)[1].strip().strip('"')
con = psycopg.connect(url, connect_timeout=30)
con.read_only = True
cur = con.cursor()
for t in ("game_scores", "game_plays"):
    cur.execute("select column_name from information_schema.columns where table_name = %s order by ordinal_position", (t,))
    print(t, [r[0] for r in cur.fetchall()])
cur.execute("select count(*) from game_scores where coalesce(\"check\", false) = false")
print("game_scores, check false:", cur.fetchone()[0])
cur.execute("select count(*) from game_plays")
print("game_plays:", cur.fetchone()[0])
cur.execute("""select count(*) from game_scores s where coalesce(s."check", false) = false and exists (
                 select 1 from game_plays p where p.level_date = s.level_date and p.preset is not distinct from s.preset
                 and p.score = s.score and abs(extract(epoch from (p.ts - s.ts))) <= 120)""")
print("matched within 120 s:", cur.fetchone()[0])
con.close()
