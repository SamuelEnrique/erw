# Draft: asking the Virginia SCC for permission to read docket documents programmatically

Written by session 172 (10 October 2026) for Samuel to send himself, from his own address. Nothing here was sent. The commission's Contact page lists the Clerk's Office and the webmaster; the draft names neither address, so that the right one is chosen by hand. Fill the two bracketed items first.

Why it is needed: the commission's robots file (`https://www.scc.virginia.gov/robots.txt`) ends with `User-agent: *` and `Disallow: /`, so every automated request of the site is disallowed for an agent it does not name. The ERW stopped every request of the commission on 9 October 2026 after reading it (`docs/methods/vascc_pause.md`), and asks nothing of the site until the commission answers or a person rules.

---

**Subject:** Permission to read public docket documents by script, for an academic research project

Dear Clerk's Office,

I am writing to ask for the commission's permission to read a small number of public docket documents from the Docket Search programmatically, for an academic research project.

I am [name, role and affiliation]. The project is the Energy Research Warehouse, an open, non-commercial research dataset on the US energy system (its code and documentation are public at github.com/SamuelEnrique/erw). One part of it follows how state regulators are treating large new electricity loads, such as data centers. Virginia's record is central to that work, in particular case PUR-2026-00011 (Virginia Electric and Power Company's large-load connection queue process standards) and a handful of related large-load cases.

Your robots.txt disallows automated requests of the site for agents it does not name. We read it on 9 October 2026 and stopped every automated request at once; nothing has been requested since. Before that, from 8 October, a daily script had read the Docket Search's public case list and document list (about 10 to 20 small requests a day). We would like to resume only with your permission.

What we are asking to do, if you allow it:

- Read the Docket Search's public case list and document list for about ten named large-load cases, and the public PDF filings in them, once a day at most.
- Send at most 120 requests a day in all, never more than one request every 2.5 seconds, from one process, with a User-Agent that identifies the project ("ERW research project, github.com/SamuelEnrique/erw").
- Keep a copy of each document so that no document is requested twice.
- Publish only what the project computes from the documents (case numbers, filing dates, document titles, and aggregate figures such as how long a stage of the queue takes), with attribution to the commission and a link to the docket. We would not republish the documents themselves.

If a different rate, a different time of day, or a bulk download or API is preferable to you, we will follow whatever you specify. If the commission would rather we did not read the site by script at all, we will keep to the links and to documents downloaded by hand, as we do now.

Thank you for considering this, and for the public record the commission keeps.

Kind regards,

[name]
[affiliation and postal address]
