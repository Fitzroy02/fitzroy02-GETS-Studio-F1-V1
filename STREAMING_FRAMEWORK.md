# 🎬 GETS Studio Streaming Framework

## Overview

A **multi-mode streaming architecture** that intelligently routes content based on duration, type, and user preferences. Balances short-form videos, full-length movies, and advertising while supporting flexible bundle packages.

---

## 🎯 Core Streaming Modes

### 1. Ad + Short Content Mode
**Purpose**: Deliver bite-sized content with advertising integration

**Characteristics**:
- **Anchor**: 30-second advert
- **Content Duration**: Under 10 minutes
- **Allowed Content**:
  - Music videos (motion only, no static images)
  - Short films
  - Trailers
  - Documentary clips
- **Flow**: `Ad → Short Video → [Optional Next Ad] → Repeat`

**Ad Logic**:
```
┌─────────────┐
│  30s Advert │
└──────┬──────┘
       │
       v
┌─────────────────┐
│ Short Video     │
│ (0-10 minutes)  │
└──────┬──────────┘
       │
       v
  ┌────────────────┐
  │ Session Active?│
  └───┬────────┬───┘
      │ Yes    │ No
      v        v
┌─────────┐  End
│Next Ad  │
└─────────┘
```

---

### 2. Full-Length Movie Mode
**Purpose**: Feature film streaming with minimal interruption

**Characteristics**:
- **Content Duration**: ≥10 minutes (typically 90-180 minutes)
- **User Selection**: Browse movie pool, choose specific title
- **Ad Options**:
  - **Pre-roll Only** (single ad before movie)
  - **Interval Ads** (every 10-15 minutes, opt-out available)

**Ad Logic**:
```
User Selects Movie
       │
       v
┌──────────────┐
│ Pre-roll Ad  │
│  (30 sec)    │
└──────┬───────┘
       │
       v
┌──────────────────┐
│ Movie Playback   │
│ (90-180 minutes) │
└──────┬───────────┘
       │
   ┌───┴────┐
   │ 10 min │
   │elapsed?│
   └───┬────┘
       │ Yes
       v
  ┌─────────────┐
  │User Opted   │
  │for Mid-roll?│
  └───┬─────┬───┘
      │Yes  │No
      v     v
  ┌──────┐ Continue
  │30s Ad│ Playback
  └──────┘
```

---

## 📡 Channel Feeds Architecture

### Feed Types

| Feed Name | Content Type | Duration Range | Motion Requirement | Ad Integration |
|-----------|--------------|----------------|-------------------|----------------|
| **Music Feed** | Music videos | 2-8 minutes | Motion only | Pre-roll every video |
| **Shorts Feed** | Creative shorts | 1-10 minutes | Any format | Pre-roll every 2-3 videos |
| **Movies Feed** | Feature films | 60-180 minutes | Any format | Pre-roll + optional intervals |
| **Advert Feed** | Commercials | 15-30 seconds | Any format | Standalone continuous |

### Feed Management System

```python
# Conceptual feed manager structure

class FeedManager:
    def __init__(self):
        self.feeds = {
            'music': MusicFeed(),
            'shorts': ShortsFeed(),
            'movies': MoviesFeed(),
            'adverts': AdvertFeed()
        }
    
    def get_feed_content(self, feed_type, duration_limit=None):
        """Retrieve content from specified feed"""
        feed = self.feeds.get(feed_type)
        return feed.fetch_content(duration_limit)
    
    def ensure_diversity(self, feed_type):
        """Maintain content variety within feed"""
        feed = self.feeds.get(feed_type)
        return feed.check_diversity_threshold()

class MusicFeed:
    def fetch_content(self, limit):
        """Fetch motion music videos only"""
        return [video for video in self.catalog 
                if video.has_motion and video.duration <= 600]

class MoviesFeed:
    def fetch_content(self, limit):
        """Fetch feature-length films"""
        return [movie for movie in self.catalog 
                if movie.duration >= 600]
```

---

## 🧩 Bundle Packages

### Bundle Architecture

Bundles are **curated combinations of feeds** that users subscribe to. Each bundle defines:
- Which feeds are included
- Ad placement rules
- Pricing tier
- Special features (skip ads, downloads, etc.)

### Bundle Types

| Bundle Name | Feeds Included | Ad Placement | Price Tier | Special Features |
|-------------|----------------|--------------|------------|------------------|
| **Music Only** | Music Feed | Pre-roll every video | £5/month | Curated playlists |
| **Shorts Variety** | Shorts Feed | Pre-roll every 2-3 videos | £7/month | Creator spotlights |
| **Movie Buff** | Movies Feed | Pre-roll + mid-roll opt-out | £12/month | New releases first |
| **Music + Shorts** | Music + Shorts | Pre-roll every video | £10/month | Cross-feed discovery |
| **Complete Access** | All Feeds | Pre-roll only | £18/month | Ad-skip option |
| **Premium Ad-Free** | All Feeds | No ads | £25/month | Downloads, 4K |

### Bundle Logic Flow

```
User Subscribes to Bundle
       │
       v
┌──────────────────┐
│ Parse Bundle     │
│ Configuration    │
└────────┬─────────┘
         │
         v
    ┌────────────────┐
    │ Load Feed List │
    └────┬───────────┘
         │
         v
    ┌────────────────────┐
    │ Apply Ad Rules     │
    │ (from bundle tier) │
    └────┬───────────────┘
         │
         v
    ┌────────────────────┐
    │ Generate Playlist  │
    │ (stitched feeds)   │
    └────┬───────────────┘
         │
         v
    Stream to User
```

---

## 🛠️ Content Router System

### Routing Decision Tree

The **Content Router** is the brain that decides which mode to use based on content metadata:

```
Content Uploaded
       │
       v
┌──────────────────┐
│ Analyze Metadata │
│ • Duration       │
│ • Type           │
│ • Motion         │
└────────┬─────────┘
         │
    ┌────┴─────┐
    │ Duration │
    │ Check    │
    └────┬─────┘
         │
    ┌────┴────────┐
    │             │
    v             v
< 10 min      ≥ 10 min
    │             │
    v             v
┌──────────┐  ┌──────────┐
│ Short    │  │ Movie    │
│ Content  │  │ Mode     │
│ Mode     │  │          │
└────┬─────┘  └────┬─────┘
     │             │
     v             v
┌──────────┐  ┌──────────┐
│ Check    │  │ Add to   │
│ Motion   │  │ Movies   │
│ (if      │  │ Feed     │
│ music)   │  │          │
└────┬─────┘  └──────────┘
     │
  ┌──┴───┐
  │      │
  v      v
Motion  Static
  │      │
  v      v
Music  Shorts
Feed   Feed
```

### Router Implementation Concept

```python
class ContentRouter:
    def __init__(self):
        self.duration_threshold = 600  # 10 minutes in seconds
        self.music_motion_required = True
    
    def route_content(self, content):
        """
        Route content to appropriate mode and feed
        
        Args:
            content: Video object with metadata
        
        Returns:
            dict: {mode, feed, ad_strategy}
        """
        duration = content.duration
        content_type = content.type
        has_motion = content.has_motion
        
        # Duration-based routing
        if duration < self.duration_threshold:
            mode = 'short_content'
            
            # Type-based feed assignment
            if content_type == 'music':
                if has_motion:
                    feed = 'music_feed'
                else:
                    return {'error': 'Music videos require motion'}
            else:
                feed = 'shorts_feed'
            
            ad_strategy = 'pre_roll'
        
        else:  # Full-length content
            mode = 'movie'
            feed = 'movies_feed'
            ad_strategy = 'pre_roll_with_intervals'
        
        return {
            'mode': mode,
            'feed': feed,
            'ad_strategy': ad_strategy,
            'content_id': content.id
        }
```

---

## 📊 Ad Scheduler System

### Ad Placement Rules

| Mode | Pre-Roll | Mid-Roll | Frequency | User Control |
|------|----------|----------|-----------|--------------|
| Short Content | Always | Optional | After each video | Skip after 5 sec |
| Movie | Always | Optional | Every 10-15 min | Full opt-out |
| Music Feed | Always | Never | Every video | Skip after 5 sec |
| Ad-Free Bundle | Never | Never | N/A | Full control |

### Scheduler Logic

```python
class AdScheduler:
    def __init__(self, user_bundle):
        self.user_bundle = user_bundle
        self.ad_settings = self._load_bundle_ad_rules(user_bundle)
    
    def schedule_ads(self, content, mode):
        """
        Generate ad insertion points for content
        
        Args:
            content: Video object
            mode: 'short_content' or 'movie'
        
        Returns:
            list: Ad insertion timestamps
        """
        ad_points = []
        
        # Check bundle ad rules
        if self.ad_settings['pre_roll_enabled']:
            ad_points.append({'time': 0, 'type': 'pre_roll', 'duration': 30})
        
        if mode == 'movie' and self.ad_settings['mid_roll_enabled']:
            duration = content.duration
            interval = self.ad_settings['mid_roll_interval']  # 600-900 seconds
            
            current_time = interval
            while current_time < duration:
                ad_points.append({
                    'time': current_time,
                    'type': 'mid_roll',
                    'duration': 30,
                    'skippable': self.ad_settings['mid_roll_skippable']
                })
                current_time += interval
        
        return ad_points
    
    def _load_bundle_ad_rules(self, bundle):
        """Load ad rules from bundle configuration"""
        bundle_configs = {
            'music_only': {
                'pre_roll_enabled': True,
                'mid_roll_enabled': False
            },
            'premium_ad_free': {
                'pre_roll_enabled': False,
                'mid_roll_enabled': False
            },
            'complete_access': {
                'pre_roll_enabled': True,
                'mid_roll_enabled': False
            }
        }
        return bundle_configs.get(bundle, {
            'pre_roll_enabled': True,
            'mid_roll_enabled': True,
            'mid_roll_interval': 600,
            'mid_roll_skippable': True
        })
```

---

## 📋 Workflow Diagram: Full System

```
┌─────────────────────────────────────────────────────────────────┐
│                     CONTENT INGESTION                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         v
                ┌────────────────┐
                │ Content Router │
                └────────┬───────┘
                         │
            ┌────────────┴────────────┐
            │                         │
            v                         v
    ┌───────────────┐        ┌──────────────┐
    │ Short Content │        │ Movie Mode   │
    │ Mode          │        │              │
    └───────┬───────┘        └──────┬───────┘
            │                       │
            v                       v
    ┌───────────────┐        ┌──────────────┐
    │ Feed Manager  │        │ Movies Feed  │
    │ • Music       │        │              │
    │ • Shorts      │        └──────┬───────┘
    └───────┬───────┘               │
            │                       │
            └───────────┬───────────┘
                        │
                        v
                ┌───────────────┐
                │ Ad Scheduler  │
                └───────┬───────┘
                        │
                        v
                ┌───────────────┐
                │ Bundle Logic  │
                └───────┬───────┘
                        │
                        v
            ┌───────────────────────┐
            │ Playlist Generation   │
            └───────┬───────────────┘
                    │
                    v
            ┌───────────────────────┐
            │ Stream to User        │
            └───────────────────────┘
```

---

## 🗂️ Mode Comparison Table

| Mode | Content Type | Duration Range | Ad Placement | Bundle Options | User Control |
|------|--------------|----------------|--------------|----------------|--------------|
| **Short Content** | Music videos, shorts, trailers | <10 minutes | Pre-roll + optional | Music + Shorts, Shorts Variety | Skip after 5 sec |
| **Full Movie** | Feature films | ≥10 minutes (60-180 min) | Pre-roll + mid-roll opt-out | Movie Buff, Complete Access | Full mid-roll opt-out |
| **Music Videos** | Motion music only | 2-8 minutes | Pre-roll every video | Music-only bundle | Skip after 5 sec |
| **Advert Channel** | 30-sec commercials | 15-30 seconds | Continuous feed | Ad-supported bundles | N/A |

---

## 🚀 Implementation Phases

### Phase 1: Core Router (Weeks 1-2)
- [ ] Build `ContentRouter` class
- [ ] Implement duration-based routing
- [ ] Add motion detection for music videos
- [ ] Unit tests for all routing scenarios

### Phase 2: Feed Management (Weeks 3-4)
- [ ] Create `FeedManager` class
- [ ] Implement individual feed classes (Music, Shorts, Movies, Adverts)
- [ ] Add diversity checking algorithms
- [ ] Content tagging and metadata system

### Phase 3: Ad Scheduler (Week 5)
- [ ] Build `AdScheduler` class
- [ ] Implement pre-roll logic
- [ ] Add mid-roll interval calculations
- [ ] User opt-out handling

### Phase 4: Bundle System (Weeks 6-7)
- [ ] Design bundle configuration schema
- [ ] Create bundle subscription logic
- [ ] Implement playlist stitching
- [ ] Pricing tier integration

### Phase 5: Integration & Testing (Week 8)
- [ ] Connect all components
- [ ] End-to-end user flow testing
- [ ] Performance optimization
- [ ] Documentation completion

---

## 🔐 Technical Considerations

### Content Requirements
- **Motion Detection**: Computer vision to verify music videos have motion
- **Duration Metadata**: Accurate timestamps for routing decisions
- **Type Classification**: ML model or manual tagging for content types

### Scalability
- **Feed Caching**: Pre-load feeds for faster retrieval
- **CDN Integration**: Distribute content geographically
- **Database Indexing**: Duration and type fields for quick queries

### User Experience
- **Smooth Transitions**: Seamless ad-to-content flow
- **Buffer Management**: Pre-load next content during ads
- **Skip Logic**: 5-second skip button for eligible ads

---

## 📖 Next Steps

### Ready for GitHub?
**Yes, when**:
- Core routing logic is pseudocoded (✅ Done above)
- Feed structure is defined (✅ Done above)
- You want collaborators to implement/test

**Not yet, if**:
- Still conceptualizing bundle pricing
- Need to experiment with ad intervals
- Want to prototype in isolation first

### Recommendation
**Push to GitHub now** as a design document (`STREAMING_FRAMEWORK.md`). Mark it as "RFC" (Request for Comments) so collaborators know it's still evolving. You can iterate in branches without cluttering main.

---

*This streaming framework scaffolding is ready for implementation. All major components are defined with clear interfaces and flow logic.*
