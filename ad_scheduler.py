from datetime import datetime, timedelta

class AdCampaign:
    def __init__(self, name, start_date, end_date, budget, priority):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.budget = budget
        self.priority = priority
        self.scheduled_slots = []

    def is_active(self, date):
        return self.start_date <= date <= self.end_date and self.budget > 0

class AdSlot:
    def __init__(self, slot_time, duration_minutes):
        self.slot_time = slot_time
        self.duration_minutes = duration_minutes
        self.assigned_campaign = None

    def assign_campaign(self, campaign):
        if not self.assigned_campaign:
            self.assigned_campaign = campaign
            campaign.scheduled_slots.append(self)
            campaign.budget -= 1  # deduct cost per slot
            return True
        return False

class Scheduler:
    def __init__(self, campaigns, slots):
        self.campaigns = campaigns
        self.slots = slots

    def schedule_ads(self):
        # Sort campaigns by priority (highest first)
        sorted_campaigns = sorted(self.campaigns, key=lambda c: c.priority, reverse=True)
        for slot in self.slots:
            for campaign in sorted_campaigns:
                if campaign.is_active(slot.slot_time):
                    if slot.assign_campaign(campaign):
                        break  # move to next slot once filled

# Example usage
if __name__ == "__main__":
    # Define campaigns
    campaigns = [
        AdCampaign("Eco Project", datetime(2025, 12, 7), datetime(2025, 12, 14), budget=5, priority=2),
        AdCampaign("Centre Funding", datetime(2025, 12, 7), datetime(2025, 12, 10), budget=3, priority=3),
    ]

    # Define slots (every hour for one day)
    slots = [AdSlot(datetime(2025, 12, 7, hour), 30) for hour in range(8, 20)]

    # Run scheduler
    scheduler = Scheduler(campaigns, slots)
    scheduler.schedule_ads()

    # Print results
    for slot in slots:
        if slot.assigned_campaign:
            print(f"{slot.slot_time.strftime('%Y-%m-%d %H:%M')} → {slot.assigned_campaign.name}")
        else:
            print(f"{slot.slot_time.strftime('%Y-%m-%d %H:%M')} → Empty")
