// Energy Research Warehouse (ERW) site, session 150: made-up answers of the two providers added beside PitchBook, for
// scripts/test-thesis-providers.mjs, scripts/check-thesis.mjs and the stand-in scripts/thesis-stub.mjs.
//
// THE ANSWERS BELOW ARE A FIXTURE. Every company, person, investor, figure, date and address in them is made up for
// the test and is no company's: nothing here was returned by Harmonic or by Crunchbase (no connector was ever called),
// nothing here is data of the warehouse, and none of it is ever loaded, published or shown on the site. They follow
// the rule session 135 set for its own paste fixtures (scripts/thesis-stub.mjs): names that say they are examples.
//
// They are shaped to exercise the readers: a documented field with its documented shape, a documented field with
// another shape (kept as given, not mapped), a field no documentation names (kept as given, not mapped), a company
// that was not found, and values that agree and disagree with the PitchBook fixture of scripts/thesis-stub.mjs
// (Example Storage Inc.: total raised USD 18 million, founded 2019, 42 employees, Austin, TX, two founders).

export const RUN = "fixture-done";

export function harmonicAnswer(runId = RUN) {
  return {
    format: "erw-harmonic-1", run_id: runId, pulled_on: "2026-10-07",
    companies: [
      {
        name: "Example Storage Inc.", found: true,
        company: {
          id: 1000001, entity_urn: "urn:fixture:company:1000001", name: "Example Storage", legal_name: "Example Storage, Inc.",
          short_description: "Fixture description from the second provider.", website: { url: "https://www.example.com", domain: "example.com" },
          founding_date: { date: "2019-01-01", granularity: "fixture granularity" }, headcount: 42, ownership_status: "fixture ownership", stage: 7,
          location: { city: "Austin", state: "Texas", country: "United States" },
          funding: {
            funding_total: 18200000, num_funding_rounds: 2, investors: ["Fixture Fund One", "Fixture Fund Two"], last_funding_at: "2025-03-14T00:00:00Z",
            last_funding_type: "fixture round type", last_funding_total: 12500000, valuation_info: { amount: 61000000, source: "fixture source" },
          },
          funding_rounds: [
            { announcement_date: "2023-06-01", funding_round_type: "fixture seed", funding_amount: 5700000, funding_currency: "USD", investors: [{ investor_name: "Fixture Fund Two", is_lead: true }] },
            { announcement_date: "2025-03-14", funding_round_type: "fixture round type", funding_amount: 12500000, funding_currency: "USD", fixture_round_extra: "kept as given",
              investors: [{ investor_name: "Fixture Fund One", is_lead: true }, { investor_name: "Fixture Fund Two", is_lead: false, fixture_investor_extra: 1 }], valuation_info: { amount: 61000000 } },
          ],
          fixture_undocumented_field: { nested: "kept as given" },
        },
        people: [
          { full_name: "A. Fixture", experience: [{ title: "Co-Founder and Chief Executive", company_name: "Example Storage", is_current_position: true }, { title: "Engineer", company_name: "Another Fixture Co", is_current_position: false }] },
          { full_name: "C. Fixture", experience: [{ title: "Cofounder", company_name: "Example Storage Inc.", is_current_position: true }], fixture_person_extra: "kept as given" },
          { full_name: "D. Fixture", experience: [{ title: "Head of Sales", company_name: "Example Storage", is_current_position: true }] },
        ],
        fixture_entry_extra: "kept as given",
      },
      { name: "Sample Grid Co", found: true, company: { name: "Sample Grid Co", headcount: 8, location: { location: "Reno, Nevada, United States" } } },
    ],
    additional_companies: [
      { name: "Harmonic Fixture Later LLC", found: true, why: "Fixture: matched the search words.", company: { name: "Harmonic Fixture Later LLC", headcount: 5, funding: { funding_total: 1500000 } } },
    ],
    saved_searches: [
      { name: "Fixture saved search of companies", of: "companies", results: [{ name: "Saved Fixture Co", record: { name: "Saved Fixture Co", headcount: 12, stage: "fixture stage" } }] },
      { name: "Fixture saved search of investors", of: "investors", results: [{ name: "Fixture Fund Three", record: { type: "fixture investor type", investment_count: 31, check_size_min_usd: 250000, check_size_max_usd: 2000000, fixture_investor_field: "kept as given" } }] },
      { name: "Fixture saved search of people", of: "people", results: [{ name: "E. Fixture", record: { full_name: "E. Fixture", linkedin_headline: "Fixture headline" } }] },
    ],
    fixture_envelope_extra: ["kept", "as", "given"],
  };
}

export function crunchbaseAnswer(runId = RUN) {
  const usd = (value) => ({ value, currency: "USD", value_usd: value });
  return {
    format: "erw-crunchbase-1", run_id: runId, pulled_on: "2026-10-07",
    companies: [
      {
        name: "Example Storage Inc.", found: true,
        organization: {
          identifier: { value: "Example Storage", permalink: "example-storage-fixture", entity_def_id: "organization" }, legal_name: "Example Storage, Inc.",
          short_description: "Fixture description from the third provider.", website_url: "https://www.example.com",
          founded_on: { value: "2018-01-01", precision: "year" }, num_employees_enum: "c_00011_00050", status: "operating",
          location_identifiers: [{ value: "Austin", location_type: "city" }, { value: "Texas", location_type: "region" }, { value: "United States", location_type: "country" }],
          funding_total: usd(18000000), num_funding_rounds: 2, last_funding_at: "2025-03-14", last_funding_type: "series_a", last_funding_total: usd(12500000),
          funding_stage: "early_stage_venture", valuation: "sixty million", valuation_date: "2025-03-14",
          founder_identifiers: [{ value: "A. Fixture" }, { value: "C. Fixture" }], investor_identifiers: [{ value: "Fixture Fund One" }, { value: "Fixture Fund Two" }],
          url: "https://www.example.com/fixture-profile", fixture_undocumented_field: 3,
        },
        cards: {
          founders: [{ identifier: { value: "A. Fixture" }, primary_job_title: "Fixture title" }, { identifier: { value: "C. Fixture" } }],
          raised_funding_rounds: [
            { announced_on: "2025-03-14", investment_type: "series_a", money_raised: usd(12500000), lead_investor_identifiers: [{ value: "Fixture Fund One" }] },
            { announced_on: "2023-06-01", investment_type: "seed", money_raised: { value: 5000000, currency: "EUR" }, lead_investor_identifiers: [{ value: "Fixture Fund Two" }] },
          ],
          fixture_card: [{ identifier: { value: "kept as given" } }],
        },
      },
      { name: "Sample Grid Co", found: false },
    ],
    additional_companies: [
      { name: "Crunchbase Fixture Later LLC", found: true, why: "Fixture: matched the search words.", organization: { identifier: { value: "Crunchbase Fixture Later LLC" }, num_funding_rounds: 1 } },
    ],
  };
}
