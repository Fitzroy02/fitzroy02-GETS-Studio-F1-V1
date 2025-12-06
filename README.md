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

```bash
git clone https://github.com/Fitzroy02/fitzroy02-GETS-Studio-F1-V1.git
cd fitzroy02-GETS-Studio-F1-V1
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The app will open in your default browser at `http://localhost:8501`

3. Navigate through pages:
   - **Home:** Policy profile overview
   - **Jurisdiction Resolution:** Signal-based resolver with simulator
   - **Compliance Monitoring:** Audit logs and transparency reports
   - **Policy Editor:** YAML configuration management
   - **Comparative Analysis:** Cross-jurisdictional regulatory matrix
   - **Media Loader Controls:** Jurisdiction-aware media access governance

## Features

- **Automatic Enforcement:** Zero user choice—compliance applied server-side
- **Multi-Jurisdiction Support:** UK, EU, US, AU, MY, IN, VN with extensible framework
- **Signal Fusion:** IP geolocation, account residency, billing, device locale, carrier
- **Media Loader Governance:** Jurisdiction-aware controls for video, books, scenarios, trailers, podcasts
- **Age-Gating:** Automatic age verification with jurisdiction-specific thresholds
- **Audit Logging:** Timestamped decisions with signal provenance and media access trails
- **Transparency UX:** User notices and appeals without exposing controls
- **Policy Versioning:** Immutable profiles with Git-based governance

## Tech Stack

- **Streamlit** - Governance dashboard framework
- **Python** - Rules engine and signal processing
- **PyYAML** - Policy-as-code configuration
- **Pandas** - Audit log analysis and reporting

## Compliance Profiles

| Profile | Jurisdiction | Regulator | Layer | Key Requirements | Max Penalty |
|---------|-------------|-----------|-------|------------------|-------------|
| UK_OSA_v1 | United Kingdom | Ofcom | Foundation | Child protection (13+), illegal content removal, quarterly reports | 10% global turnover |
| EU_DSA_v1 | European Union | European Commission | Enhanced | 24h takedown SLA, ad transparency, researcher access, 16+ | 6% global revenue |
| US_Federal_v1 | United States | FTC / Congress | Fragmented | COPPA (under 13), Section 230 (partial), deepfake liability (pending) | Varies per violation |
| AU_Ban_v1 | Australia | eSafety Commissioner | Prohibitive | Under-16 social media ban, strict age verification | A$49.5m |
| MY_OSA_v1 | Malaysia | Communications Ministry | Prohibitive | Under-13 ban, under-16 restrictions, platform licensing | Licensing revocation |
| IN_DPDP_v1 | India | IT Ministry | Emerging | Parental consent, DPDP Act compliance, profiling limits | DPDP provisions |
| VN_Cyber_v1 | Vietnam | MIC | Prohibitive | Proactive monitoring, data localization, strict liability | High penalties |
| Strictest_Global_v1 | Global Fallback | Composite | Maximum | 16+, proactive moderation, full transparency, no circumvention | Highest exposure |

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
- **VPN/Proxy:** Fall back to account metadata, reduce confidence score, flag for review
- **Roaming:** Temporary overlay (local content + home privacy baseline, re-eval every 24h)
- **Undetermined:** Apply `Strictest_Global_v1` profile until resolution improves

## Policy Layering Strategy

### Layer Classification
1. **Foundation (UK):** Strong fines, Ofcom oversight, child protection baseline
2. **Enhanced (EU):** Adds scam liability, transparency, researcher access
3. **Fragmented (US):** Reforms narrowing immunity, expanding child safety
4. **Prohibitive (Asia):** Bans, licensing, proactive monitoring, data localization
5. **Maximum (Global Fallback):** Composite strictest requirements when uncertain

### Comparative Dimensions
- **Age Limits:** 13+ (UK) → 16+ (EU/AU) → Bans (AU/MY)
- **Content Moderation:** Reactive (US) → 24h SLA (EU) → Proactive (VN/MY)
- **Transparency:** Quarterly (UK) → Algorithmic (EU) → Regulator audits (Asia)
- **Penalties:** 10% turnover (UK) > 6% revenue (EU) > Fixed caps (AU) > Revocation (MY)

## Governance Workflow

1. Legal/compliance team proposes policy change
2. Create feature branch in Git repository
3. Edit `policy_profiles.yaml` with new requirements
4. Submit pull request with justification + risk assessment
5. Required approvals from legal + compliance + engineering
6. Merge to main → automated deployment pipeline
7. Archive old version, publish changelog for audits

## Media Loader Governance

### Media Types Supported
- **Video:** Age-gated with jurisdiction-specific access rules (disabled in AU for under-16)
- **Books:** Content filtering and researcher access controls
- **Scenarios:** Risk assessments and contributor verification
- **Trailers:** Age-gated promotional content with ad transparency
- **Podcasts:** Child protection and licensing requirements

### Jurisdiction-Specific Controls

| Media Type | UK | EU | US | AU | MY |
|------------|----|----|----|----|-----|
| Video | 13+, parental notice | 16+, ad transparency | 13+, deepfake flagging | Disabled for under-16 | 13+, restricted |
| Books | Child-safe filter | Researcher access | COPPA compliance | Allowed | Licensing required |
| Scenarios | Impact flags | Risk assessment | Liability disclaimer | Disabled for under-16 | Contributor verification |
| Trailers | 13+, parental notice | Ad transparency | Age verification | Disabled | Restricted |
| Podcasts | Child protection | Ad disclosure | COPPA compliance | Disabled for under-16 | Licensing required |

### Access Decision Logic
1. Resolve user's jurisdiction using signal fusion
2. Look up media type rules for jurisdiction profile
3. Check access status (allowed/restricted/disabled)
4. Verify age requirements if applicable
5. Apply additional controls (filters, notices, licensing)
6. Log decision for audit trail
7. Show user-facing notice without exposing jurisdiction logic

## Data Protection

- **Minimal Collection:** Use non-identifying signals (IP, ASN) before requesting documents
- **PII Minimization:** Hash user IDs, avoid storing unnecessary location data
- **Retention Limits:** Audit logs retained 12 months, then anonymized/deleted
- **Transparency:** Users receive notices when rules affect experience
- **Appeals Process:** In-app form with human review, no automated rejections

## Programmatic API

The `governance.py` module provides a Python API for programmatic compliance management:

```python
from governance import EmpowermentDashboard

# Initialize dashboard
dashboard = EmpowermentDashboard()

# Toggle visibility mode
dashboard.toggle_visibility("local")  # global, local, regional

# Export compliance summary
dashboard.export_summary("summary.csv")  # Also supports JSON, YAML

# Get policy profile
uk_profile = dashboard.get_profile("UK_OSA_v1")

# Check media access
access = dashboard.check_media_access("video", "AU_Ban_v1", user_age=15)
# Returns: {'allowed': False, 'reason': 'video is disabled in this jurisdiction', ...}

# Generate compliance report
report = dashboard.generate_compliance_report()

# Get media access matrix
matrix = dashboard.get_media_matrix()
```

### API Methods

- **`toggle_visibility(mode)`** - Set dashboard view mode (global/local/regional)
- **`export_summary(filename, format)`** - Export compliance data (CSV/JSON/YAML)
- **`get_profile(profile_name)`** - Retrieve specific jurisdiction profile
- **`list_profiles()`** - List all available profiles
- **`get_media_rules(media_type, profile)`** - Get media access rules
- **`check_media_access(media_type, profile, age)`** - Validate media access
- **`generate_compliance_report()`** - Generate detailed compliance DataFrame
- **`get_media_matrix()`** - Build media access matrix across jurisdictions
- **`get_resolution_rules()`** - Retrieve jurisdiction resolution configuration
- **`get_audit_config()`** - Get audit logging settings

See `example_usage.py` for complete demonstrations.

### Media Loader API

```python
from loader import MediaLoader

# Initialize loader
loader = MediaLoader()

# Ingest media with author attribution
loader.ingest("video.mp4", author="John T. Hope", pen_name="DJ Fitz")

# Preview ingested items
loader.preview()

# Check jurisdiction-aware access
access = loader.check_access(media_id, "AU_Ban_v1", user_age=15)
# Returns: {'allowed': False, 'reason': 'video is disabled in this jurisdiction', ...}

# Get jurisdiction rules
rules = loader.get_jurisdiction_rules(media_id, "UK_OSA_v1")

# List all ingested items
items = loader.list_ingested()
```

**Supported Media Types:**
- Video (.mp4, .avi, .mov, .mkv, .webm)
- Books (.pdf, .epub, .mobi, .txt, .md)
- Scenarios (.json, .yaml, .yml)
- Trailers (.trailer.mp4, .trailer.mov, or 'trailer' in filename)
- Podcasts (.mp3, .wav, .m4a, .ogg)

**Key Features:**
- Automatic media type detection from file extensions
- Author and pen name attribution
- Unique media ID generation
- Jurisdiction-aware access checks
- Age verification integration

## Configuration Files

- **`policy_profiles.yaml`** - Jurisdiction compliance profiles with requirements and penalties
- **`loader_config.yaml`** - Media type access rules per jurisdiction
- **`governance.py`** - Python API for programmatic compliance management

All configuration files are version-controlled in Git with required approval workflows.

## 📬 Support & Contact

### Issues & Bugs
Please use the repository's **Issues tab** to report bugs, request features, or suggest improvements. Include clear steps to reproduce problems and any relevant logs or screenshots.

### Questions & Discussion
For general questions or design discussions, open a **Discussion thread** in the repo. This helps keep conversations transparent and accessible to all contributors.

### Direct Contact
Maintainers can be reached via the repository's listed contact email or through community channels (Unitarian civic forums, contributor workshops). Use direct contact only for sensitive matters that cannot be shared publicly.

### Contribution Flow
- Fork the repo and create a feature branch
- Submit a pull request with a clear description
- Expect review focused on audit resilience, accessibility, and civic stewardship

## License

See [LICENSE](LICENSE) for details.
