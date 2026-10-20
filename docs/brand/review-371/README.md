Session 371, 20 October 2026: the four internal pages that now open with the internal view's cookie alone (docs/security.md, S2), at 1280 and 390.
Before: production (https://erw-flame.vercel.app), the internal view opened by the form, no token in the address: each page answered "No page at this address".
After: the local build of wip/371-docs-security, the same cookie and no token: each page opens as it did with ?token= (the finder and the lease loader without their internal data, which this machine does not hold).
