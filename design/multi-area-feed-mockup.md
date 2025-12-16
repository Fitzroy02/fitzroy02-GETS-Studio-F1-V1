# Multi-area Feed Mockup & Local Ad Rules

Overview
- Objective: Provide a multi-area content feed UI that can surface multiple geographically-scoped content areas (e.g., national, regional, hyper-local) and enforce local advertising rules before rendering ads.
- Scope: UI mockup, client-side rule enforcement helpers, simple test coverage.

Areas
- global: content/ad content shown to all users
- region: content/ad content targeted to user's region (country/state)
- neighborhood: highly-local content/ad content targeted to small areas (city/zipcode)

Advertising rules (examples)
- Disallowed categories per locale (e.g., gambling restrictions).
- Max frequency per user per ad (e.g., 3 impressions/hour).
- Consent requirements: some locales require explicit consent before showing behavioral ads.
- Language/translation requirements: ads must appear in official locale language(s).

Acceptance criteria
- UI shows separate feed areas stacked or in columns per mockup.
- Ads pass rules check before display; blocked ads show fallback (organic content or placeholder).
- Tests exist for rules enforcement logic.

Design notes
- Use progressive enhancement: ads are validated server-side but client should do a quick pre-check to avoid rendering disallowed content.
- Provide telemetry hooks for blocked ad reasons for ops/analytics.
- Provide mechanism for configurable rules per locale via JSON policy.
