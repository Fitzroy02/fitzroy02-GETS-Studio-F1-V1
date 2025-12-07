# 📜 Platform Content Sharing Policy

**GETS Studio - Civic Media Platform**  
**Version:** 1.0  
**Effective Date:** December 7, 2025

---

## 🎯 Purpose

To ensure all material aired on the platform aligns with civic stewardship, ecological anchors, and contributor empowerment — while protecting originality and platform integrity.

---

## 📚 Libraries & Categories

### Music Library
- **Accepted content**: Music tracks and music videos
- **Length requirement**: Minimum 1 minute, maximum 10 minutes
- **Format**: MP4 or equivalent with clear audio and video
- **Metadata required**: 
  - Genre
  - Description
  - Author notes
  - Tags
- **Feedback enabled**: Likes/dislikes tracked

### Podcast & Radio Library
- **Accepted content**: Spoken-word content (podcasts, radio shows, civic dialogues)
- **Format**: MP3 or equivalent audio format
- **Metadata required**:
  - Genre
  - Description
  - Author notes
  - Tags
- **Feedback enabled**: Likes/dislikes tracked

---

## 🎵 Music Video Rules

- **Length**: Must be between 1 and 10 minutes
- **Format**: MP4 or equivalent, with clear audio and video
- **Metadata**: Genre, description, author notes, tags (all required)
- **Example**: A 1-minute ambient track is fully compliant

---

## 🚫 External Sharing Restriction

**CRITICAL RULE: No other platform's material may be aired here.**

- All content must be **originally submitted to this platform** with full metadata
- This ensures integrity, avoids licensing conflicts, and keeps governance rehearsal focused on civic stewardship
- Contributors retain copyright but grant platform broadcast rights
- Content cannot be simultaneously featured as "exclusive" on competing platforms

---

## ⚖️ Governance & Fairness

### Representation Requirements
- **Minimum 25%** of slots reserved for *impact* or *civic* tagged content
- **Minimum 10%** of slots reserved for *ecological* tagged content
- Priority scoring ensures high-priority civic campaigns get fair airtime

### Feedback Loop
- Likes/dislikes tracked per library item
- Community feedback influences future scheduling recommendations
- All feedback exported with allocation data for transparency

### Audit Trail
- All content appears in CSV/JSON exports with complete metadata
- Campaign-to-content linkage preserved in all reports
- Timestamped exports provide immutable record

---

## 🌱 Ecological Anchors

Every piece of content carries ecological metadata:

### Impression-Based Impact
- **Trees planted** per 1,000 impressions
- **Ocean restoration score** per 1,000 impressions
- Set by campaign when linking to content

### Currency-Based Impact
- **Trees bucket**: £1 allocated → 0.1 trees planted (configurable)
- **Oceans bucket**: £1 allocated → 0.05 ocean score (configurable)
- Conversion rates set in `EcoRates` configuration

### Dual Methodology
Total ecological impact = Impression-based + Currency-based allocations

---

## 📊 Exports & Transparency

### CSV Exports
**allocations_detailed.csv**:
- Per-slot allocations with canonical bucket order
- Metadata columns: genre, description, author_notes, tags, likes, dislikes
- Sorted by datetime then channel (TV → Radio → Online)

**allocations_daily.csv**:
- Wide format with buckets as columns
- One row per day for easy spreadsheet analysis

**allocations_campaign.csv**:
- Revenue distribution per campaign and stakeholder

### JSON Exports
**complete_summary.json**:
- Campaign spend and slot counts
- Daily and campaign allocation totals (canonical bucket order)
- Ecological impact summary
- **Library metadata section** with complete content details
- ISO timestamps for audit compliance

### Audit Compliance
- Contributors can review both financial numbers and creative context
- Stakeholders can verify ecological impact claims
- Broadcasters can demonstrate fairness policy compliance

---

## 📋 Content Submission Requirements

### Required Metadata
All submissions must include:
1. **Name**: Content title (required)
2. **Genre**: Category/style (required)
3. **Description**: Public-facing summary (required)
4. **Author Notes**: Behind-the-scenes context (required)
5. **Tags**: Categorization keywords (at least one, use civic/impact/ecological where applicable)

### Optional Metadata
- Ecological impact rates (trees/oceans per 1000 impressions)
- Channel preferences for campaign scheduling
- Target audience information

### Prohibited Content
- Material exclusively featured on competing platforms
- Content without complete metadata
- Music videos shorter than 1 minute or longer than 10 minutes
- Content that violates copyright or licensing agreements

---

## 🔄 Content Lifecycle

1. **Submission**: Contributor uploads content with complete metadata
2. **Review**: Platform validates format, length, and metadata completeness
3. **Library Addition**: Content added to appropriate library (Music or Podcast)
4. **Campaign Linking**: Campaigns can link to library items for scheduling
5. **Broadcasting**: Content aired according to multi-channel scheduler
6. **Feedback Collection**: Community likes/dislikes tracked in real-time
7. **Impact Reporting**: Ecological and financial impact exported regularly

---

## 💰 Revenue Allocation

All advertising revenue distributed via canonical stakeholder buckets:

1. **Broadcaster** (typically 60-75%): Platform operations and reinvestment
2. **Centre** (typically 15-30%): Direct funding to GETS Community Centre
3. **Trees** (typically 5-8%): Tree planting initiatives
4. **Oceans** (typically 2-5%): Ocean cleanup and restoration

Per-campaign allocation policies allow flexibility while maintaining transparency.

---

## ✅ Summary

- **Music**: 1-10 minutes only, full metadata required
- **Podcasts/Radio**: Spoken-word content with full metadata
- **No external platform sharing** — all content must originate here
- **Fairness enforced**: 25% civic, 10% ecological minimum representation
- **Ecological anchors**: Dual methodology tracks real environmental impact
- **Full transparency**: CSV and JSON exports include all metadata and feedback
- **Canonical ordering**: Consistent bucket order (broadcaster → centre → trees → oceans) in all reports

---

## 📞 Contact & Governance

Questions about this policy? Contact the GETS Studio governance team.

For technical implementation details, see:
- `CANONICAL_ORDERING.md` - Sorting and bucket order specifications
- `ARCHITECTURE_QUICK_REFERENCE.md` - Platform architecture overview
- `library.py` - Content library implementation
- `ad_scheduler_advanced.py` - Scheduling and allocation system

---

**This makes GETS Studio a closed civic-creative ecosystem**: Contributors bring their own work, it's governed by clear rules, and everything is auditable with ecological anchors.
