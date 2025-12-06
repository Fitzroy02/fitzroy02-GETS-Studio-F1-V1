#!/usr/bin/env python3
"""
Example usage of the GETS Compliance Studio Governance API
"""

from governance import EmpowermentDashboard

# Initialize the dashboard
print("=" * 60)
print("GETS Compliance Studio - Governance API Demo")
print("=" * 60)

dashboard = EmpowermentDashboard()
print(f"\n{dashboard}\n")

# 1. Toggle visibility mode
print("1. Toggling Visibility Mode")
print("-" * 60)
dashboard.toggle_visibility("local")
print()

# 2. Export summary to CSV
print("2. Exporting Summary")
print("-" * 60)
dashboard.export_summary("summary.csv")
print()

# 3. List all available profiles
print("3. Available Policy Profiles")
print("-" * 60)
profiles = dashboard.list_profiles()
for idx, profile in enumerate(profiles, 1):
    print(f"  {idx}. {profile}")
print()

# 4. Get specific profile details
print("4. Profile Details - UK_OSA_v1")
print("-" * 60)
uk_profile = dashboard.get_profile("UK_OSA_v1")
print(f"  Jurisdiction: {uk_profile['jurisdiction']}")
print(f"  Regulator: {uk_profile['regulator']}")
print(f"  Layer: {uk_profile['layer']}")
print(f"  Max Fine: {uk_profile['penalties']['max_fine']}")
print()

# 5. Check media access for different scenarios
print("5. Media Access Checks")
print("-" * 60)

scenarios = [
    ("video", "UK_OSA_v1", 15),
    ("video", "EU_DSA_v1", 15),
    ("video", "AU_Ban_v1", 15),
    ("book", "MY_OSA_v1", 14),
]

for media_type, profile, age in scenarios:
    access = dashboard.check_media_access(media_type, profile, age)
    status = "✓ ALLOWED" if access['allowed'] else "✗ DENIED"
    print(f"  {status}: {media_type} in {profile} (age {age})")
    print(f"    → {access['reason']}")
print()

# 6. Generate compliance report
print("6. Compliance Report")
print("-" * 60)
report = dashboard.generate_compliance_report(profile_names=["UK_OSA_v1", "EU_DSA_v1", "AU_Ban_v1"])
print(report[['profile', 'jurisdiction', 'layer', 'enforcement_priority', 'max_fine']].to_string(index=False))
print()

# 7. Get media access matrix
print("7. Media Access Matrix")
print("-" * 60)
matrix = dashboard.get_media_matrix()
print(matrix.to_string(index=False))
print()

# 8. Get resolution rules
print("8. Jurisdiction Resolution Rules")
print("-" * 60)
resolution = dashboard.get_resolution_rules()
print(f"  Precedence: {', '.join(resolution['precedence'])}")
print(f"  Conflict Handling: {resolution['conflict_handling']}")
print(f"  VPN Detection: {resolution['vpn_detection']}")
print(f"  Default Profile: {resolution['default_profile']}")
print()

# 9. Get audit configuration
print("9. Audit Configuration")
print("-" * 60)
audit = dashboard.get_audit_config()
print(f"  Enabled: {audit['enabled']}")
print(f"  Retention: {audit['retention']}")
print(f"  Logged Fields: {', '.join(audit['fields'])}")
print()

# 10. Export in different formats
print("10. Multi-Format Export")
print("-" * 60)
dashboard.export_summary("compliance_summary.json", format="json")
dashboard.export_summary("compliance_summary.yaml", format="yaml")
print()

print("=" * 60)
print("Demo Complete!")
print("=" * 60)
