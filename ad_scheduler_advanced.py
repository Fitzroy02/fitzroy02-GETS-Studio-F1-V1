from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import csv

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
