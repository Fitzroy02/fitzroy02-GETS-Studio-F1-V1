"""
Report utility functions for generating contributor activity reports.

This module provides helper functions to:
- Filter audit log data by date range (weekly, monthly, lifetime)
- Aggregate activity metrics for selected periods
- Aggregate contribution events for selected periods
- Calculate reward totals and sapling conversion (4,000 points = 1 sapling)
- Generate summary statistics for each report section
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def get_date_boundaries(period: str) -> Tuple[Optional[datetime], datetime]:
    """
    Calculate date boundaries for filtering audit log entries.
    
    Args:
        period: One of 'weekly', 'monthly', or 'lifetime'
        
    Returns:
        Tuple of (start_date, end_date). start_date is None for lifetime.
    """
    end_date = datetime.utcnow()
    
    if period == 'weekly':
        start_date = end_date - timedelta(days=7)
    elif period == 'monthly':
        start_date = end_date - timedelta(days=30)
    elif period == 'lifetime':
        start_date = None
    else:
        raise ValueError(f"Invalid period: {period}. Must be 'weekly', 'monthly', or 'lifetime'")
    
    return start_date, end_date


def load_audit_log(audit_log_path: Path) -> List[Dict]:
    """
    Load and parse audit log entries from JSONL file.
    
    Args:
        audit_log_path: Path to the audit log JSONL file
        
    Returns:
        List of audit log entries as dictionaries
    """
    entries = []
    
    if not audit_log_path.exists():
        return entries
    
    try:
        with audit_log_path.open('r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    entries.append(entry)
                except json.JSONDecodeError:
                    # Skip malformed entries defensively
                    continue
    except Exception:
        # Return empty list if file can't be read
        return []
    
    return entries


def filter_entries_by_date(entries: List[Dict], start_date: Optional[datetime]) -> List[Dict]:
    """
    Filter audit log entries by date range.
    
    Args:
        entries: List of audit log entries
        start_date: Start date for filtering (None for lifetime/all entries)
        
    Returns:
        Filtered list of entries
    """
    if start_date is None:
        return entries
    
    filtered = []
    for entry in entries:
        timestamp_str = entry.get('timestamp')
        if not timestamp_str:
            continue
        
        try:
            # Parse ISO format timestamp (with or without 'Z')
            timestamp_str = timestamp_str.rstrip('Z')
            timestamp = datetime.fromisoformat(timestamp_str)
            
            if timestamp >= start_date:
                filtered.append(entry)
        except (ValueError, AttributeError):
            # Skip entries with invalid timestamps
            continue
    
    return filtered


def aggregate_activity_metrics(entries: List[Dict]) -> Dict:
    """
    Aggregate activity metrics from audit log entries.
    
    Args:
        entries: List of filtered audit log entries
        
    Returns:
        Dictionary with activity metrics:
        - sessions: Number of unique sessions
        - time_spent: Estimated time spent (placeholder)
        - pages_visited: Number of page views
    """
    sessions = set()
    pages_visited = 0
    
    for entry in entries:
        action = entry.get('action', '')
        
        # Count sessions (page views indicate sessions)
        if 'page_view' in action or 'visit' in action:
            pages_visited += 1
            user = entry.get('user')
            timestamp = entry.get('timestamp', '')
            # Use combination of user and rounded timestamp for session identification
            if user and timestamp:
                # Round to nearest 30 minutes to group into sessions
                sessions.add(f"{user}_{timestamp[:16]}")  # YYY-MM-DDTHH:MM
        
        # Count export actions as page visits too
        if 'export' in action or 'download' in action:
            pages_visited += 1
    
    # Estimate time spent (rough approximation: 2 minutes per page view)
    time_spent_minutes = pages_visited * 2
    
    return {
        'sessions': len(sessions) if sessions else max(1, pages_visited // 3),  # Fallback: ~3 pages per session
        'time_spent_minutes': time_spent_minutes,
        'pages_visited': pages_visited,
    }


def aggregate_contribution_metrics(entries: List[Dict]) -> Dict:
    """
    Aggregate contribution metrics from audit log entries.
    
    Args:
        entries: List of filtered audit log entries
        
    Returns:
        Dictionary with contribution metrics:
        - items_added: Number of items created/added
        - items_reviewed: Number of items reviewed/verified
        - community_tasks: Number of community tasks completed
    """
    items_added = 0
    items_reviewed = 0
    community_tasks = 0
    
    for entry in entries:
        action = entry.get('action', '').lower()
        
        # Count items added
        if any(keyword in action for keyword in ['add', 'create', 'submit', 'upload']):
            items_added += 1
        
        # Count items reviewed
        if any(keyword in action for keyword in ['review', 'verify', 'approve', 'check']):
            items_reviewed += 1
        
        # Count community tasks
        if any(keyword in action for keyword in ['export', 'share', 'help', 'feedback', 'report']):
            community_tasks += 1
    
    return {
        'items_added': items_added,
        'items_reviewed': items_reviewed,
        'community_tasks': community_tasks,
    }


def calculate_rewards(entries: List[Dict]) -> Dict:
    """
    Calculate reward totals and sapling conversion from audit log entries.
    
    Args:
        entries: List of filtered audit log entries
        
    Returns:
        Dictionary with reward metrics:
        - points_earned: Total points earned in this period
        - saplings: Sapling equivalent (points / 4000)
        - contribution_count: Number of point-earning contributions
    """
    points_earned = 0
    contribution_count = 0
    
    # Points are awarded for various contribution actions
    # Using a simple point system based on action types
    for entry in entries:
        action = entry.get('action', '').lower()
        details = entry.get('details', {})
        
        # Check if points are explicitly recorded
        if 'points' in details:
            points_earned += details.get('points', 0)
            contribution_count += 1
        else:
            # Award points based on action type
            points = 0
            if any(keyword in action for keyword in ['add', 'create', 'submit']):
                points = 100  # Adding new content
            elif any(keyword in action for keyword in ['review', 'verify', 'approve']):
                points = 50  # Reviewing content
            elif any(keyword in action for keyword in ['export', 'share']):
                points = 25  # Community engagement
            
            if points > 0:
                points_earned += points
                contribution_count += 1
    
    # Calculate saplings (4,000 points = 1 sapling)
    saplings = points_earned / 4000.0
    
    return {
        'points_earned': points_earned,
        'saplings': round(saplings, 2),
        'contribution_count': contribution_count,
    }


def generate_report_summary(audit_log_path: Path, period: str) -> Dict:
    """
    Generate a complete report summary for the specified period.
    
    Args:
        audit_log_path: Path to the audit log JSONL file
        period: One of 'weekly', 'monthly', or 'lifetime'
        
    Returns:
        Dictionary containing:
        - period: Selected period
        - date_range: Human-readable date range
        - activity: Activity metrics dictionary
        - contributions: Contribution metrics dictionary
        - rewards: Reward metrics dictionary
    """
    start_date, end_date = get_date_boundaries(period)
    entries = load_audit_log(audit_log_path)
    filtered_entries = filter_entries_by_date(entries, start_date)
    
    # Format date range for display
    if start_date:
        date_range = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
    else:
        date_range = "All Time"
    
    return {
        'period': period.capitalize(),
        'date_range': date_range,
        'activity': aggregate_activity_metrics(filtered_entries),
        'contributions': aggregate_contribution_metrics(filtered_entries),
        'rewards': calculate_rewards(filtered_entries),
        'total_entries': len(filtered_entries),
    }


def format_time_spent(minutes: int) -> str:
    """
    Format time spent in a human-readable format.
    
    Args:
        minutes: Time in minutes
        
    Returns:
        Formatted string (e.g., "2h 30m", "45m")
    """
    if minutes < 60:
        return f"{minutes}m"
    else:
        hours = minutes // 60
        mins = minutes % 60
        if mins > 0:
            return f"{hours}h {mins}m"
        else:
            return f"{hours}h"
