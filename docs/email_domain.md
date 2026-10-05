# Verifying a sending domain for the digest and the Roundup

The steps a person takes so that the Energy Research Warehouse (ERW) can email anyone but its owner. Written in session 119 (5 October 2026). Nothing here can be done by a session: it needs the Resend account, a domain's DNS, and GitHub's secrets.

## Where things stand

- Every ERW email goes out through Resend (`warehouse/news/email_digest.py`, `warehouse/news/shadow.py`, `scripts/notify.py`, `scripts/alert.py`), from the address in `DIGEST_FROM`, or, when that is not set, from `ERW Energy Digest <onboarding@resend.dev>`.
- **No domain is verified.** Asked on 5 October 2026, Resend's API lists no domain for this account (`GET /domains`: none), and every email it holds for the account was sent from `onboarding@resend.dev`.
- `onboarding@resend.dev` is Resend's test sender. It delivers to the address of the account that owns the key and to no one else. That is why all 53 emails Resend holds for the ERW went to the one fixed recipient, and why `/subscribe` has no confirmed subscriber the digest could reach: the confirmation email itself cannot be delivered to a stranger. (The limit is Resend's; this session did not test it against a second address.)
- So the digest, the Roundup and the subscription flow are built and tested, and distribution waits on this one thing.

## What you need before you start

1. **A domain whose DNS you control.** `erw-flame.vercel.app` will not do: it is Vercel's, and you cannot add DNS records to it. Any registrar's domain works. If the ERW gets its own site address later, use that domain; the email subdomain does not have to match the site's.
2. **The Resend account** that owns `RESEND_API_KEY`.
3. **Access to the repository's secrets** on GitHub (Settings, Secrets and variables, Actions).

## The steps

Steps 1 to 6 follow Resend's own guide, "Add a domain" (`https://resend.com/docs/add-a-domain`, read on 5 October 2026). The words in quotation marks are Resend's.

1. **In Resend, open Domains and click "Add Domain".**
2. **Enter a subdomain, not the root domain.** For example `mail.<your domain>`. Resend advises "sending emails from a subdomain (e.g., `notifications.example.com`) instead of your root domain", to keep the sending reputation apart from the rest of the domain. Each subdomain is "configured and verified individually".
3. **Choose the region** nearest the readers (for the ERW, a US region).
4. **Leave the Return-Path as Resend proposes** (it defaults to `send` under your subdomain) unless you have a reason to change it.
5. **Add the DNS records Resend shows you, at the company that hosts the domain's DNS.** "Copy and paste the records to avoid configuration errors." Resend lists them on the domain's Records tab. They are of these kinds:
   - an **SPF** record (a TXT record): which servers may send for the subdomain;
   - a **DKIM** record (a TXT record at a host name like `resend._domainkey`): the signature that proves an email is yours;
   - an **MX** record for the Return-Path host: where bounces go;
   - **DMARC** (a TXT record at `_dmarc`), optional, after the domain is verified: what a receiver should do with mail that fails the first two.
   If the DNS is at Cloudflare, do not proxy these records (no orange cloud).
6. **Wait for "Verified".** Resend says domains typically "verify within 15 minutes", and that "DNS changes can occasionally take up to 72 hours to propagate globally". If it has not verified after 72 hours, use "Restart verification" on the domain's page.
7. **Set the sender.** In GitHub's repository secrets, set `DIGEST_FROM` to an address on the verified subdomain, with a name:

   ```
   ERW Energy Digest <digest@mail.<your domain>>
   ```

   The three workflows that send (`daily-prices.yml`, `roundup.yml`, `chain-watch.yml`) already read `DIGEST_FROM`. Put the same line in `.env` on each machine, so that the session emails (`scripts/notify.py`, `scripts/alert.py`) use it too.
8. **Check it, without sending a digest.** On a machine with the new `.env`:

   ```bash
   python scripts/alert.py send --subject "ERW: a test from the verified domain" --line "If this arrived from the new address, the domain works."
   ```

   The email should arrive from the new address, and Resend's Emails page should show it "delivered". This goes to the fixed recipients only, never to a subscriber.
9. **Then, and only then, test a stranger's address.** Subscribe a second address of your own on `/subscribe`, confirm it from the email, and wait for the next weekday digest (14:00 UTC run). The send-once guard (`digest_sends`) keeps a day's digest from going out twice whatever you do.

## What does not change

- The send-once guard, the unsubscribe link in every email, the suppression list and the double opt-in are all as they are. Verifying a domain changes who can be reached, not what is sent.
- `DIGEST_RECIPIENTS` stays the fixed list. Subscribers are read from the site's database only when `EMAIL_SUBSCRIBERS` is `1`, which the two workflows already set.

## If something goes wrong

- **The domain stays "Pending".** One of the records is not public yet, or was typed and not pasted. Compare each record at the DNS host with Resend's Records tab, character for character.
- **Emails are accepted and land in spam.** Add the DMARC record, and give it a few days: a new sending domain has no reputation yet.
- **A send fails with a 403 after the change.** `DIGEST_FROM` names a domain that is not the verified one (a typo, or the root domain where the subdomain was verified).
