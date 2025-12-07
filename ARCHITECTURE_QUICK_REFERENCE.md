# 🎬 GETS Studio Architecture Quick Reference

**One-page overview of streaming platform architecture, monetization bundles, and user flows**

---

## 🗺️ Simplified System Flow

```
                ┌─────────────────────┐
                │   User selects      │
                │  content type       │
                └─────────┬───────────┘
                          │
        ┌─────────────────┼───────────────────┐
        │                 │                   │
   Short Video (<10 min)  │             Full-Length Movie
        │                 │                   │
        ▼                 │                   ▼
 ┌───────────────┐        │          ┌───────────────────┐
 │ Short Content │        │          │ Full Movie Mode   │
 │     Mode      │        │          └─────────┬─────────┘
 └───────┬───────┘        │                    │
         │                 │                    │
         ▼                 │                    ▼
 ┌───────────────┐         │          ┌───────────────────┐
 │ Ad Scheduler  │─────────┼─────────▶│ Ad Scheduler      │
 │ - 30s pre-roll│         │          │ - 30s pre-roll    │
 │ - Sponsorship │         │          │ - Mid-roll ads    │
 └───────┬───────┘         │          │ - Sponsorship     │
         │                 │          └─────────┬─────────┘
         ▼                 │                    │
 ┌───────────────┐         │                    ▼
 │ Subscription  │─────────┼─────────▶┌───────────────────┐
 │   Manager     │         │          │ Subscription      │
 │ - £10 opt-out │         │          │ Manager           │
 │ - Ad-free     │         │          │ - £10 opt-out     │
 └───────┬───────┘         │          │ - Ad-free movies  │
         │                 │          └─────────┬─────────┘
         ▼                 │                    │
 ┌───────────────┐         │                    ▼
 │ Feed Manager  │─────────┼─────────▶┌───────────────────┐
 │ - Music Feed  │         │          │ Bundling Logic    │
 │ - Shorts Feed │         │          │ - Basic Bundle    │
 │ - Movies Feed │         │          │ - Premium Bundle  │
 │ - Ad Channel  │         │          │ - Sponsor Bundle  │
 └───────────────┘         │          └───────────────────┘
```

### Flow Highlights
- **Left path**: Short videos with pre-roll ads
- **Right path**: Full-length movies with pre-roll + optional mid-rolls
- **Central integration**: All paths converge through Ad Scheduler → Subscription Manager → Feed Manager → Bundling Logic

---

## 📦 Bundle Comparison Table

| Feature | Basic (Ad-Supported) | Premium (£10/month) | Sponsor Bundle |
|---------|---------------------|---------------------|----------------|
| **Price** | Free | £10/month | Free (partner-funded) |
| **Content Access** | Music, shorts, movies | Music, shorts, movies | Music, shorts, movies |
| **Pre-Roll Ads** | ✅ 30 seconds before all content | ❌ None | ❌ Replaced by sponsor branding |
| **Mid-Roll Ads (Movies)** | ✅ Every 10 min (skippable) | ❌ None | ❌ None |
| **Sponsorship Branding** | Optional end-card | Subtle logo (5 sec) | Prominent "Presented by..." |
| **Local Ad Quota** | ✅ 25% of airtime | N/A (no ads) | ✅ 25% if ads present |
| **Skip Ads After** | 5 seconds | N/A | N/A |
| **4K Quality** | ❌ 1080p max | ✅ 4K available | ❌ 1080p max |
| **Downloads** | ❌ Stream only | ✅ Offline viewing | ❌ Stream only |
| **Best For** | Casual viewers, local ad supporters | Binge watchers, ad-free seekers | Brand partners, corporate sponsors |

### 🔑 Key Notes
- **Local Ads**: Always 25% of ad airtime in Basic Bundle (supports community businesses)
- **Premium Tier**: Removes disruptive ads, allows non-interruptive sponsor branding
- **Sponsor Bundle**: Corporate partners replace ads with brand identity

---

## 🎯 Example User Journeys

### Short Video (<10 minutes)

| Bundle | Journey |
|--------|---------|
| **Basic** | 30s pre-roll ad (local) → Video plays → End card with sponsor option |
| **Premium** | Video plays immediately → Subtle corner logo → End card (no sponsor) |
| **Sponsor** | Sponsor intro (5s) → Video with branding → Sponsor outro (5s) |

### Full-Length Movie (90-180 minutes)

| Bundle | Journey |
|--------|---------|
| **Basic** | 30s pre-roll → Movie → Mid-roll every 10 min (6 total, skippable after 5s) |
| **Premium** | Sponsor logo (5s) → Movie uninterrupted → End credits |
| **Sponsor** | Sponsor sequence (15s) → Movie with corner logo → Mid-movie message (5s) |

---

## 📊 Airtime Allocation (100 minutes daily)

| Ad Type | % Airtime | Daily Minutes | Slots (30s) | Target |
|---------|-----------|---------------|-------------|--------|
| **Local Ads** | 25% | 25 min | 50 slots | Community businesses |
| **National Ads** | 50% | 50 min | 100 slots | Regional brands |
| **Global Ads** | 20% | 20 min | 40 slots | International corps |
| **Sponsorships** | 5% | 5 min | 10 slots | Premium partners |

---

## 💸 Revenue & Ecological Impact

### Revenue per User (Monthly)

| Bundle | User Pays | Platform Revenue | Ecological Impact |
|--------|-----------|------------------|-------------------|
| **Basic** | £0 | £12 (from ads) | £1.20 → 0.6 trees |
| **Premium** | £10 | £10 (subscription) | £1.00-1.50 → 0.5-0.75 trees |
| **Sponsor** | £0 | £15 (sponsor contract) | £1.50 → 0.75 trees |

### Total Platform Revenue (Monthly)
- **Daily Potential**: £142,500
- **Monthly Potential**: £4,275,000
- **Ecological (10-15%)**: £427K-641K → **213K-320K trees planted**

### Revenue Allocation
- 📊 **Platform Operations**: 55% (£2.35M)
- 🌱 **Ecological Impact**: 10-15% (£427K-641K)
- 🏢 **Centre**: 20% (£855K)
- 👥 **Contributors**: 5% (£213K)
- 💰 **Reserve**: 5% (£213K)

---

## 🛠️ Three-Layer Architecture

### Layer 1: Content Router
- Analyzes duration (<10 min = short, ≥10 min = movie)
- Checks content type and motion (music videos)
- Routes to appropriate mode

### Layer 2: Ad Scheduler
- Inserts pre-roll ads (30 seconds)
- Schedules mid-roll ads (every 10 min for movies)
- Enforces 25% local ad quota
- Applies sponsorship branding for premium users

### Layer 3: Subscription Manager
- Verifies user subscription tier (Basic/Premium/Sponsor)
- Applies bundle-specific ad rules
- Processes payments (£10 for Premium)
- Grants access to premium features (4K, downloads)

---

## 📈 Bundle Growth Strategy

| Phase | Timeline | Basic | Premium | Sponsor |
|-------|----------|-------|---------|---------|
| **Launch** | Months 1-3 | 90% | 8% | 2% |
| **Maturity** | Months 6-12 | 70% | 25% | 5% |
| **Optimization** | Year 2+ | 60% | 35% | 5% |

**Key Insight**: Target 35% premium conversion by Year 2 for predictable subscription revenue while maintaining ad-supported majority.

---

## 🎬 Feed Organization

| Feed Type | Content | Duration | Ad Integration |
|-----------|---------|----------|----------------|
| **Music Feed** | Motion music videos | 2-8 min | Pre-roll every video |
| **Shorts Feed** | Creative shorts | 1-10 min | Pre-roll every 2-3 videos |
| **Movies Feed** | Feature films | 60-180 min | Pre-roll + optional intervals |
| **Advert Feed** | Commercials | 15-30 sec | Standalone continuous |

---

## ✅ Implementation Checklist

### Week 1-2: Core Router
- [ ] Build ContentRouter class with duration-based logic
- [ ] Implement motion detection for music videos
- [ ] Add content type classification

### Week 3-4: Ad Scheduling
- [ ] Create AdScheduler with pre-roll/mid-roll logic
- [ ] Implement 25% local quota enforcement
- [ ] Build ad inventory management

### Week 5-6: Subscription System
- [ ] Build SubscriptionManager with tier verification
- [ ] Integrate payment processing (Stripe)
- [ ] Create subscription database schema

### Week 7-8: Integration & Testing
- [ ] Connect all three layers
- [ ] End-to-end user flow testing
- [ ] Revenue tracking and analytics

---

## 🔗 Related Documents

- **[STREAMING_FRAMEWORK.md](STREAMING_FRAMEWORK.md)**: Complete technical architecture with pseudocode
- **[MONETIZATION_SCAFFOLDING.md](MONETIZATION_SCAFFOLDING.md)**: Detailed monetization models and revenue analysis
- **[INTEGRATION_PLAN.md](INTEGRATION_PLAN.md)**: Live dashboard integration with data sources
- **[README.md](README.md)**: Governance framework, token economy, and civic stewardship vision

---

*This quick reference provides a complete at-a-glance view of GETS Studio's streaming architecture, bundle differentiation, and implementation roadmap.*
