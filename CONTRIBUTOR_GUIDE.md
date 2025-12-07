# 🚀 Contributor Quickstart Guide

**GETS Studio - Civic Media Platform**  
**For Content Creators & Community Contributors**

---

## Welcome!

Thank you for contributing to GETS Studio — a civic media platform where your creative work directly supports community initiatives and ecological restoration. This guide will help you submit your content and understand how it creates real-world impact.

---

## 📋 Before You Start

### What You Can Submit
✅ **Music** (tracks or videos, 1-10 minutes)  
✅ **Podcasts** (spoken-word content, any reasonable length)  
✅ **Radio Shows** (civic dialogues, interviews, discussions)

### What You Cannot Submit
❌ Content exclusive to other platforms  
❌ Material without complete metadata  
❌ Music videos under 1 minute or over 10 minutes  
❌ Copyrighted material you don't own

---

## 🎵 Step 1: Prepare Your Content

### Music & Music Videos
- **Format**: MP4 (video) or MP3 (audio only)
- **Length**: Between 1 and 10 minutes
- **Quality**: Clear audio and video (if applicable)
- **Example**: 1-minute ambient track ✅ | 15-minute live set ❌

### Podcasts & Radio Shows
- **Format**: MP3 or equivalent audio format
- **Length**: Any reasonable length (typically 5-60 minutes)
- **Quality**: Clear spoken audio, minimal background noise
- **Example**: 30-minute civic dialogue ✅

---

## 📝 Step 2: Gather Your Metadata

All submissions require **complete metadata**. Here's what you need:

### Required Fields

1. **Name** (Content Title)
   - Example: "Static Motion Track" or "Civic Dialogue Podcast"
   - Keep it clear and descriptive

2. **Genre**
   - Music: Ambient, Electronic, Folk, Jazz, etc.
   - Podcasts: Documentary, Interview, Civic Dialogue, Educational, etc.

3. **Description** (Public-facing summary)
   - 1-3 sentences explaining what this content is
   - Example: "Slow tempo, static motion piece for background use"

4. **Author Notes** (Behind-the-scenes context)
   - Share your creative process or production details
   - Example: "Designed to anchor calm presence in civic broadcasts"

5. **Tags** (Keywords for categorization)
   - **Required**: At least one tag
   - **Important tags for priority scheduling**:
     - `civic` - Content related to community governance
     - `impact` - Content with social impact focus
     - `ecological` - Content about environmental topics
   - Other tags: `music`, `podcast`, `education`, `local`, etc.
   - Example: `["impact", "music"]` or `["civic", "ethics"]`

---

## 📤 Step 3: Submit Your Content

### Using Python API (Technical Contributors)

```python
from library import LibraryItem

# Create your library item
my_content = LibraryItem(
    name="My Awesome Track",
    genre="Ambient",
    description="A peaceful soundscape for mindful listening",
    author_notes="Recorded in one take using analog synthesizers",
    tags=["music", "impact"]
)

# Your content is now ready to be linked to campaigns
```

### Using Web Interface (Coming Soon)
1. Log in to GETS Studio dashboard
2. Navigate to "Submit Content"
3. Upload your file (MP4/MP3)
4. Fill in all metadata fields
5. Review and submit

---

## 🔗 Step 4: Link to Campaigns

Once your content is in the library, it can be linked to advertising campaigns:

```python
from ad_scheduler_advanced import AdCampaign

campaign = AdCampaign(
    name="Community Tree Planting",
    # ... other campaign details ...
    library_item=my_content  # Link your content here
)
```

Campaigns that use your content will:
- Track how many times it airs
- Record community feedback (likes/dislikes)
- Generate ecological impact based on impressions
- Distribute revenue according to stakeholder allocations

---

## 📊 Step 5: Track Your Impact

### Community Feedback
Your content automatically tracks:
- **Likes**: Community members who enjoyed your work
- **Dislikes**: Feedback for improvement

Access feedback through:
```python
my_content.add_like()        # When someone likes it
my_content.add_dislike()     # When someone dislikes it
summary = my_content.summary()  # View current stats
```

### View in Exports

Your content metadata appears in all platform exports:

**CSV Export** (`allocations_detailed.csv`):
```csv
datetime,channel,campaign,impressions,total_spend,broadcaster,centre,trees,oceans,genre,description,author_notes,tags,likes,dislikes
2025-12-07T19:00,TV,Tree Campaign,50000,500,350,100,30,20,Ambient,"Peaceful soundscape","Analog synths","music, impact",5,0
```

**JSON Export** (`complete_summary.json`):
```json
{
  "library_metadata": {
    "Tree Campaign": {
      "name": "My Awesome Track",
      "genre": "Ambient",
      "description": "Peaceful soundscape for mindful listening",
      "author_notes": "Recorded in one take using analog synthesizers",
      "tags": "music, impact",
      "likes": "5",
      "dislikes": "0"
    }
  }
}
```

---

## 🌱 Understanding Your Ecological Impact

### How Impact is Calculated

Your content generates real environmental impact through **two methods**:

1. **Impression-Based Impact**
   - Set per campaign: e.g., 2.5 trees planted per 1,000 views
   - Example: 50,000 impressions = 125 trees planted

2. **Currency-Based Impact**
   - Revenue allocated to "trees" and "oceans" buckets
   - Conversion: £1 in trees bucket = 0.1 trees planted
   - Example: £30 to trees = 3 additional trees

**Total Impact = Impression Impact + Currency Impact**

### Example Impact Report
```
Campaign: Community Tree Planting
Content: My Awesome Track
Slots: 12
Impressions: 600,000
Trees Planted: 1,500 (impression) + 24 (currency) = 1,524 trees
Ocean Restoration: 720 (impression) + 8 (currency) = 728 score
```

---

## 💰 Revenue Distribution

When your content airs, ad revenue is distributed through **canonical buckets**:

| Bucket | Typical % | Purpose |
|--------|-----------|---------|
| **Broadcaster** | 60-75% | Platform operations & reinvestment |
| **Centre** | 15-30% | Direct funding to GETS Community Centre |
| **Trees** | 5-8% | Tree planting initiatives |
| **Oceans** | 2-5% | Ocean cleanup & restoration |

You can see exact allocations in exported reports. Every campaign may have slightly different percentages based on its specific civic focus.

---

## ⚖️ Fairness & Governance

### Priority Scheduling
Content tagged with `civic`, `impact`, or `ecological` gets scheduling priority:
- **25% minimum** of all slots reserved for civic/impact content
- **10% minimum** for ecological content
- Higher priority campaigns (set by platform governance) get first pick

### Fair Representation
The multi-channel scheduler ensures:
- Diverse content across TV, Radio, and Online channels
- No single campaign monopolizes airtime
- Community-focused content gets adequate visibility

---

## ✅ Submission Checklist

Before submitting, verify:

- [ ] Content is 1-10 minutes (music) or appropriate length (podcasts)
- [ ] Format is MP4 (video) or MP3 (audio)
- [ ] **Name** is clear and descriptive
- [ ] **Genre** is specified
- [ ] **Description** is complete (1-3 sentences)
- [ ] **Author Notes** explain your creative process
- [ ] **Tags** include at least one keyword (civic/impact/ecological preferred)
- [ ] Content is original and not exclusive to another platform
- [ ] You own the rights to this content

---

## 🎯 Quick Examples

### Example 1: Music Track
```python
music_item = LibraryItem(
    name="Static Motion Track",
    genre="Ambient",
    description="Slow tempo, static motion piece for background use",
    author_notes="Designed to anchor calm presence in civic broadcasts",
    tags=["impact", "music"]
)
```

### Example 2: Podcast
```python
podcast_item = LibraryItem(
    name="Civic Dialogue Podcast",
    genre="Podcast",
    description="Weekly discussion on ethics and governance",
    author_notes="Anchors Centre Funding with lived voices",
    tags=["civic", "ethics"]
)
```

---

## ❓ FAQ

**Q: Can I submit the same content to other platforms?**  
A: Not if it's featured as "exclusive" elsewhere. Our policy prohibits airing content that's simultaneously exclusive on competing platforms.

**Q: How often will my content air?**  
A: Depends on campaign scheduling. Higher-priority civic campaigns using your content may air more frequently.

**Q: Can I update my metadata after submission?**  
A: Yes, you can update description, author notes, and tags. Name and genre changes require platform review.

**Q: What if I get dislikes?**  
A: Feedback helps improve content. Some dislikes are normal. Focus on the overall like/dislike ratio and community comments.

**Q: How do I see my ecological impact?**  
A: Check the `complete_summary.json` export for your campaign's tree and ocean scores, or request a contributor dashboard report.

**Q: Can I remove my content?**  
A: Yes, contact platform governance. Removal takes effect after current scheduled slots complete.

---

## 📞 Support & Questions

- **Technical Issues**: Check `library.py` documentation
- **Policy Questions**: See `CONTENT_POLICY.md`
- **Platform Architecture**: See `ARCHITECTURE_QUICK_REFERENCE.md`
- **Governance**: Contact GETS Studio governance team

---

## 🎉 Thank You!

Your contribution helps build a civic-creative ecosystem where content directly funds community initiatives and ecological restoration. Every view, every like, and every slot generates real-world impact.

**Welcome to the GETS Studio community!** 🌱
