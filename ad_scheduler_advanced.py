from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import csv
import json

# ----- Revenue Allocation Framework -----

@dataclass
class AllocationPolicy:
    """
    Defines how ad revenue is distributed across stakeholders.
    Percentages (sum can be <= or == 1.0; remainder is unallocated/contingency if < 1.0)
    Example: {"broadcaster": 0.7, "centre": 0.2, "trees": 0.06, "oceans": 0.04}
    """
    shares: Dict[str, float]

@dataclass
class AllocationResult:
    """Currency allocation for one slot with stakeholder breakdown."""
    amounts: Dict[str, float]          # e.g., {"broadcaster": 350.0, "centre": 100.0, "trees": 30.0, "oceans": 20.0}
    total_spend: float                  # cost_per_slot for that slot
    impressions: int                    # audience_size
    dt: datetime
    channel: str
    campaign: str

def apply_allocation(cost: float, impressions: int, dt: datetime, channel: str, campaign: str,
                     policy: AllocationPolicy) -> AllocationResult:
    """Apply allocation policy to a single ad slot spend."""
    amounts = {k: round(cost * v, 2) for k, v in policy.shares.items()}
    return AllocationResult(amounts=amounts, total_spend=round(cost, 2),
                            impressions=impressions, dt=dt, channel=channel, campaign=campaign)

# ----- Domain models -----

@dataclass
class Channel:
    name: str
    base_cpm: float              # cost per 1000 impressions (or per slot if simple)
    max_slots_per_day: Optional[int] = None
    audience_weight: float = 1.0  # relative value multiplier (e.g., prime TV = 1.3)

@dataclass
class EcoImpact:
    trees_per_1000_impressions: float = 0.0
    oceans_score_per_1000: float = 0.0

@dataclass
class AdCampaign:
    name: str
    start_date: datetime
    end_date: datetime
    budget: float                 # currency budget
    priority: int                 # scheduling priority (higher first)
    target_impressions: Optional[int] = None
    channel_weights: Dict[str, float] = field(default_factory=dict)  # e.g., {"TV": 0.5, "Radio": 0.3, "Online": 0.2}
    cost_per_slot: Dict[str, float] = field(default_factory=dict)    # e.g., {"TV": 500, "Radio": 120, "Online": 60}
    frequency_cap_per_day: Optional[int] = None
    pacing: str = "even"          # "even" or "frontload" or "backload"
    eco_impact: EcoImpact = field(default_factory=EcoImpact)
    metadata: Dict[str, str] = field(default_factory=dict)

    # runtime state
    spent: float = 0.0
    scheduled_slots: List[Tuple['AdSlot', float]] = field(default_factory=list)  # (slot, cost)

    def is_active(self, dt: datetime) -> bool:
        return self.start_date <= dt <= self.end_date and self.spent < self.budget

    def can_afford(self, channel_name: str) -> bool:
        return self.spent + self.cost_per_slot.get(channel_name, float('inf')) <= self.budget

@dataclass
class AdSlot:
    dt: datetime
    duration_minutes: int
    channel_name: str
    audience_size: int            # impressions estimate
    assigned_campaign: Optional[AdCampaign] = None

# ----- Governance policies -----

@dataclass
class FairnessPolicy:
    # e.g., minimum % of slots for community/impact campaigns
    min_share_for_tags: Dict[str, float] = field(default_factory=dict)  # tag -> minimum fraction
    campaign_tags: Dict[str, List[str]] = field(default_factory=dict)   # campaign_name -> [tags]

    def tag_for(self, campaign_name: str) -> List[str]:
        return self.campaign_tags.get(campaign_name, [])

# ----- Ecological Impact Framework -----

@dataclass
class EcoRates:
    """
    Currency-to-impact conversion rates.
    Defines how allocated currency translates to ecological outcomes.
    Example: £1 in "trees" bucket = 0.1 trees planted
    """
    trees_per_currency: float = 0.0
    oceans_score_per_currency: float = 0.0

def eco_rollup_from_allocations(allocations: List[AllocationResult],
                                campaign_impacts: Dict[str, EcoImpact],
                                eco_rates: EcoRates = EcoRates()) -> Dict[str, Dict[str, float]]:
    """
    Calculate total ecological impact from allocations using dual methodology:
    1. Impression-based: Uses campaign's eco_impact rates (trees/oceans per 1000 impressions)
    2. Currency-based: Uses eco_rates to convert allocated currency to impact
    
    Returns {campaign: {"trees": x, "oceans": y}}
    """
    totals = defaultdict(lambda: {"trees": 0.0, "oceans": 0.0})
    
    for alloc in allocations:
        c_name = alloc.campaign
        eco = campaign_impacts.get(c_name, EcoImpact())
        
        # Impression-based ecological impact
        trees_impr = (alloc.impressions / 1000.0) * eco.trees_per_1000_impressions
        oceans_impr = (alloc.impressions / 1000.0) * eco.oceans_score_per_1000
        
        # Currency-based impact (from allocated trees/oceans buckets)
        trees_amt = alloc.amounts.get("trees", 0.0) * eco_rates.trees_per_currency
        oceans_amt = alloc.amounts.get("oceans", 0.0) * eco_rates.oceans_score_per_currency
        
        # Combined total
        totals[c_name]["trees"] += trees_impr + trees_amt
        totals[c_name]["oceans"] += oceans_impr + oceans_amt
    
    return totals

# ----- Export Utilities -----

def export_allocations_csv(path: str, allocations: List[AllocationResult]):
    """Export detailed per-slot allocation data to CSV."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["datetime", "channel", "campaign", "impressions", "total_spend", "broadcaster", "centre", "trees", "oceans"])
        for a in allocations:
            w.writerow([
                a.dt.isoformat(),
                a.channel,
                a.campaign,
                a.impressions,
                a.total_spend,
                round(a.amounts.get("broadcaster", 0.0), 2),
                round(a.amounts.get("centre", 0.0), 2),
                round(a.amounts.get("trees", 0.0), 2),
                round(a.amounts.get("oceans", 0.0), 2),
            ])

def export_daily_totals_csv(path: str, daily_totals):
    """Export daily revenue allocation totals to CSV."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["day", "bucket", "amount"])
        for day, buckets in sorted(daily_totals.items()):
            for bucket, amt in buckets.items():
                w.writerow([day.isoformat(), bucket, round(amt, 2)])

def export_campaign_totals_csv(path: str, campaign_totals):
    """Export per-campaign revenue allocation totals to CSV."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["campaign", "bucket", "amount"])
        for campaign, buckets in sorted(campaign_totals.items()):
            for bucket, amt in buckets.items():
                w.writerow([campaign, bucket, round(amt, 2)])

def export_summary_json(path: str, scheduler: 'MultiChannelScheduler', eco_summary: Dict[str, Dict[str, float]]):
    """Export comprehensive scheduler summary including allocations and ecological impact to JSON."""
    data = {
        "campaign_spend": {
            c.name: round(c.spent, 2) for c in scheduler.campaigns
        },
        "campaign_slots": {
            c.name: len(c.scheduled_slots) for c in scheduler.campaigns
        },
        "daily_allocation_totals": {
            day.isoformat(): {b: round(amt, 2) for b, amt in buckets.items()}
            for day, buckets in scheduler.daily_allocation_totals.items()
        },
        "campaign_allocation_totals": {
            camp: {b: round(amt, 2) for b, amt in buckets.items()}
            for camp, buckets in scheduler.campaign_allocation_totals.items()
        },
        "eco_summary": eco_summary,
        "timestamp": datetime.now().isoformat()
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ----- Advanced Scheduler -----

class AdvancedScheduler:
    def __init__(
        self,
        campaigns: List[AdCampaign],
        slots: List[AdSlot],
        channels: List[Channel],
        fairness_policy: Optional[FairnessPolicy] = None
    ):
        self.campaigns = campaigns
        self.slots = slots
        self.channels = {ch.name: ch for ch in channels}
        self.fairness_policy = fairness_policy or FairnessPolicy()

    def schedule_ads(self):
        """Main scheduling logic with governance constraints."""
        # Sort campaigns by priority (highest first)
        sorted_campaigns = sorted(self.campaigns, key=lambda c: c.priority, reverse=True)
        
        # Track slots by tag for fairness enforcement
        tag_slot_counts = {tag: 0 for tag in self.fairness_policy.min_share_for_tags.keys()}
        total_slots = len(self.slots)
        
        for slot in self.slots:
            for campaign in sorted_campaigns:
                if not campaign.is_active(slot.dt):
                    continue
                
                if not campaign.can_afford(slot.channel_name):
                    continue
                
                # Check frequency cap
                if campaign.frequency_cap_per_day:
                    slots_today = sum(
                        1 for s, _ in campaign.scheduled_slots
                        if s.dt.date() == slot.dt.date()
                    )
                    if slots_today >= campaign.frequency_cap_per_day:
                        continue
                
                # Assign slot
                if self._assign_slot(slot, campaign):
                    # Update tag counts
                    for tag in self.fairness_policy.tag_for(campaign.name):
                        if tag in tag_slot_counts:
                            tag_slot_counts[tag] += 1
                    break
        
        # Report fairness compliance
        self._report_fairness(tag_slot_counts, total_slots)

    def _assign_slot(self, slot: AdSlot, campaign: AdCampaign) -> bool:
        """Assign a slot to a campaign and deduct budget."""
        if slot.assigned_campaign:
            return False
        
        cost = campaign.cost_per_slot.get(slot.channel_name, 0)
        slot.assigned_campaign = campaign
        campaign.spent += cost
        campaign.scheduled_slots.append((slot, cost))
        return True

    def _report_fairness(self, tag_slot_counts: Dict[str, int], total_slots: int):
        """Report on fairness policy compliance."""
        print("\n--- Fairness Policy Compliance ---")
        for tag, required_fraction in self.fairness_policy.min_share_for_tags.items():
            actual_count = tag_slot_counts[tag]
            actual_fraction = actual_count / total_slots if total_slots > 0 else 0
            required_count = int(required_fraction * total_slots)
            status = "✓" if actual_fraction >= required_fraction else "✗"
            print(f"{status} {tag}: {actual_count}/{total_slots} slots "
                  f"({actual_fraction:.1%}) - Required: {required_fraction:.1%}")

    def generate_report(self) -> Dict:
        """Generate comprehensive scheduling report."""
        total_spent = sum(c.spent for c in self.campaigns)
        total_impressions = sum(
            slot.audience_size 
            for c in self.campaigns 
            for slot, _ in c.scheduled_slots
        )
        
        # Calculate eco impact
        total_trees = sum(
            c.eco_impact.trees_per_1000_impressions * 
            sum(slot.audience_size for slot, _ in c.scheduled_slots) / 1000
            for c in self.campaigns
        )
        
        report = {
            "total_budget_spent": total_spent,
            "total_impressions": total_impressions,
            "total_trees_planted": total_trees,
            "campaigns": []
        }
        
        for campaign in self.campaigns:
            campaign_impressions = sum(slot.audience_size for slot, _ in campaign.scheduled_slots)
            report["campaigns"].append({
                "name": campaign.name,
                "spent": campaign.spent,
                "budget": campaign.budget,
                "utilization": f"{campaign.spent/campaign.budget:.1%}" if campaign.budget > 0 else "N/A",
                "slots_scheduled": len(campaign.scheduled_slots),
                "impressions": campaign_impressions,
                "trees_planted": campaign.eco_impact.trees_per_1000_impressions * campaign_impressions / 1000
            })
        
        return report

    def export_schedule_csv(self, filename: str):
        """Export the schedule to CSV format."""
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['DateTime', 'Channel', 'Duration (min)', 'Campaign', 'Audience Size', 'Cost'])
            
            for slot in sorted(self.slots, key=lambda s: s.dt):
                if slot.assigned_campaign:
                    cost = slot.assigned_campaign.cost_per_slot.get(slot.channel_name, 0)
                    writer.writerow([
                        slot.dt.strftime('%Y-%m-%d %H:%M'),
                        slot.channel_name,
                        slot.duration_minutes,
                        slot.assigned_campaign.name,
                        slot.audience_size,
                        f"£{cost:.2f}"
                    ])
                else:
                    writer.writerow([
                        slot.dt.strftime('%Y-%m-%d %H:%M'),
                        slot.channel_name,
                        slot.duration_minutes,
                        'Empty',
                        slot.audience_size,
                        '£0.00'
                    ])

# ----- Multi-Channel Scheduler with Pacing & Fairness Optimization -----

class MultiChannelScheduler:
    """
    Enhanced scheduler with:
    - Pacing algorithms (even/frontload/backload)
    - Fairness pressure scoring
    - Audience utility optimization
    - Dynamic campaign scoring per slot
    - Real-time revenue allocation tracking
    """
    def __init__(self, campaigns: List[AdCampaign], channels: Dict[str, Channel], slots: List[AdSlot],
                 fairness: Optional[FairnessPolicy] = None):
        self.campaigns = campaigns
        self.channels = channels
        self.slots = sorted(slots, key=lambda s: (s.dt, -channels[s.channel_name].audience_weight))
        self.fairness = fairness or FairnessPolicy()
        self.daily_counts = defaultdict(lambda: defaultdict(int))  # campaign -> day -> count
        self.tag_counts = defaultdict(int)                         # tag -> assigned slot count
        self.total_slots = len(self.slots)
        
        # Revenue allocation tracking
        self.allocations_per_slot: List[AllocationResult] = []
        self.daily_allocation_totals = defaultdict(lambda: defaultdict(float))  # day -> bucket -> amount
        self.campaign_allocation_totals = defaultdict(lambda: defaultdict(float))  # campaign -> bucket -> amount

    def _pacing_score(self, campaign: AdCampaign, slot_dt: datetime) -> float:
        """Calculate pacing multiplier based on campaign pacing strategy."""
        total_days = max(1, (campaign.end_date.date() - campaign.start_date.date()).days + 1)
        day_index = (slot_dt.date() - campaign.start_date.date()).days
        # even: flat; frontload: earlier days higher; backload: later days higher
        if campaign.pacing == "frontload":
            return max(0.1, (total_days - day_index) / total_days)
        if campaign.pacing == "backload":
            return max(0.1, (day_index + 1) / total_days)
        return 1.0

    def _frequency_ok(self, campaign: AdCampaign, slot_dt: datetime) -> bool:
        """Check if campaign hasn't exceeded daily frequency cap."""
        if campaign.frequency_cap_per_day is None:
            return True
        day = slot_dt.date()
        return self.daily_counts[campaign.name][day] < campaign.frequency_cap_per_day

    def _fairness_pressure(self, campaign: AdCampaign) -> float:
        """
        Increase score if campaign helps meet a fairness minimum.
        Applies pressure to prioritize under-represented tags.
        """
        tags = self.fairness.tag_for(campaign.name)
        pressure = 1.0
        for t in tags:
            min_share = self.fairness.min_share_for_tags.get(t)
            if min_share is None:
                continue
            current_share = self.tag_counts[t] / max(1, self.total_slots)
            if current_share < min_share:
                pressure *= 1.2  # boost; tune as needed
        return pressure

    def _campaign_slot_score(self, campaign: AdCampaign, slot: AdSlot) -> float:
        """
        Calculate dynamic score for assigning a campaign to a slot.
        Considers: channel preference, pacing, fairness, audience utility.
        """
        ch = self.channels[slot.channel_name]
        weight = campaign.channel_weights.get(slot.channel_name, 0.0)
        if weight <= 0:
            return 0.0
        pacing = self._pacing_score(campaign, slot.dt)
        fairness = self._fairness_pressure(campaign)
        # Audience utility: impressions * channel audience weight
        audience_util = slot.audience_size * ch.audience_weight
        return weight * pacing * fairness * audience_util

    def schedule(self):
        """Execute optimized scheduling with dynamic scoring and real-time allocation tracking."""
        # Sort campaigns by priority (desc), then name for stability
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
                
                # Fairness tag increment
                for t in self.fairness.tag_for(best_campaign.name):
                    self.tag_counts[t] += 1

                # Revenue allocation step (uses per-campaign policy; default if missing)
                policy = best_campaign.metadata.get("allocation_policy")
                if policy is None:
                    # Default allocation: broadcaster 70%, centre 20%, trees 6%, oceans 4%
                    policy = AllocationPolicy(shares={"broadcaster": 0.7, "centre": 0.2, "trees": 0.06, "oceans": 0.04})
                    best_campaign.metadata["allocation_policy"] = policy

                alloc = apply_allocation(
                    cost=cost,
                    impressions=slot.audience_size,
                    dt=slot.dt,
                    channel=slot.channel_name,
                    campaign=best_campaign.name,
                    policy=policy,
                )
                self.allocations_per_slot.append(alloc)

                # Roll up daily and campaign totals
                for bucket, amt in alloc.amounts.items():
                    self.daily_allocation_totals[day][bucket] += amt
                    self.campaign_allocation_totals[best_campaign.name][bucket] += amt

    def export_csv(self, path: str):
        """Export schedule with detailed slot and campaign information."""
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

    def report_fairness(self):
        """Report fairness policy compliance."""
        print("\n--- Fairness Policy Compliance (MultiChannelScheduler) ---")
        for tag, required_fraction in self.fairness.min_share_for_tags.items():
            actual_count = self.tag_counts[tag]
            actual_fraction = actual_count / self.total_slots if self.total_slots > 0 else 0
            status = "✓" if actual_fraction >= required_fraction else "✗"
            print(f"{status} {tag}: {actual_count}/{self.total_slots} slots "
                  f"({actual_fraction:.1%}) - Required: {required_fraction:.1%}")

    def calculate_revenue_allocation(self, policy: AllocationPolicy) -> Dict:
        """
        Calculate revenue allocation across stakeholders based on allocation policy.
        Returns breakdown by stakeholder and summary totals.
        """
        allocations = []
        stakeholder_totals = defaultdict(float)
        
        for slot in self.slots:
            if slot.assigned_campaign:
                c = slot.assigned_campaign
                cost = c.cost_per_slot.get(slot.channel_name, 0.0)
                result = apply_allocation(
                    cost=cost,
                    impressions=slot.audience_size,
                    dt=slot.dt,
                    channel=slot.channel_name,
                    campaign=c.name,
                    policy=policy
                )
                allocations.append(result)
                
                # Accumulate stakeholder totals
                for stakeholder, amount in result.amounts.items():
                    stakeholder_totals[stakeholder] += amount
        
        total_revenue = sum(stakeholder_totals.values())
        
        return {
            "allocations": allocations,
            "stakeholder_totals": dict(stakeholder_totals),
            "total_revenue": round(total_revenue, 2),
            "policy_shares": policy.shares
        }

    def export_revenue_allocation_csv(self, path: str, policy: AllocationPolicy):
        """Export detailed revenue allocation showing stakeholder distribution per slot."""
        allocation_data = self.calculate_revenue_allocation(policy)
        
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Get stakeholder names from policy
            stakeholders = list(policy.shares.keys())
            header = ["datetime", "channel", "campaign", "total_cost", "impressions"] + stakeholders
            writer.writerow(header)
            
            for alloc in allocation_data["allocations"]:
                row = [
                    alloc.dt.isoformat(),
                    alloc.channel,
                    alloc.campaign,
                    alloc.total_spend,
                    alloc.impressions
                ] + [alloc.amounts.get(sh, 0.0) for sh in stakeholders]
                writer.writerow(row)
            
            # Write summary row
            writer.writerow([])
            writer.writerow(["TOTALS", "", "", allocation_data["total_revenue"], ""] + 
                          [allocation_data["stakeholder_totals"].get(sh, 0.0) for sh in stakeholders])

    def export_revenue_summary_json(self, path: str, policy: AllocationPolicy):
        """Export revenue allocation summary as JSON."""
        allocation_data = self.calculate_revenue_allocation(policy)
        
        summary = {
            "total_revenue": allocation_data["total_revenue"],
            "stakeholder_breakdown": allocation_data["stakeholder_totals"],
            "policy_shares": allocation_data["policy_shares"],
            "total_slots": len(allocation_data["allocations"]),
            "timestamp": datetime.now().isoformat()
        }
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

    def report_daily_allocation(self):
        """Report daily revenue allocation breakdown."""
        if not self.daily_allocation_totals:
            print("No allocation data available. Run schedule() first.")
            return
        
        print("\n--- Daily Revenue Allocation ---")
        sorted_days = sorted(self.daily_allocation_totals.keys())
        
        for day in sorted_days:
            totals = self.daily_allocation_totals[day]
            day_total = sum(totals.values())
            print(f"\n{day.strftime('%Y-%m-%d')} - Total: £{day_total:.2f}")
            for bucket, amount in sorted(totals.items()):
                percentage = (amount / day_total * 100) if day_total > 0 else 0
                print(f"  {bucket}: £{amount:.2f} ({percentage:.1f}%)")

    def report_campaign_allocation(self):
        """Report per-campaign revenue allocation breakdown."""
        if not self.campaign_allocation_totals:
            print("No allocation data available. Run schedule() first.")
            return
        
        print("\n--- Campaign Revenue Allocation ---")
        for campaign_name in sorted(self.campaign_allocation_totals.keys()):
            totals = self.campaign_allocation_totals[campaign_name]
            campaign_total = sum(totals.values())
            print(f"\n{campaign_name} - Total: £{campaign_total:.2f}")
            for bucket, amount in sorted(totals.items()):
                percentage = (amount / campaign_total * 100) if campaign_total > 0 else 0
                print(f"  {bucket}: £{amount:.2f} ({percentage:.1f}%)")

    def get_allocation_summary(self) -> Dict:
        """Get comprehensive allocation summary with daily and campaign breakdowns."""
        total_allocated = sum(
            sum(bucket_amounts.values()) 
            for bucket_amounts in self.daily_allocation_totals.values()
        )
        
        # Aggregate all buckets
        bucket_totals = defaultdict(float)
        for day_buckets in self.daily_allocation_totals.values():
            for bucket, amount in day_buckets.items():
                bucket_totals[bucket] += amount
        
        return {
            "total_allocated": round(total_allocated, 2),
            "bucket_totals": {k: round(v, 2) for k, v in bucket_totals.items()},
            "daily_breakdown": {
                day.strftime('%Y-%m-%d'): {k: round(v, 2) for k, v in buckets.items()}
                for day, buckets in self.daily_allocation_totals.items()
            },
            "campaign_breakdown": {
                campaign: {k: round(v, 2) for k, v in buckets.items()}
                for campaign, buckets in self.campaign_allocation_totals.items()
            },
            "total_slots_allocated": len(self.allocations_per_slot)
        }

    def calculate_ecological_impact(self, eco_rates: EcoRates = None) -> Dict:
        """
        Calculate total ecological impact using dual methodology:
        - Impression-based: from campaign eco_impact settings
        - Currency-based: from allocated trees/oceans buckets using eco_rates
        
        Returns comprehensive impact summary with per-campaign breakdown.
        """
        if eco_rates is None:
            # Default: £1 allocated to trees = 0.1 trees planted, £1 to oceans = 0.05 ocean score
            eco_rates = EcoRates(trees_per_currency=0.1, oceans_score_per_currency=0.05)
        
        # Build campaign impacts map
        campaign_impacts = {c.name: c.eco_impact for c in self.campaigns}
        
        # Calculate using rollup function
        campaign_eco = eco_rollup_from_allocations(
            self.allocations_per_slot,
            campaign_impacts,
            eco_rates
        )
        
        # Calculate totals
        total_trees = sum(impacts["trees"] for impacts in campaign_eco.values())
        total_oceans = sum(impacts["oceans"] for impacts in campaign_eco.values())
        
        # Get currency allocated to eco buckets
        total_trees_currency = sum(
            buckets.get("trees", 0.0) 
            for buckets in self.campaign_allocation_totals.values()
        )
        total_oceans_currency = sum(
            buckets.get("oceans", 0.0) 
            for buckets in self.campaign_allocation_totals.values()
        )
        
        return {
            "total_trees": round(total_trees, 2),
            "total_oceans_score": round(total_oceans, 2),
            "trees_currency_allocated": round(total_trees_currency, 2),
            "oceans_currency_allocated": round(total_oceans_currency, 2),
            "eco_rates": {
                "trees_per_currency": eco_rates.trees_per_currency,
                "oceans_per_currency": eco_rates.oceans_score_per_currency
            },
            "per_campaign": {
                campaign: {
                    "trees": round(impacts["trees"], 2),
                    "oceans": round(impacts["oceans"], 2)
                }
                for campaign, impacts in campaign_eco.items()
            }
        }

    def report_ecological_impact(self, eco_rates: EcoRates = None):
        """Report comprehensive ecological impact with dual methodology."""
        impact = self.calculate_ecological_impact(eco_rates)
        
        print("\n--- Ecological Impact Summary ---")
        print(f"Total Trees Planted: {impact['total_trees']:.2f}")
        print(f"  - From Currency (£{impact['trees_currency_allocated']:.2f} × {impact['eco_rates']['trees_per_currency']}): "
              f"{impact['trees_currency_allocated'] * impact['eco_rates']['trees_per_currency']:.2f}")
        print(f"  - From Impressions: {impact['total_trees'] - impact['trees_currency_allocated'] * impact['eco_rates']['trees_per_currency']:.2f}")
        
        print(f"\nTotal Ocean Restoration Score: {impact['total_oceans_score']:.2f}")
        print(f"  - From Currency (£{impact['oceans_currency_allocated']:.2f} × {impact['eco_rates']['oceans_per_currency']}): "
              f"{impact['oceans_currency_allocated'] * impact['eco_rates']['oceans_per_currency']:.2f}")
        print(f"  - From Impressions: {impact['total_oceans_score'] - impact['oceans_currency_allocated'] * impact['eco_rates']['oceans_per_currency']:.2f}")
        
        print("\nPer-Campaign Impact:")
        for campaign, impacts in impact['per_campaign'].items():
            print(f"  {campaign}:")
            print(f"    Trees: {impacts['trees']:.2f}")
            print(f"    Oceans: {impacts['oceans']:.2f}")

# ----- Example Usage -----

if __name__ == "__main__":
    # Define channels
    channels = [
        Channel(name="TV", base_cpm=15.0, max_slots_per_day=10, audience_weight=1.3),
        Channel(name="Radio", base_cpm=8.0, max_slots_per_day=20, audience_weight=1.0),
        Channel(name="Online", base_cpm=3.0, max_slots_per_day=50, audience_weight=0.8),
    ]
    
    # Define campaigns with eco impact
    campaigns = [
        AdCampaign(
            name="Eco Tree Project",
            start_date=datetime(2025, 12, 7),
            end_date=datetime(2025, 12, 14),
            budget=5000,
            priority=2,
            cost_per_slot={"TV": 500, "Radio": 120, "Online": 60},
            frequency_cap_per_day=3,
            eco_impact=EcoImpact(trees_per_1000_impressions=2.5, oceans_score_per_1000=1.2),
            metadata={"tags": "community,ecological"}
        ),
        AdCampaign(
            name="Centre Funding Drive",
            start_date=datetime(2025, 12, 7),
            end_date=datetime(2025, 12, 10),
            budget=3000,
            priority=3,
            cost_per_slot={"TV": 500, "Radio": 120, "Online": 60},
            frequency_cap_per_day=4,
            eco_impact=EcoImpact(trees_per_1000_impressions=1.0, oceans_score_per_1000=0.5),
            metadata={"tags": "community"}
        ),
        AdCampaign(
            name="Commercial Brand",
            start_date=datetime(2025, 12, 7),
            end_date=datetime(2025, 12, 14),
            budget=8000,
            priority=1,
            cost_per_slot={"TV": 500, "Radio": 120, "Online": 60},
            eco_impact=EcoImpact(trees_per_1000_impressions=0.5, oceans_score_per_1000=0.2),
            metadata={"tags": "commercial"}
        ),
    ]
    
    # Define fairness policy: 25% of slots for community campaigns
    fairness_policy = FairnessPolicy(
        min_share_for_tags={"community": 0.25, "ecological": 0.10},
        campaign_tags={
            "Eco Tree Project": ["community", "ecological"],
            "Centre Funding Drive": ["community"],
            "Commercial Brand": ["commercial"]
        }
    )
    
    # Generate slots for 7 days across multiple channels
    slots = []
    for day in range(7):
        base_date = datetime(2025, 12, 7) + timedelta(days=day)
        # TV slots (prime time)
        for hour in [19, 20, 21]:
            slots.append(AdSlot(
                dt=datetime(2025, 12, 7 + day, hour),
                duration_minutes=30,
                channel_name="TV",
                audience_size=50000
            ))
        # Radio slots (morning drive)
        for hour in [7, 8, 9]:
            slots.append(AdSlot(
                dt=datetime(2025, 12, 7 + day, hour),
                duration_minutes=60,
                channel_name="Radio",
                audience_size=20000
            ))
        # Online slots (all day)
        for hour in range(8, 22):
            slots.append(AdSlot(
                dt=datetime(2025, 12, 7 + day, hour),
                duration_minutes=5,
                channel_name="Online",
                audience_size=5000
            ))
    
    # Run scheduler
    scheduler = AdvancedScheduler(campaigns, slots, channels, fairness_policy)
    scheduler.schedule_ads()
    
    # Generate and print report
    report = scheduler.generate_report()
    print("\n--- Campaign Performance Report ---")
    print(f"Total Budget Spent: £{report['total_budget_spent']:.2f}")
    print(f"Total Impressions: {report['total_impressions']:,}")
    print(f"Total Trees Planted: {report['total_trees_planted']:.1f}")
    print("\nPer-Campaign Breakdown:")
    for campaign in report['campaigns']:
        print(f"  {campaign['name']}:")
        print(f"    Spent: £{campaign['spent']:.2f} / £{campaign['budget']:.2f} ({campaign['utilization']})")
        print(f"    Slots: {campaign['slots_scheduled']}")
        print(f"    Impressions: {campaign['impressions']:,}")
        print(f"    Trees: {campaign['trees_planted']:.1f}")
    
    # Export to CSV
    scheduler.export_schedule_csv("ad_schedule.csv")
    print("\n✓ Schedule exported to ad_schedule.csv")
    
    # ----- Test MultiChannelScheduler with optimized scoring -----
    print("\n" + "="*60)
    print("Testing MultiChannelScheduler (with pacing & fairness optimization)")
    print("="*60)
    
    # Reset campaign state for new scheduler
    for c in campaigns:
        c.spent = 0.0
        c.scheduled_slots = []
    
    # Add channel weights to campaigns for multi-channel optimization
    campaigns[0].channel_weights = {"TV": 0.5, "Radio": 0.3, "Online": 0.2}  # Eco Tree prefers TV
    campaigns[0].pacing = "frontload"  # Load early in campaign
    
    campaigns[1].channel_weights = {"TV": 0.7, "Radio": 0.2, "Online": 0.1}  # Centre Funding heavily TV
    campaigns[1].pacing = "even"
    
    campaigns[2].channel_weights = {"TV": 0.2, "Radio": 0.3, "Online": 0.5}  # Commercial focuses online
    campaigns[2].pacing = "backload"
    
    # Regenerate slots
    slots_multi = []
    for day in range(7):
        base_date = datetime(2025, 12, 7) + timedelta(days=day)
        # TV slots
        for hour in [19, 20, 21]:
            slots_multi.append(AdSlot(
                dt=datetime(2025, 12, 7 + day, hour),
                duration_minutes=30,
                channel_name="TV",
                audience_size=50000
            ))
        # Radio slots
        for hour in [7, 8, 9]:
            slots_multi.append(AdSlot(
                dt=datetime(2025, 12, 7 + day, hour),
                duration_minutes=60,
                channel_name="Radio",
                audience_size=20000
            ))
        # Online slots
        for hour in range(8, 22):
            slots_multi.append(AdSlot(
                dt=datetime(2025, 12, 7 + day, hour),
                duration_minutes=5,
                channel_name="Online",
                audience_size=5000
            ))
    
    # Set custom allocation policies for campaigns
    campaigns[0].metadata["allocation_policy"] = AllocationPolicy(
        shares={"broadcaster": 0.65, "centre": 0.25, "trees": 0.08, "oceans": 0.02}
    )  # Eco Tree: more to centre and trees
    
    campaigns[1].metadata["allocation_policy"] = AllocationPolicy(
        shares={"broadcaster": 0.60, "centre": 0.30, "trees": 0.05, "oceans": 0.05}
    )  # Centre Funding: highest centre allocation
    
    # Commercial Brand will use default policy (70/20/6/4)
    
    # Run MultiChannelScheduler
    multi_scheduler = MultiChannelScheduler(
        campaigns=campaigns,
        channels={ch.name: ch for ch in channels},
        slots=slots_multi,
        fairness=fairness_policy
    )
    multi_scheduler.schedule()
    multi_scheduler.report_fairness()
    
    # Generate report
    print("\n--- MultiChannel Campaign Performance ---")
    total_spent_multi = sum(c.spent for c in campaigns)
    total_impressions_multi = sum(
        slot.audience_size 
        for c in campaigns 
        for slot, _ in c.scheduled_slots
    )
    total_trees_multi = sum(
        c.eco_impact.trees_per_1000_impressions * 
        sum(slot.audience_size for slot, _ in c.scheduled_slots) / 1000
        for c in campaigns
    )
    
    print(f"Total Budget Spent: £{total_spent_multi:.2f}")
    print(f"Total Impressions: {total_impressions_multi:,}")
    print(f"Total Trees Planted: {total_trees_multi:.1f}")
    print("\nPer-Campaign Breakdown:")
    for campaign in campaigns:
        campaign_impressions = sum(slot.audience_size for slot, _ in campaign.scheduled_slots)
        print(f"  {campaign.name}:")
        print(f"    Pacing: {campaign.pacing}")
        print(f"    Spent: £{campaign.spent:.2f} / £{campaign.budget:.2f} ({campaign.spent/campaign.budget:.1%})")
        print(f"    Slots: {len(campaign.scheduled_slots)}")
        print(f"    Impressions: {campaign_impressions:,}")
        print(f"    Trees: {campaign.eco_impact.trees_per_1000_impressions * campaign_impressions / 1000:.1f}")
    
    # Export optimized schedule
    multi_scheduler.export_csv("ad_schedule_optimized.csv")
    print("\n✓ Optimized schedule exported to ad_schedule_optimized.csv")
    
    # ----- Revenue Allocation Demo -----
    print("\n" + "="*60)
    print("Revenue Allocation Analysis")
    print("="*60)
    
    # Define allocation policy: broadcaster 70%, centre 20%, trees 6%, oceans 4%
    allocation_policy = AllocationPolicy(
        shares={
            "broadcaster": 0.70,
            "centre": 0.20,
            "trees": 0.06,
            "oceans": 0.04
        }
    )
    
    print("\nAllocation Policy:")
    for stakeholder, share in allocation_policy.shares.items():
        print(f"  {stakeholder}: {share:.1%}")
    
    # Calculate allocation
    allocation_data = multi_scheduler.calculate_revenue_allocation(allocation_policy)
    
    print(f"\nTotal Revenue: £{allocation_data['total_revenue']:.2f}")
    print("\nStakeholder Breakdown:")
    for stakeholder, amount in allocation_data['stakeholder_totals'].items():
        percentage = (amount / allocation_data['total_revenue'] * 100) if allocation_data['total_revenue'] > 0 else 0
        print(f"  {stakeholder}: £{amount:.2f} ({percentage:.1f}%)")
    
    # Export detailed allocation
    multi_scheduler.export_revenue_allocation_csv("ad_schedule_with_allocation.csv", allocation_policy)
    print("\n✓ Revenue allocation exported to ad_schedule_with_allocation.csv")
    
    # Export JSON summary
    multi_scheduler.export_revenue_summary_json("revenue_summary.json", allocation_policy)
    print("✓ Revenue summary exported to revenue_summary.json")
    
    # ----- Real-Time Allocation Tracking Demo -----
    print("\n" + "="*60)
    print("Real-Time Allocation Tracking (Per-Campaign Policies)")
    print("="*60)
    
    # Report allocations by campaign
    multi_scheduler.report_campaign_allocation()
    
    # Report allocations by day
    multi_scheduler.report_daily_allocation()
    
    # Get comprehensive summary
    allocation_summary = multi_scheduler.get_allocation_summary()
    print(f"\n--- Overall Allocation Summary ---")
    print(f"Total Allocated: £{allocation_summary['total_allocated']:.2f}")
    print(f"Slots Allocated: {allocation_summary['total_slots_allocated']}")
    print("\nAggregate Bucket Totals:")
    for bucket, amount in sorted(allocation_summary['bucket_totals'].items()):
        percentage = (amount / allocation_summary['total_allocated'] * 100) if allocation_summary['total_allocated'] > 0 else 0
        print(f"  {bucket}: £{amount:.2f} ({percentage:.1f}%)")
    
    # ----- Ecological Impact with Dual Methodology -----
    print("\n" + "="*60)
    print("Ecological Impact (Impression + Currency-Based)")
    print("="*60)
    
    # Define eco rates: £1 in trees bucket = 0.1 trees, £1 in oceans bucket = 0.05 ocean score
    eco_rates = EcoRates(trees_per_currency=0.1, oceans_score_per_currency=0.05)
    
    print(f"\nEco Conversion Rates:")
    print(f"  Trees: £1 → {eco_rates.trees_per_currency} trees planted")
    print(f"  Oceans: £1 → {eco_rates.oceans_score_per_currency} restoration score")
    
    # Report ecological impact
    multi_scheduler.report_ecological_impact(eco_rates)
    
    # ----- Comprehensive Export Suite -----
    print("\n" + "="*60)
    print("Exporting Comprehensive Reports")
    print("="*60)
    
    # Export detailed allocations (slot-by-slot)
    export_allocations_csv("allocations_detailed.csv", multi_scheduler.allocations_per_slot)
    print("\n✓ Detailed allocations exported to allocations_detailed.csv")
    
    # Export daily totals
    export_daily_totals_csv("allocations_daily.csv", multi_scheduler.daily_allocation_totals)
    print("✓ Daily allocation totals exported to allocations_daily.csv")
    
    # Export campaign totals
    export_campaign_totals_csv("allocations_campaign.csv", multi_scheduler.campaign_allocation_totals)
    print("✓ Campaign allocation totals exported to allocations_campaign.csv")
    
    # Export comprehensive JSON summary with ecological impact
    eco_impact_data = multi_scheduler.calculate_ecological_impact(eco_rates)
    export_summary_json("complete_summary.json", multi_scheduler, eco_impact_data["per_campaign"])
    print("✓ Complete summary with eco impact exported to complete_summary.json")
    
    print("\n" + "="*60)
    print("All exports complete!")
    print("="*60)
