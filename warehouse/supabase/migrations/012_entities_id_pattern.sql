-- Energy Research Warehouse (ERW): Supabase live set, migration 012 (session 37).
--
-- The grid pages read each ISO's queue positions from energy_projects with entity_id like '<iso>_queue:%'
-- (site/lib/grid.ts). Under the database's en_US.UTF-8 collation the primary key cannot serve a prefix LIKE, so each
-- read filtered every energy_projects row: 1.8 s warm, and over the anon role's 3 s statement timeout when a build
-- renders the seven grid pages at once (sessions 36C and 37: "canceling statement due to statement timeout"). An index
-- with text_pattern_ops turns the prefix into a range. Idempotent; drop the index to undo.

create index if not exists entities_id_pattern on public.entities (table_name, entity_id text_pattern_ops);
