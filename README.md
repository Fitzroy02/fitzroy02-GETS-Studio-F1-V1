# ⚖️ GETS Compliance Studio

A policy-as-code governance platform for jurisdiction-aware social media compliance.

## Purpose

GETS Compliance Studio enforces regional regulatory requirements automatically—without user controls. The system resolves each user's jurisdiction using multi-signal detection (IP, account, billing, device) and applies the appropriate compliance profile server-side.

## Architecture

### Core Components

1. **Policy-as-Code Engine**
   - Versioned YAML profiles for UK OSA, EU DSA, US Federal, AU Ban, MY OSA
   - Immutable, auditable policy definitions
   - Git-based version control with required approvals

2. **Jurisdiction Resolution**
   - Multi-signal detection with weighted precedence
   - Automatic profile assignment (no user selector)
   - VPN detection and fallback handling
   - Stricter-by-default conflict resolution

3. **Audit & Transparency**
   - Regulator-ready decision trails
   - 12-month retention with minimal PII
   - Transparency reports and enforcement stats
   - User appeals workflow

## How to Run

1. Install the requirements

   ```bash
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```bash
   $ streamlit run streamlit_app.py
   ```

3. Navigate through pages:
   - **Home:** Policy profile overview
   - **Jurisdiction Resolution:** Signal-based resolver with simulator
   - **Compliance Monitoring:** Audit logs and transparency reports
   - **Policy Editor:** YAML configuration management

## Features

- **Automatic Enforcement:** Zero user choice—compliance applied server-side
- **Multi-Jurisdiction Support:** UK, EU, US, AU, MY with extensible framework
- **Signal Fusion:** IP geolocation, account residency, billing, device locale, carrier
- **Audit Logging:** Timestamped decisions with signal provenance
- **Transparency UX:** User notices and appeals without exposing controls
- **Policy Versioning:** Immutable profiles with Git-based governance

## Tech Stack

- **Streamlit** - Governance dashboard framework
- **Python** - Rules engine and signal processing
- **PyYAML** - Policy-as-code configuration
- **Pandas** - Audit log analysis and reporting

## Compliance Profiles

| Profile | Jurisdiction | Regulator | Key Requirements | Max Penalty |
|---------|-------------|-----------|------------------|-------------|
| UK_OSA_v1 | United Kingdom | Ofcom | Child protection (13+), illegal content removal, quarterly reports | 10% global turnover |
| EU_DSA_v1 | European Union | European Commission | 24h takedown SLA, ad transparency, researcher access, 16+ | 6% global revenue |
| US_Federal_v1 | United States | FTC / Congress | COPPA (under 13), Section 230 (partial), deepfake liability (pending) | FTC enforcement |
| AU_Ban_v1 | Australia | eSafety Commissioner | Under-16 social media ban, strict age verification | A$49.5m |
| MY_OSA_v1 | Malaysia | Communications Ministry | Under-13 ban, under-16 restrictions, platform licensing | Council enforcement |

## Resolution Logic

### Signal Precedence
1. Account residency (verified via KYC)
2. Billing country (payment method BIN)
3. IP geolocation (MaxMind/IPinfo)
4. Device locale (OS settings)

### Conflict Handling
- Apply **stricter** profile when signals differ
- Example: UK resident in US → Apply UK OSA (stricter child protection)
- Default to `strictest_global` if signals insufficient

### Edge Cases
- **VPN/Proxy:** Fall back to account metadata, reduce confidence score
- **Roaming:** Temporary overlay (local content + home privacy)
- **Undetermined:** Apply strictest profile, prompt optional verification

## Governance Workflow

1. Legal/compliance team proposes policy change
2. Create feature branch in Git repository
3. Edit `policy_profiles.yaml` with new requirements
4. Submit pull request with justification + risk assessment
5. Required approvals from legal + compliance + engineering
6. Merge to main → automated deployment pipeline
7. Archive old version, publish changelog for audits

## Data Protection

- **Minimal Collection:** Use non-identifying signals (IP, ASN) before requesting documents
- **PII Minimization:** Hash user IDs, avoid storing unnecessary location data
- **Retention Limits:** Audit logs retained 12 months, then anonymized/deleted
- **Transparency:** Users receive notices when rules affect experience
- **Appeals Process:** In-app form with human review, no automated rejections

## License

See [LICENSE](LICENSE) for details.
