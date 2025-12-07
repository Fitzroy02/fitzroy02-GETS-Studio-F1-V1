# Canonical Ordering Reference

## Overview
The GETS Studio Ad Scheduler uses **canonical ordering** to ensure consistent presentation of channels and stakeholder buckets across all reports, exports, and visualizations.

## Constants

### Channel Order
```python
CHANNEL_ORDER = ["TV", "Radio", "Online"]
```
- TV: Highest reach, premium pricing (£500/slot)
- Radio: Mid-tier reach, moderate pricing (£120/slot)
- Online: Targeted reach, entry pricing (£60/slot)

### Bucket Order
```python
BUCKET_ORDER = ["broadcaster", "centre", "trees", "oceans"]
```
- **broadcaster**: Revenue retained by broadcaster for operations/reinvestment
- **centre**: Direct funding to GETS Community Centre operations
- **trees**: Allocation for tree-planting ecological impact (via EcoRates)
- **oceans**: Allocation for ocean cleanup/restoration (via EcoRates)

## Helper Functions

### `channel_rank(name: str) -> int`
Returns the index position of a channel in `CHANNEL_ORDER`, or `len(CHANNEL_ORDER)` if not found.

**Usage Example:**
```python
channels_sorted = sorted(channels, key=lambda ch: channel_rank(ch.name))
```

## Application

Canonical ordering is enforced throughout the system:

### CSV Exports
- **allocations_detailed.csv**: Header follows `BUCKET_ORDER` (broadcaster, centre, trees, oceans)
- **allocations_daily.csv**: Buckets appear in `BUCKET_ORDER` for each day
- **allocations_campaign.csv**: Buckets appear in `BUCKET_ORDER` for each campaign

### JSON Exports
- **complete_summary.json**: Uses `OrderedDict` to maintain `BUCKET_ORDER` in nested structures
  - `daily_allocation_totals`: Each day's buckets ordered canonically
  - `campaign_allocation_totals`: Each campaign's buckets ordered canonically

### Console Reports
- **report_daily_allocation()**: Prints buckets in `BUCKET_ORDER`
- **report_campaign_allocation()**: Prints buckets in `BUCKET_ORDER`

## Benefits

1. **Consistency**: All reports show data in same order, reducing confusion
2. **Comparability**: Easy to compare reports from different runs or time periods
3. **Predictability**: Users know where to look for specific metrics
4. **Maintainability**: Single source of truth (`BUCKET_ORDER`, `CHANNEL_ORDER`) prevents drift
5. **Professional Presentation**: Clean, organized output builds stakeholder confidence

## Example Output

### CSV Format
```csv
day,bucket,amount
2025-12-07,broadcaster,1845.0
2025-12-07,centre,585.0
2025-12-07,trees,165.0
2025-12-07,oceans,105.0
```

### JSON Format
```json
{
  "daily_allocation_totals": {
    "2025-12-07": {
      "broadcaster": 1845.0,
      "centre": 585.0,
      "trees": 165.0,
      "oceans": 105.0
    }
  }
}
```

### Console Output
```
2025-12-07 - Total: £2700.00
  broadcaster: £1845.00 (68.3%)
  centre: £585.00 (21.7%)
  trees: £165.00 (6.1%)
  oceans: £105.00 (3.9%)
```

---

**Last Updated:** 2025-01-XX  
**Version:** 1.0  
**Related Files:** `ad_scheduler_advanced.py`, `example_complete_workflow.py`
