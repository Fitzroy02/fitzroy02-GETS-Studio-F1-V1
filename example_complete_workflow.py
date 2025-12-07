#!/usr/bin/env python3
"""
Complete workflow example for GETS Studio Ad Scheduler
Demonstrates: multi-channel scheduling, per-campaign allocation policies, 
fairness enforcement, and ecological impact tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import csv
import json

# Import classes from ad_scheduler_advanced
# In production, use: from ad_scheduler_advanced import *

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
class EcoRates:
    trees_per_currency: float = 0.0
    oceans_score_per_currency: float = 0.0

@dataclass
class AllocationPolicy:
    shares: Dict[str, float]

@dataclass
class AllocationResult:
    amounts: Dict[str, float]
    total_spend: float
    impressions: int
    dt: datetime
    channel: str
    campaign: str

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
    metadata: Dict[str, any] = field(default_factory=dict)
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

def apply_allocation(cost: float, impressions: int, dt: datetime, channel: str, campaign: str,
                     policy: AllocationPolicy) -> AllocationResult:
    amounts = {k: round(cost * v, 2) for k, v in policy.shares.items()}
    return AllocationResult(amounts=amounts, total_spend=round(cost, 2),
                            impressions=impressions, dt=dt, channel=channel, campaign=campaign)

def eco_rollup_from_allocations(allocations: List[AllocationResult],
                                campaign_impacts: Dict[str, EcoImpact],
                                eco_rates: EcoRates = EcoRates()) -> Dict[str, Dict[str, float]]:
    totals = defaultdict(lambda: {"trees": 0.0, "oceans": 0.0})
    for alloc in allocations:
        c_name = alloc.campaign
        eco = campaign_impacts.get(c_name, EcoImpact())
        trees_impr = (alloc.impressions / 1000.0) * eco.trees_per_1000_impressions
        oceans_impr = (alloc.impressions / 1000.0) * eco.oceans_score_per_1000
        trees_amt = alloc.amounts.get("trees", 0.0) * eco_rates.trees_per_currency
        oceans_amt = alloc.amounts.get("oceans", 0.0) * eco_rates.oceans_score_per_currency
        totals[c_name]["trees"] += trees_impr + trees_amt
        totals[c_name]["oceans"] += oceans_impr + oceans_amt
    return totals

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
        self.allocations_per_slot: List[AllocationResult] = []
        self.daily_allocation_totals = defaultdict(lambda: defaultdict(float))
        self.campaign_allocation_totals = defaultdict(lambda: defaultdict(float))

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

                # Allocation step
                policy = best_campaign.metadata.get("allocation_policy")
                if policy is None:
                    policy = AllocationPolicy(shares={"broadcaster": 0.7, "centre": 0.2, "trees": 0.06, "oceans": 0.04})
                    best_campaign.metadata["allocation_policy"] = policy

                alloc = apply_allocation(cost, slot.audience_size, slot.dt, slot.channel_name, best_campaign.name, policy)
                self.allocations_per_slot.append(alloc)

                for bucket, amt in alloc.amounts.items():
                    self.daily_allocation_totals[day][bucket] += amt
                    self.campaign_allocation_totals[best_campaign.name][bucket] += amt

if __name__ == "__main__":
    print("="*70)
    print("GETS Studio Ad Scheduler - Complete Workflow Example")
    print("="*70)
    
    # Define channels
    channels = {
        "TV": Channel(name="TV", base_cpm=18.0, max_slots_per_day=48, audience_weight=1.3),
        "Radio": Channel(name="Radio", base_cpm=6.0, max_slots_per_day=96, audience_weight=0.9),
        "Online": Channel(name="Online", base_cpm=4.0, max_slots_per_day=None, audience_weight=1.0),
    }

    # Define campaigns
    start = datetime(2025, 12, 7)
    end = datetime(2025, 12, 14)
    campaigns = [
        AdCampaign(
            name="Community Centre",
            start_date=start,
            end_date=datetime(2025, 12, 10),
            budget=4000,
            priority=3,
            channel_weights={"TV": 0.5, "Radio": 0.3, "Online": 0.2},
            cost_per_slot={"TV": 450, "Radio": 100, "Online": 50},
            frequency_cap_per_day=5,
            pacing="even",
            eco_impact=EcoImpact(trees_per_1000_impressions=0.3, oceans_score_per_1000=0.15),
        ),
        AdCampaign(
            name="Eco Initiative",
            start_date=start,
            end_date=end,
            budget=6000,
            priority=2,
            channel_weights={"TV": 0.3, "Radio": 0.4, "Online": 0.3},
            cost_per_slot={"TV": 400, "Radio": 90, "Online": 45},
            frequency_cap_per_day=6,
            pacing="frontload",
            eco_impact=EcoImpact(trees_per_1000_impressions=0.6, oceans_score_per_1000=0.4),
        ),
        AdCampaign(
            name="Local Business",
            start_date=start + timedelta(days=1),
            end_date=end,
            budget=5000,
            priority=1,
            channel_weights={"TV": 0.2, "Radio": 0.5, "Online": 0.3},
            cost_per_slot={"TV": 350, "Radio": 80, "Online": 40},
            frequency_cap_per_day=8,
            pacing="backload",
            eco_impact=EcoImpact(trees_per_1000_impressions=0.1, oceans_score_per_1000=0.05),
        ),
    ]

    # Fairness policy
    fairness = FairnessPolicy(
        min_share_for_tags={"impact": 0.20},
        campaign_tags={
            "Eco Initiative": ["impact"],
            "Community Centre": ["civic"],
            "Local Business": ["commercial"],
        }
    )

    # Generate slots (3 days for demo)
    def gen_slots_for_day(day: datetime) -> List[AdSlot]:
        slots = []
        for hour in range(8, 20):
            slots.append(AdSlot(dt=day.replace(hour=hour), duration_minutes=30, channel_name="TV",
                                audience_size=12000 if hour in (19, 20) else 8000))
            slots.append(AdSlot(dt=day.replace(hour=hour, minute=0), duration_minutes=15, channel_name="Radio",
                                audience_size=4000))
            slots.append(AdSlot(dt=day.replace(hour=hour, minute=30), duration_minutes=15, channel_name="Radio",
                                audience_size=4500))
            for m in (0, 15, 30, 45):
                slots.append(AdSlot(dt=day.replace(hour=hour, minute=m), duration_minutes=10, channel_name="Online",
                                    audience_size=3000 if hour in (12, 18) else 2000))
        return slots

    slots = []
    for d in range(0, 3):
        slots.extend(gen_slots_for_day(start + timedelta(days=d)))

    print(f"\nGenerated {len(slots)} slots across 3 days")
    print(f"Scheduling {len(campaigns)} campaigns with {len(channels)} channels")

    # Per-campaign allocation policies (different per campaign)
    campaigns[0].metadata["allocation_policy"] = AllocationPolicy(shares={
        "broadcaster": 0.68, "centre": 0.22, "trees": 0.06, "oceans": 0.04
    })
    campaigns[1].metadata["allocation_policy"] = AllocationPolicy(shares={
        "broadcaster": 0.65, "centre": 0.25, "trees": 0.06, "oceans": 0.04
    })
    campaigns[2].metadata["allocation_policy"] = AllocationPolicy(shares={
        "broadcaster": 0.75, "centre": 0.15, "trees": 0.06, "oceans": 0.04
    })

    # Schedule
    scheduler = MultiChannelScheduler(campaigns=campaigns, channels=channels, slots=slots, fairness=fairness)
    scheduler.schedule()

    # Eco conversion rates by currency (tune to match your impact model)
    eco_rates = EcoRates(trees_per_currency=0.01, oceans_score_per_currency=0.02)
    
    # Build map for impression-based impact
    campaign_impacts = {c.name: c.eco_impact for c in campaigns}

    eco_summary = eco_rollup_from_allocations(
        allocations=scheduler.allocations_per_slot,
        campaign_impacts=campaign_impacts,
        eco_rates=eco_rates
    )

    # Print quick summaries
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    print("\nSpend and slots:")
    for c in campaigns:
        utilization = (c.spent / c.budget * 100) if c.budget > 0 else 0
        print(f"  {c.name}: spend=£{round(c.spent, 2)} ({utilization:.1f}%) slots={len(c.scheduled_slots)}")

    print("\nDaily allocation totals:")
    for day, buckets in sorted(scheduler.daily_allocation_totals.items()):
        row = ", ".join([f"{b}:£{round(amt,2)}" for b, amt in buckets.items()])
        print(f"  {day.isoformat()} → {row}")

    print("\nCampaign allocation totals:")
    for camp, buckets in sorted(scheduler.campaign_allocation_totals.items()):
        row = ", ".join([f"{b}:£{round(amt,2)}" for b, amt in buckets.items()])
        print(f"  {camp} → {row}")

    print("\nEco summary (trees, oceans):")
    total_trees = sum(vals['trees'] for vals in eco_summary.values())
    total_oceans = sum(vals['oceans'] for vals in eco_summary.values())
    for camp, vals in eco_summary.items():
        print(f"  {camp}: trees={vals['trees']:.2f}, oceans={vals['oceans']:.2f}")
    print(f"  TOTAL: trees={total_trees:.2f}, oceans={total_oceans:.2f}")

    # Optional exports (uncomment to use)
    # from ad_scheduler_advanced import export_allocations_csv, export_daily_totals_csv, export_campaign_totals_csv, export_summary_json
    # export_allocations_csv("allocations_per_slot.csv", scheduler.allocations_per_slot)
    # export_daily_totals_csv("daily_totals.csv", scheduler.daily_allocation_totals)
    # export_campaign_totals_csv("campaign_totals.csv", scheduler.campaign_allocation_totals)
    # export_summary_json("summary.json", scheduler, eco_summary)
    
    print("\n" + "="*70)
    print("Workflow complete!")
    print("="*70)
