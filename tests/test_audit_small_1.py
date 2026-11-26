"""Session 10238, the small pages' audit, finding 1 (docs/reviews/small-pages-audit-2026-11-26.md): /subscribe said "The
public site can add an address but cannot read one back; only the warehouse's own service key can." Since migration 034
(session 301) the site's server writes every sign-up with the service key, and the suppression list is stored too."""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class TheCode(unittest.TestCase):
    def test_the_site_writes_a_sign_up_with_the_service_key(self):
        sup = src("site", "lib", "supabase.ts")
        insert = sup.split("export async function insertRow", 1)[1].split("\n}\n", 1)[0]
        self.assertIn("writeConfig()", insert)
        self.assertIn("SUPABASE_SERVICE_KEY", sup)
        self.assertIn('insertRow("subscribers"', src("site", "app", "api", "subscribe", "route.ts"))
        m034 = src("warehouse", "supabase", "migrations", "034_server_writes.sql")
        self.assertIn("revoke insert on public.subscribers from anon, authenticated;", m034)

    def test_an_unsubscribed_address_is_kept_on_a_suppression_list(self):
        m007 = src("warehouse", "supabase", "migrations", "007_subscriber_confirm.sql")
        self.assertIn("insert into public.email_suppressions (email)", m007)


class ThePage(unittest.TestCase):
    def page(self):
        return re.sub(r"\s+", " ", src("site", "app", "subscribe", "page.tsx"))

    def test_the_page_no_longer_says_the_site_cannot_read_an_address(self):
        self.assertNotIn("The public site can add an address but cannot read one back", self.page())

    def test_the_page_says_what_writes_and_what_is_kept(self):
        p = self.page()
        self.assertIn("writes the address with the warehouse&apos;s service key, which can read the table and which no browser is given", p)
        self.assertIn("kept on a suppression list, so that it is never emailed again", p)


if __name__ == "__main__":
    unittest.main()
