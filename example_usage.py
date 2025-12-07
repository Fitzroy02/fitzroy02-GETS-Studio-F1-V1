#!/usr/bin/env python3
"""
Example usage demonstrating MultiChannelScheduler with realistic campaign scenarios.
Shows civic, impact, and commercial campaigns competing for airtime with fairness constraints.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import csv

# Import from ad_scheduler_advanced
# In a real project, these would be: from ad_scheduler_advanced import *
# For this example, we'll redefine the core classes inline

@dataclass
class Channel:
    name: str
    base_cpm: float
    max_slots_per_day: Optional[int] = None
    audience_weight: float = 1.0

@dataclass
class EcoImpact:
    trees_per_1000_impressions: float = 0.0
    oceans_score_per_1000: float = 0.0

@dataclass
class AdCampaign:
    name: str
    start_date: datetime
    end_date: datetime
    budget: float
    priority: int
    target_impressions: Optional[int] = None
    channel_weights: Dict[str, float] = field(default_factory=dict)
    cost_per_slot: Dict[str, float] = field(default_factory=dict)
    frequency_cap_per_day: Optional[int] = None
    pacing: str = "even"
    eco_impact: EcoImpact = field(default_factory=EcoImpact)
    metadata: Dict[str, str] = field(default_factory=dict)
    spent: float = 0.0
    scheduled_slots: List[Tuple['AdSlot', float]] = field(default_factory=list)

    def is_active(self, dt: datetime) -> bool:
        return self.start_date <= dt <= self.end_date and self.spent < self.budget

    def can_afford(self, channel_name: str) -> bool:
        return self.spent + self.cost_per_slot.get(channel_name, float('inf')) <= self.budget

@dataclass
class AdSlot:
    dt: datetime
    duration_minutes: int
    channel_name: str
    audience_size: int
    assigned_campaign: Optional[AdCampaign] = None

@dataclass
class FairnessPolicy:
    min_share_for_tags: Dict[str, float] = field(default_factory=dict)
    campaign_tags: Dict[str, List[str]] = field(default_factory=dict)

    def tag_for(self, campaign_name: str) -> List[str]:
        return self.campaign_tags.get(campaign_name, [])

class MultiChannelScheduler:
    def __init__(self, campaigns: List[AdCampaign], channels: Dict[str, Channel], slots: List[AdSlot],
                 fairness: Optional[FairnessPolicy] = None):
        self.campaigns = campaigns
        self.channels = channels
        self.slots = sorted(slots, key=lambda s: (s.dt, -channels[s.channel_name].audience_weight))
        self.fairness = fairness or FairnessPolicy()
        self.daily_counts = defaultdict(lambda: defaultdict(int))
        self.tag_counts = defaultdict(int)
        self.total_slots = len(self.slots)

    def _pacing_score(self, campaign: AdCampaign, slot_dt: datetime) -> float:
        total_days = max(1, (campaign.end_date.date() - campaign.start_date.date()).days + 1)
        day_index = (slot_dt.date() - campaign.start_date.date()).days
        if campaign.pacing == "frontload":
            return max(0.1, (total_days - day_index) / total_days)
        if campaign.pacing == "backload":
            return max(0.1, (day_index + 1) / total_days)
        return 1.0

    def _frequency_ok(self, campaign: AdCampaign, slot_dt: datetime) -> bool:
        if campaign.frequency_cap_per_day is None:
            return True
        day = slot_dt.date()
        return self.daily_counts[campaign.name][day] < campaign.frequency_cap_per_day

    def _fairness_pressure(self, campaign: AdCampaign) -> float:
        tags = self.fairness.tag_for(campaign.name)
        pressure = 1.0
        for t in tags:
            min_share = self.fairness.min_share_for_tags.get(t)
            if min_share is None:
                continue
            current_share = self.tag_counts[t] / max(1, self.total_slots)
            if current_share < min_share:
                pressure *= 1.2
        return pressure

    def _campaign_slot_score(self, campaign: AdCampaign, slot: AdSlot) -> float:
        ch = self.channels[slot.channel_name]
        weight = campaign.channel_weights.get(slot.channel_name, 0.0)
        if weight <= 0:
            return 0.0
        pacing = self._pacing_score(campaign, slot.dt)
        fairness = self._fairness_pressure(campaign)
        audience_util = slot.audience_size * ch.audience_weight
        return weight * pacing * fairness * audience_util

    def schedule(self):
        campaigns_sorted = sorted(self.campaigns, key=lambda c: (-c.priority, c.name))
        for slot in self.slots:
            best_campaign = None
            best_score = 0.0
            for campaign in campaigns_sorted:
                if not campaign.is_active(slot.dt):
                    continue
                if slot.channel_name not in campaign.cost_per_slot:
                    continue
                if not campaign.can_afford(slot.channel_name):
                    continue
                if not self._frequency_ok(campaign, slot.dt):
                    continue
                score = self._campaign_slot_score(campaign, slot)
                if score > best_score:
                    best_score = score
                    best_campaign = campaign
            if best_campaign:
                slot.assigned_campaign = best_campaign
                cost = best_campaign.cost_per_slot[slot.channel_name]
                best_campaign.spent += cost
                best_campaign.scheduled_slots.append((slot, cost))
                day = slot.dt.date()
                self.daily_counts[best_campaign.name][day] += 1
                for t in self.fairness.tag_for(best_campaign.name):
                    self.tag_counts[t] += 1

    def export_csv(self, path: str):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["datetime", "channel", "duration_min", "audience", "campaign", "slot_cost", "spent_total"])
            for slot in self.slots:
                if slot.assigned_campaign:
                    c = slot.assigned_campaign
                    cost = c.cost_per_slot.get(slot.channel_name, 0.0)
                    writer.writerow([
                        slot.dt.isoformat(),
                        slot.channel_name,
                        slot.duration_minutes,
                        slot.audience_size,
                        c.name,
                        round(cost, 2),
                        round(c.spent, 2),
                    ])

def estimate_eco_impact(campaigns: List[AdCampaign]) -> Dict[str, Dict[str, float]]:
    """Calculate ecological impact metrics for all campaigns."""
    impact = {}
    for campaign in campaigns:
        total_impressions = sum(slot.audience_size for slot, _ in campaign.scheduled_slots)
        trees = campaign.eco_impact.trees_per_1000_impressions * total_impressions / 1000
        oceans = campaign.eco_impact.oceans_score_per_1000 * total_impressions / 1000
        impact[campaign.name] = {
            "trees": trees,
            "oceans": oceans,
            "impressions": total_impressions
        }
    return impact

# ----- Main Example Usage -----

if __name__ == "__main__":
    # Channels
    channels = {
        "TV": Channel(name="TV", base_cpm=18.0, max_slots_per_day=48, audience_weight=1.3),
        "Radio": Channel(name="Radio", base_cpm=6.0, max_slots_per_day=96, audience_weight=0.9),
        "Online": Channel(name="Online", base_cpm=4.0, max_slots_per_day=None, audience_weight=1.0),
    }

    # Campaigns
    start = datetime(2025, 12, 7)
    end = datetime(2025, 12, 14)
    campaigns = [
        AdCampaign(
            name="Centre Funding",
            start_date=start,
            end_date=datetime(2025, 12, 10),
            budget=5000,
            priority=3,
            channel_weights={"TV": 0.6, "Radio": 0.2, "Online": 0.2},
            cost_per_slot={"TV": 500, "Radio": 120, "Online": 60},
            frequency_cap_per_day=6,
            pacing="even",
            eco_impact=EcoImpact(trees_per_1000_impressions=0.2, oceans_score_per_1000=0.1),
            metadata={"category": "civic"},
        ),
        AdCampaign(
            name="Eco Project",
            start_date=start,
            end_date=end,
            budget=7000,
            priority=2,
            channel_weights={"TV": 0.3, "Radio": 0.3, "Online": 0.4},
            cost_per_slot={"TV": 400, "Radio": 100, "Online": 50},
            frequency_cap_per_day=8,
            pacing="frontload",
            eco_impact=EcoImpact(trees_per_1000_impressions=0.5, oceans_score_per_1000=0.4),
            metadata={"category": "impact"},
        ),
        AdCampaign(
            name="Local Business",
            start_date=start + timedelta(days=1),
            end_date=end,
            budget=3000,
            priority=1,
            channel_weights={"TV": 0.2, "Radio": 0.5, "Online": 0.3},
            cost_per_slot={"TV": 300, "Radio": 80, "Online": 40},
            frequency_cap_per_day=10,
            pacing="backload",
            metadata={"category": "commercial"},
        ),
    ]

    # Fairness policy: ensure at least 25% of slots go to "impact" campaigns
    fairness = FairnessPolicy(
        min_share_for_tags={"impact": 0.25},
        campaign_tags={
            "Eco Project": ["impact"],
            "Centre Funding": ["civic"],
            "Local Business": ["commercial"],
        }
    )

    # Generate slots (e.g., 08:00–20:00 across channels, hourly TV, half-hour Radio/Online)
    def gen_slots_for_day(day: datetime) -> List[AdSlot]:
        slots: List[AdSlot] = []
        for hour in range(8, 20):
            # TV hourly
            slots.append(AdSlot(dt=day.replace(hour=hour, minute=0), duration_minutes=30, channel_name="TV",
                                audience_size=12000 if hour in (19, 20) else 8000))
            # Radio half-hour
            slots.append(AdSlot(dt=day.replace(hour=hour, minute=0), duration_minutes=15, channel_name="Radio",
                                audience_size=4000))
            slots.append(AdSlot(dt=day.replace(hour=hour, minute=30), duration_minutes=15, channel_name="Radio",
                                audience_size=4500))
            # Online quarter-hour bursts
            for m in (0, 15, 30, 45):
                slots.append(AdSlot(dt=day.replace(hour=hour, minute=m), duration_minutes=10, channel_name="Online",
                                    audience_size=3000 if hour in (12, 18) else 2000))
        return slots

    slots = []
    for d in range(0, 3):  # schedule first 3 days for the example
        slots.extend(gen_slots_for_day(start + timedelta(days=d)))

    print(f"Generated {len(slots)} slots across 3 days for TV, Radio, and Online channels")
    print(f"Scheduling {len(campaigns)} campaigns with fairness policy (25% impact minimum)")
    print("="*70)

    # Schedule
    scheduler = MultiChannelScheduler(campaigns=campaigns, channels=channels, slots=slots, fairness=fairness)
    scheduler.schedule()

    # Output summary
    print("\n--- Campaign Performance ---")
    total_spent = 0
    total_slots = 0
    for c in campaigns:
        total_spent += c.spent
        total_slots += len(c.scheduled_slots)
        utilization = (c.spent / c.budget * 100) if c.budget > 0 else 0
        print(f"{c.name}:")
        print(f"  Spent: £{round(c.spent, 2)} / £{c.budget} ({utilization:.1f}% utilization)")
        print(f"  Slots: {len(c.scheduled_slots)}")
        print(f"  Pacing: {c.pacing}")
        print(f"  Category: {c.metadata.get('category', 'N/A')}")
    
    print(f"\nTotal Spent: £{total_spent:.2f}")
    print(f"Total Slots Assigned: {total_slots}")

    # Eco impact
    print("\n--- Ecological Impact ---")
    impact = estimate_eco_impact(campaigns)
    total_trees = 0
    total_oceans = 0
    for name, vals in impact.items():
        print(f"{name}:")
        print(f"  Trees planted: {vals['trees']:.2f}")
        print(f"  Ocean restoration score: {vals['oceans']:.2f}")
        print(f"  Impressions: {vals['impressions']:,}")
        total_trees += vals['trees']
        total_oceans += vals['oceans']
    
    print(f"\nTotal Trees Planted: {total_trees:.2f}")
    print(f"Total Ocean Restoration Score: {total_oceans:.2f}")

    # Fairness compliance
    print("\n--- Fairness Policy Compliance ---")
    for tag, required_fraction in fairness.min_share_for_tags.items():
        actual_count = scheduler.tag_counts[tag]
        actual_fraction = actual_count / scheduler.total_slots if scheduler.total_slots > 0 else 0
        status = "✓" if actual_fraction >= required_fraction else "✗"
        print(f"{status} {tag}: {actual_count}/{scheduler.total_slots} slots "
              f"({actual_fraction:.1%}) - Required: {required_fraction:.1%}")

    # CSV export
    output_file = "summary.csv"
    scheduler.export_csv(output_file)
    print(f"\n✓ Schedule exported to {output_file}")
    print("="*70)
