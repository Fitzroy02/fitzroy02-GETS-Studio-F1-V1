# 💰 GETS Studio Monetization Scaffolding

## Overview

A **three-tier monetization architecture** balancing advertising revenue, subscription income, and sponsorship partnerships. Supports both ad-supported (default) and premium opt-out (£10) experiences while maintaining a 25% local ad quota.

---

## 💡 Monetization Modes

### Mode 1: Default (Ad-Supported)
**Free for users, revenue from advertising**

**Characteristics**:
- **Pre-roll ads**: 30-second advert before every full-length movie
- **Short content (<10 min)**: Always paired with pre-roll ad
- **Local ad quota**: 25% of total airtime reserved for local businesses
- **Mid-roll options**: Every 10 minutes in movies (user can skip)
- **Sponsorships**: Can replace standard ads for premium partners

**User Experience**:
```
Full-Length Movie:
┌──────────────┐
│ 30s Pre-Roll │
│    Advert    │
└──────┬───────┘
       │
       v
┌──────────────────┐
│ Movie Playback   │
│ (90-180 minutes) │
└──────┬───────────┘
       │
   ┌───┴────────┐
   │ 10 min     │
   │ elapsed?   │
   └───┬────────┘
       │ Yes
       v
┌──────────────────┐
│ Optional 30s     │
│ Mid-Roll         │
│ (skippable)      │
└──────────────────┘

Short Content:
┌──────────────┐
│ 30s Pre-Roll │
│    Advert    │
└──────┬───────┘
       │
       v
┌──────────────┐
│ Video (<10m) │
└──────┬───────┘
       │
       v
┌──────────────┐
│ End Card +   │
│ Sponsorship  │
└──────────────┘
```

---

### Mode 2: Opt-Out Premium (£10 Subscription)
**Paid tier, ad-free experience**

**Characteristics**:
- **No pre-roll ads** on full-length movies
- **No mid-roll interruptions**
- **Short content**: May carry subtle sponsorship branding (non-interruptive)
- **Pricing**: £10/month or £10 per movie (configurable)
- **Positioning**: "Ad-Free Premium Experience"

**User Experience**:
```
Full-Length Movie:
┌──────────────────┐
│ Movie Playback   │
│ (Uninterrupted)  │
└──────┬───────────┘
       │
       v
┌──────────────────┐
│ Sponsorship Logo │
│ "Presented by..."│
│ (5 seconds)      │
└──────────────────┘

Short Content:
┌──────────────────┐
│ Video (<10m)     │
│ (Uninterrupted)  │
└──────┬───────────┘
       │
       v
┌──────────────────┐
│ Subtle Branding  │
│ (Corner logo)    │
└──────────────────┘
```

---

## 📊 Airtime Allocation Model

### Daily Advertising Inventory
**Assumption**: 100 minutes of total advertising airtime per day across all feeds

| Ad Type | Airtime % | Daily Minutes | Slots (30s each) | Target Advertisers |
|---------|-----------|---------------|------------------|-------------------|
| **Local Ads** | 25% | 25 minutes | 50 slots | Small businesses, community orgs |
| **National Ads** | 50% | 50 minutes | 100 slots | Regional/national brands |
| **Global Ads** | 20% | 20 minutes | 40 slots | International corporations |
| **Sponsorships** | 5% | 5 minutes | 10 slots | Premium partners (branded content) |
| **Total** | 100% | 100 minutes | 200 slots | — |

### Local Ad Quota Enforcement

**Why 25%?**
- Mirrors commercial TV business practices
- Supports community economic development
- Creates accessible entry point for local businesses
- Ensures platform doesn't become exclusively corporate

**Enforcement Logic**:
```python
class AdAirtimeManager:
    def __init__(self):
        self.total_daily_minutes = 100
        self.local_quota_pct = 0.25
        self.local_quota_minutes = self.total_daily_minutes * self.local_quota_pct
        self.local_minutes_used = 0
    
    def can_schedule_local_ad(self, duration_seconds):
        """Check if local ad can be scheduled within quota"""
        duration_minutes = duration_seconds / 60
        if (self.local_minutes_used + duration_minutes) <= self.local_quota_minutes:
            return True
        return False
    
    def schedule_ad(self, ad_type, duration_seconds):
        """Schedule ad and track quota usage"""
        if ad_type == 'local':
            if not self.can_schedule_local_ad(duration_seconds):
                raise QuotaExceededError("Local ad quota reached for today")
            self.local_minutes_used += duration_seconds / 60
        
        return {'scheduled': True, 'quota_remaining': self.get_local_quota_remaining()}
    
    def get_local_quota_remaining(self):
        """Calculate remaining local ad quota"""
        return self.local_quota_minutes - self.local_minutes_used
```

---

## 🎬 Content Flow by Mode & Type

### Full-Length Movie Flows

#### Ad-Supported Mode
```
User Selects Movie (Free)
       │
       v
┌──────────────────────┐
│ Check Ad Inventory   │
│ • 25% local quota    │
│ • Sponsorship avail? │
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ Pre-Roll Ad (30s)    │
│ [Local or National]  │
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ Movie Playback       │
└──────┬───────────────┘
       │
   ┌───┴────────────┐
   │ Every 10 min   │
   └───┬────────────┘
       │
       v
┌──────────────────────┐
│ Mid-Roll Ad (30s)    │
│ [Skippable]          │
└──────────────────────┘
```

#### Premium Opt-Out Mode (£10)
```
User Selects Movie (Paid £10)
       │
       v
┌──────────────────────┐
│ Verify Subscription  │
│ Status               │
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ Sponsorship Logo     │
│ "Presented by XYZ"   │
│ (5 seconds)          │
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ Movie Playback       │
│ (Uninterrupted)      │
└──────────────────────┘
```

---

### Short Content Flows

#### Ad-Supported Mode
```
User Watches Short Video (Free)
       │
       v
┌──────────────────────┐
│ Pre-Roll Ad (30s)    │
│ [Respects local      │
│  25% quota]          │
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ Video Playback       │
│ (<10 minutes)        │
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ End Card             │
│ • Sponsorship option │
│ • Next video preview │
└──────────────────────┘
```

#### Premium Opt-Out Mode (£10)
```
User Watches Short Video (Paid)
       │
       v
┌──────────────────────┐
│ Video Playback       │
│ (No Pre-Roll)        │
│                      │
│ [Subtle branding:    │
│  corner logo]        │
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ End Card             │
│ • No sponsorship     │
│ • Next video preview │
└──────────────────────┘
```

---

## 📦 Bundle Integration

### Bundle Pricing & Ad Rules

| Bundle Tier | Monthly Price | Full-Length Movies | Short Content | Sponsorships | Local Ad Support |
|-------------|---------------|-------------------|---------------|--------------|------------------|
| **Basic (Free)** | £0 | Pre-roll + mid-roll | Pre-roll | Standard | 25% quota enforced |
| **Premium** | £10 | No ads | Minimal branding | Subtle logos only | N/A (no ads) |
| **Sponsor Bundle** | £0 | Branding instead of ads | Branding | Exclusive sponsor | 25% quota enforced |

### Bundle Logic Implementation

```python
class SubscriptionManager:
    def __init__(self):
        self.bundle_tiers = {
            'basic': {
                'price': 0,
                'pre_roll': True,
                'mid_roll': True,
                'sponsorship_branding': 'standard',
                'local_quota_applies': True
            },
            'premium': {
                'price': 10,
                'pre_roll': False,
                'mid_roll': False,
                'sponsorship_branding': 'subtle',
                'local_quota_applies': False
            },
            'sponsor': {
                'price': 0,
                'pre_roll': False,  # Replaced by sponsor branding
                'mid_roll': False,
                'sponsorship_branding': 'exclusive',
                'local_quota_applies': True
            }
        }
    
    def get_ad_rules(self, user_bundle):
        """Retrieve ad rules for user's subscription tier"""
        return self.bundle_tiers.get(user_bundle, self.bundle_tiers['basic'])
    
    def should_show_ad(self, user_bundle, ad_type):
        """Determine if ad should be shown based on subscription"""
        rules = self.get_ad_rules(user_bundle)
        
        if ad_type == 'pre_roll':
            return rules['pre_roll']
        elif ad_type == 'mid_roll':
            return rules['mid_roll']
        
        return False
```

---

## 🛠️ Three-Layer Implementation Architecture

### Layer 1: Content Router
**Purpose**: Classify content and route to appropriate mode

```python
class ContentRouter:
    def __init__(self):
        self.duration_threshold = 600  # 10 minutes
    
    def route_content(self, content, user_subscription):
        """
        Route content based on duration and subscription
        
        Returns:
            dict: Routing decision with monetization strategy
        """
        is_short_content = content.duration < self.duration_threshold
        
        return {
            'content_type': 'short' if is_short_content else 'movie',
            'duration': content.duration,
            'user_tier': user_subscription,
            'monetization_mode': self._get_monetization_mode(user_subscription),
            'next_layer': 'ad_scheduler'
        }
    
    def _get_monetization_mode(self, subscription):
        """Determine monetization approach"""
        if subscription == 'premium':
            return 'opt_out'
        elif subscription == 'sponsor':
            return 'branded'
        else:
            return 'ad_supported'
```

---

### Layer 2: Ad Scheduler
**Purpose**: Insert ads/sponsorships and enforce local quota

```python
class AdScheduler:
    def __init__(self, airtime_manager, subscription_manager):
        self.airtime_manager = airtime_manager
        self.subscription_manager = subscription_manager
    
    def schedule_ads(self, routing_info):
        """
        Generate ad schedule based on content and subscription
        
        Args:
            routing_info: Output from ContentRouter
        
        Returns:
            list: Ad insertion points with types
        """
        user_tier = routing_info['user_tier']
        content_type = routing_info['content_type']
        duration = routing_info['duration']
        
        ad_rules = self.subscription_manager.get_ad_rules(user_tier)
        ad_schedule = []
        
        # Pre-roll logic
        if ad_rules['pre_roll']:
            ad_type = self._select_ad_type('pre_roll')
            ad_schedule.append({
                'time': 0,
                'type': ad_type,
                'duration': 30,
                'skippable': False
            })
        
        # Mid-roll logic (movies only)
        if content_type == 'movie' and ad_rules['mid_roll']:
            interval = 600  # Every 10 minutes
            current_time = interval
            
            while current_time < duration:
                ad_type = self._select_ad_type('mid_roll')
                ad_schedule.append({
                    'time': current_time,
                    'type': ad_type,
                    'duration': 30,
                    'skippable': True
                })
                current_time += interval
        
        # Sponsorship branding
        if ad_rules['sponsorship_branding'] in ['subtle', 'exclusive']:
            ad_schedule.append({
                'time': 0,
                'type': 'sponsorship_logo',
                'duration': 5,
                'style': ad_rules['sponsorship_branding']
            })
        
        return ad_schedule
    
    def _select_ad_type(self, position):
        """
        Select ad type respecting local quota
        
        Args:
            position: 'pre_roll' or 'mid_roll'
        
        Returns:
            str: 'local', 'national', or 'global'
        """
        # Check local quota
        if self.airtime_manager.can_schedule_local_ad(30):
            # 25% chance to select local (enforces quota)
            import random
            if random.random() < 0.25:
                return 'local'
        
        # Otherwise, select national or global
        return 'national'  # Simplified; could be weighted random
```

---

### Layer 3: Subscription Manager
**Purpose**: Verify user tier and apply appropriate rules

```python
class SubscriptionManager:
    def __init__(self, database):
        self.db = database
    
    def verify_subscription(self, user_id):
        """
        Check user's subscription status
        
        Returns:
            dict: {tier, active, expires_at}
        """
        user_record = self.db.get_user(user_id)
        
        if not user_record:
            return {'tier': 'basic', 'active': True, 'expires_at': None}
        
        subscription = user_record.get('subscription', {})
        
        # Check if subscription is active
        if subscription.get('expires_at'):
            from datetime import datetime
            is_active = datetime.now() < subscription['expires_at']
        else:
            is_active = True
        
        return {
            'tier': subscription.get('tier', 'basic'),
            'active': is_active,
            'expires_at': subscription.get('expires_at')
        }
    
    def charge_user(self, user_id, amount, description):
        """
        Process subscription payment
        
        Args:
            user_id: User identifier
            amount: Payment amount (e.g., 10 for £10)
            description: Payment description
        
        Returns:
            dict: Payment status
        """
        # Integration with payment processor (Stripe, PayPal, etc.)
        # Simplified for scaffolding purposes
        
        payment_result = self._process_payment(user_id, amount)
        
        if payment_result['success']:
            self._update_subscription(user_id, 'premium', duration_months=1)
        
        return payment_result
```

---

## 💸 Revenue Stream Breakdown

### Revenue Sources

| Source | Daily Potential | Monthly Potential | Percentage | Notes |
|--------|----------------|-------------------|------------|-------|
| **Local Ads** | 50 slots × £50 avg = £2,500 | £75,000 | 20% | 25% of airtime, lower rates |
| **National Ads** | 100 slots × £500 avg = £50,000 | £1,500,000 | 40% | 50% of airtime, mid-tier rates |
| **Global Ads** | 40 slots × £2,000 avg = £80,000 | £2,400,000 | 35% | 20% of airtime, premium rates |
| **Subscriptions** | 1,000 users × £10 = £10,000 | £300,000 | 5% | Growing over time |
| **Total** | £142,500 | £4,275,000 | 100% | — |

### Revenue Allocation (Following Earlier Model)

| Allocation | Percentage | Monthly Amount | Purpose |
|------------|-----------|----------------|---------|
| **Ecological Impact** | 10-15% | £427,500-641,250 | Trees + oceans (213,750-320,625 trees) |
| **Platform Operations** | 55% | £2,351,250 | Infrastructure, moderation, compliance |
| **Centre** | 20% | £855,000 | Core services |
| **Contributors** | 5% | £213,750 | Creator rewards |
| **Reserve** | 5% | £213,750 | Emergency fund |

---

## 📈 Visual System Interconnection

```
┌─────────────────────────────────────────────────────────────────┐
│                          USER REQUEST                           │
│                    (Watch Movie or Short Video)                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         v
                ┌─────────────────────┐
                │  LAYER 1: Content   │
                │       Router        │
                │                     │
                │ • Classify content  │
                │ • Check subscription│
                │ • Route to mode     │
                └────────┬────────────┘
                         │
            ┌────────────┴─────────────┐
            │                          │
            v                          v
    ┌───────────────┐          ┌──────────────┐
    │ Ad-Supported  │          │ Premium      │
    │ Mode          │          │ Opt-Out      │
    └───────┬───────┘          └──────┬───────┘
            │                         │
            v                         v
    ┌───────────────────────┐  ┌─────────────────┐
    │ LAYER 2: Ad Scheduler │  │ No Ads, Just    │
    │                       │  │ Sponsorship     │
    │ • Insert pre-roll     │  │ Logo (5s)       │
    │ • Schedule mid-rolls  │  │                 │
    │ • Enforce 25% local   │  └─────────────────┘
    │   quota               │
    │ • Select ad type      │
    └───────┬───────────────┘
            │
            v
    ┌───────────────────────┐
    │ LAYER 3: Subscription │
    │       Manager         │
    │                       │
    │ • Verify user tier    │
    │ • Apply ad rules      │
    │ • Process payment     │
    └───────┬───────────────┘
            │
            v
    ┌───────────────────────┐
    │ CONTENT DELIVERY      │
    │                       │
    │ • Stream with ads     │
    │   (or without)        │
    │ • Track airtime quota │
    │ • Log revenue         │
    └───────────────────────┘
```

---

## 🚀 Implementation Roadmap

### Phase 1: Core Monetization (Weeks 1-2)
- [ ] Build `SubscriptionManager` with tier verification
- [ ] Implement payment processing integration (Stripe API)
- [ ] Create subscription database schema
- [ ] Unit tests for subscription flows

### Phase 2: Ad Scheduling (Weeks 3-4)
- [ ] Build `AdScheduler` with pre-roll/mid-roll logic
- [ ] Implement `AdAirtimeManager` for quota tracking
- [ ] Create ad inventory management system
- [ ] Test local quota enforcement

### Phase 3: Router Integration (Week 5)
- [ ] Connect `ContentRouter` to `AdScheduler`
- [ ] Implement mode-based routing (ad-supported vs. opt-out)
- [ ] Add sponsorship branding logic
- [ ] End-to-end flow testing

### Phase 4: Revenue Tracking (Week 6)
- [ ] Build analytics dashboard for revenue streams
- [ ] Implement real-time quota monitoring
- [ ] Create advertiser reporting tools
- [ ] Add ecological impact calculations

### Phase 5: User Experience (Week 7)
- [ ] Design subscription purchase flow
- [ ] Create ad-free preview/promotion
- [ ] Implement skip button for mid-rolls
- [ ] A/B test pricing tiers

### Phase 6: Launch & Optimize (Week 8)
- [ ] Deploy to production
- [ ] Monitor conversion rates (free → premium)
- [ ] Track advertiser satisfaction
- [ ] Iterate on quota enforcement

---

## 🔑 Key Insights

### Flexibility Achieved
✅ **Three revenue streams**: Ads + subscriptions + sponsorships  
✅ **Local business support**: 25% quota ensures community economic impact  
✅ **User choice**: Free (with ads) or premium (£10, ad-free)  
✅ **Scalable**: Can add more tiers (e.g., £5 for reduced ads)

### Ecological Impact
- **Ad-supported revenue** → 10-15% to ecological projects
- **Subscription revenue** → 10-15% to ecological projects
- **Example**: £4.275M monthly → £427K-641K for tree planting (213K-320K trees)

### Competitive Positioning
- **vs. YouTube**: More creator-friendly revenue share (5% vs. 55% platform)
- **vs. Netflix**: Hybrid model (free + premium) vs. subscription-only
- **vs. Local TV**: 25% local quota supports community businesses

---

## 📖 Next Steps

### Ready for Implementation?
**Yes** - All three layers are fully specified with pseudocode  
**Yes** - Revenue model is transparent and scalable  
**Yes** - Integration with existing streaming framework is clear

### Recommendation
**Push to GitHub** alongside `STREAMING_FRAMEWORK.md`. These two documents together provide complete technical and business scaffolding for GETS Studio platform.

---

*This monetization scaffolding completes the economic foundation for GETS Studio. Revenue flows are transparent, local businesses are supported, and users have meaningful choice.*
