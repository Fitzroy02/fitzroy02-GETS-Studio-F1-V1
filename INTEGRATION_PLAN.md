# 🔄 Live Dashboard Integration Plan

## Overview

Transform the README governance dashboard from static content into a **living, breathing civic-poetic board** that updates automatically based on real contributor activity, CI runs, token redemptions, and ecological claims.

---

## 🎯 Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA SOURCES (Live Signals)              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ GitHub       │  │ Points       │  │ Ecological   │    │
│  │ Actions      │  │ Database     │  │ Claims API   │    │
│  │              │  │              │  │              │    │
│  │ • CI Status  │  │ • User pts   │  │ • Redemptions│    │
│  │ • Build logs │  │ • Author pts │  │ • Trees      │    │
│  │ • Test runs  │  │ • Role stats │  │ • Pending    │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                  │                  │            │
└─────────┼──────────────────┼──────────────────┼────────────┘
          │                  │                  │
          v                  v                  v
┌─────────────────────────────────────────────────────────────┐
│              AGGREGATION LAYER (Python Scripts)             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  update_dashboard.py                                        │
│  ├── fetch_ci_status()      → GitHub API                   │
│  ├── fetch_points_data()    → SQLite/Supabase/Sheets       │
│  ├── fetch_ecological()     → OneTreePlanted API           │
│  └── generate_readme()      → Template → README.md         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
          │
          v
┌─────────────────────────────────────────────────────────────┐
│                 AUTOMATED UPDATES (Workflows)               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  .github/workflows/update-dashboard.yml                     │
│  • Trigger: Every 6 hours (cron schedule)                   │
│  • Trigger: On push to main                                 │
│  • Trigger: Manual dispatch                                 │
│  • Action: Run update_dashboard.py                          │
│  • Action: Commit updated README.md                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔌 Data Source Integrations

### 1. **GitHub Actions (CI Status)**

**Purpose**: Auto-update Build badge (✅ 100%) based on workflow runs

**Implementation**:
```python
# scripts/update_dashboard.py

import requests
import os

def fetch_ci_status():
    """Fetch latest CI status from GitHub Actions API"""
    token = os.getenv('GITHUB_TOKEN')
    repo = 'Fitzroy02/fitzroy02-GETS-Studio-F1-V1'
    
    headers = {'Authorization': f'token {token}'}
    url = f'https://api.github.com/repos/{repo}/actions/runs?per_page=1'
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    if data['workflow_runs']:
        latest_run = data['workflow_runs'][0]
        status = latest_run['conclusion']  # 'success', 'failure', etc.
        
        return {
            'status': 'passing' if status == 'success' else 'failing',
            'percentage': 100 if status == 'success' else 0,
            'badge_color': '28A745' if status == 'success' else 'DC3545'
        }
    
    return {'status': 'unknown', 'percentage': 0, 'badge_color': '6C757D'}
```

**GitHub Workflow Hook**:
```yaml
# .github/workflows/update-dashboard.yml
name: Update Dashboard

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install requests pyyaml
      
      - name: Update dashboard
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          POINTS_DB_URL: ${{ secrets.POINTS_DB_URL }}
          ECOLOGICAL_API_KEY: ${{ secrets.ECOLOGICAL_API_KEY }}
        run: python scripts/update_dashboard.py
      
      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add README.md
          git diff --quiet && git diff --staged --quiet || \
            git commit -m "🤖 Auto-update dashboard [skip ci]"
          git push
```

---

### 2. **Points Database (Token Economy)**

**Purpose**: Track role-based points and redemptions

**Option A: SQLite (Simple, Local)**
```python
import sqlite3

def init_points_db():
    """Initialize SQLite database for points tracking"""
    conn = sqlite3.connect('data/points.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS points (
            id INTEGER PRIMARY KEY,
            user_id TEXT,
            role TEXT,  -- 'user', 'author', 'partitioner', 'student_patient'
            points INTEGER DEFAULT 0,
            eligible BOOLEAN DEFAULT 0,
            redeemed BOOLEAN DEFAULT 0,
            redemption_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            user_id TEXT,
            points INTEGER,
            action TEXT,  -- 'earn', 'redeem'
            description TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def fetch_points_data():
    """Aggregate points data by role"""
    conn = sqlite3.connect('data/points.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            role,
            SUM(points) as total_points,
            COUNT(CASE WHEN points >= 500 THEN 1 END) as eligible,
            COUNT(CASE WHEN redeemed = 1 THEN 1 END) as redeemed,
            COUNT(CASE WHEN points >= 500 AND redeemed = 0 THEN 1 END) as pending
        FROM points
        GROUP BY role
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    return {
        row[0]: {
            'points': row[1],
            'eligible': row[2],
            'redeemed': row[3],
            'pending': row[4]
        } for row in results
    }
```

**Option B: Supabase (Cloud, Scalable)**
```python
from supabase import create_client

def fetch_points_data_supabase():
    """Fetch points data from Supabase"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    supabase = create_client(url, key)
    
    response = supabase.table('points') \
        .select('role, points, eligible, redeemed') \
        .execute()
    
    # Aggregate by role
    role_stats = {}
    for record in response.data:
        role = record['role']
        if role not in role_stats:
            role_stats[role] = {'points': 0, 'eligible': 0, 'redeemed': 0, 'pending': 0}
        
        role_stats[role]['points'] += record['points']
        if record['points'] >= 500:
            role_stats[role]['eligible'] += 1
            if not record['redeemed']:
                role_stats[role]['pending'] += 1
        if record['redeemed']:
            role_stats[role]['redeemed'] += 1
    
    return role_stats
```

**Option C: Google Sheets (Accessible, Collaborative)**
```python
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def fetch_points_data_sheets():
    """Fetch points data from Google Sheets"""
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'credentials.json', scope)
    client = gspread.authorize(creds)
    
    sheet = client.open('GETS Points Ledger').sheet1
    records = sheet.get_all_records()
    
    role_stats = {}
    for record in records:
        role = record['role']
        if role not in role_stats:
            role_stats[role] = {'points': 0, 'eligible': 0, 'redeemed': 0, 'pending': 0}
        
        role_stats[role]['points'] += record['points']
        if record['eligible']:
            role_stats[role]['eligible'] += 1
        if record['redeemed']:
            role_stats[role]['redeemed'] += 1
        if record['eligible'] and not record['redeemed']:
            role_stats[role]['pending'] += 1
    
    return role_stats
```

---

### 3. **Ecological Claims API (Tree Planting)**

**Purpose**: Track actual tree redemptions and planting status

**Implementation**:
```python
def fetch_ecological_data():
    """Fetch tree planting data from OneTreePlanted or custom API"""
    # Option 1: OneTreePlanted API (if partnership exists)
    api_key = os.getenv('ONETREEPLANTED_API_KEY')
    headers = {'Authorization': f'Bearer {api_key}'}
    
    response = requests.get(
        'https://api.onetreeplanted.org/v1/projects/gets-compliance',
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        return {
            'trees_claimed': data['trees_planted'],
            'pending_claims': data['pending_claims'],
            'total_impact': data['carbon_offset_kg']
        }
    
    # Option 2: Internal tracking database
    conn = sqlite3.connect('data/points.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as trees_claimed,
            SUM(CASE WHEN redeemed = 0 AND points >= 500 THEN 1 ELSE 0 END) as pending
        FROM points
    ''')
    
    result = cursor.fetchone()
    conn.close()
    
    return {
        'trees_claimed': result[0],
        'pending_claims': result[1]
    }
```

---

## 📝 README Template System

**Purpose**: Generate README.md dynamically from live data

```python
# scripts/templates/readme_template.md

# ⚖️ GETS Compliance Studio

[![License: CSL](https://img.shields.io/badge/License-CSL-007ACC.svg)](LICENSE)
![Build Status](https://img.shields.io/badge/Build-{{ ci_status }}-{{ ci_badge_color }}.svg)
![Stewardship](https://img.shields.io/badge/Stewardship-anchored-6C757D.svg)
![Accessible](https://img.shields.io/badge/Accessible-true-FFB400.svg)
![Audit Ready](https://img.shields.io/badge/Audit-Ready-C2185B.svg)
![Trees Linked](https://img.shields.io/badge/Trees-Linked-2E7D32.svg)
![Community Safe](https://img.shields.io/badge/Community-Safe-673AB7.svg)

\```
                    ✨ Vision ✨
        "Vision is not sound without clarity"
                 (Ethos & Motto)
                        |
                        v
                 📊 Status Dashboard
   (Health, Progress, Stewardship, Ecology, Accessibility, Safety)
                        |
                        v
                 ⚡ Quickstart
   (Clone → Run Governance → Load Media + Metadata)
           1. git clone & pip install -r requirements.txt
           2. streamlit run streamlit_app.py
           3. python example_usage.py
                        |
                        v
                 ✨ Back to Vision ✨
   (Clarity renewed through practice, stewardship embodied)
\```

...

## 📒 Points Ledger

| Role / Participant   | Points Earned (10 pts each) | Eligible (≥500 pts) | Redeemed (Trees Claimed) | Pending Claims |
|----------------------|-----------------------------|----------------------|---------------------------|----------------|
| **Users**            | {{ users_points }}          | {{ users_eligible }} | {{ users_redeemed }}      | {{ users_pending }} |
| **Authors**          | {{ authors_points }}        | {{ authors_eligible }}| {{ authors_redeemed }}    | {{ authors_pending }} |
| **Partitioners**     | {{ partitioners_points }}   | {{ partitioners_eligible }}| {{ partitioners_redeemed }} | {{ partitioners_pending }} |
| **Students / Patients** | {{ students_points }}    | {{ students_eligible }}| {{ students_redeemed }}   | {{ students_pending }} |
| **Total**            | {{ total_points }}          | {{ total_eligible }} | {{ total_redeemed }}      | {{ total_pending }} |

### 📊 Visual Progress Bars

\```
Users              [{{ users_bar }}] {{ users_points }} pts
                   Eligible: {{ users_eligible }} | Redeemed: {{ users_redeemed }} | Pending: {{ users_pending }}

Authors            [{{ authors_bar }}] {{ authors_points }} pts
                   Eligible: {{ authors_eligible }} | Redeemed: {{ authors_redeemed }} | Pending: {{ authors_pending }}

Partitioners       [{{ partitioners_bar }}] {{ partitioners_points }} pts
                   Eligible: {{ partitioners_eligible }} | Redeemed: {{ partitioners_redeemed }} | Pending: {{ partitioners_pending }}

Students/Patients  [{{ students_bar }}] {{ students_points }} pts
                   Eligible: {{ students_eligible }} | Redeemed: {{ students_redeemed }} | Pending: {{ students_pending }}
\```

---

*Last updated: {{ timestamp }} | Auto-generated by [update_dashboard.py](scripts/update_dashboard.py)*
```

**Template Renderer**:
```python
from jinja2 import Template
from datetime import datetime

def generate_progress_bar(points, max_points=2500):
    """Generate ASCII progress bar based on points"""
    bar_length = 50
    filled = int((points / max_points) * bar_length)
    return '█' * filled

def generate_readme(ci_data, points_data, ecological_data):
    """Generate README.md from template with live data"""
    with open('scripts/templates/readme_template.md', 'r') as f:
        template = Template(f.read())
    
    # Calculate progress bars
    max_points = max([v['points'] for v in points_data.values()])
    
    rendered = template.render(
        # CI data
        ci_status=ci_data['status'],
        ci_badge_color=ci_data['badge_color'],
        
        # Users
        users_points=points_data.get('user', {}).get('points', 0),
        users_eligible=points_data.get('user', {}).get('eligible', 0),
        users_redeemed=points_data.get('user', {}).get('redeemed', 0),
        users_pending=points_data.get('user', {}).get('pending', 0),
        users_bar=generate_progress_bar(points_data.get('user', {}).get('points', 0), max_points),
        
        # Authors
        authors_points=points_data.get('author', {}).get('points', 0),
        authors_eligible=points_data.get('author', {}).get('eligible', 0),
        authors_redeemed=points_data.get('author', {}).get('redeemed', 0),
        authors_pending=points_data.get('author', {}).get('pending', 0),
        authors_bar=generate_progress_bar(points_data.get('author', {}).get('points', 0), max_points),
        
        # Partitioners
        partitioners_points=points_data.get('partitioner', {}).get('points', 0),
        partitioners_eligible=points_data.get('partitioner', {}).get('eligible', 0),
        partitioners_redeemed=points_data.get('partitioner', {}).get('redeemed', 0),
        partitioners_pending=points_data.get('partitioner', {}).get('pending', 0),
        partitioners_bar=generate_progress_bar(points_data.get('partitioner', {}).get('points', 0), max_points),
        
        # Students/Patients
        students_points=points_data.get('student_patient', {}).get('points', 0),
        students_eligible=points_data.get('student_patient', {}).get('eligible', 0),
        students_redeemed=points_data.get('student_patient', {}).get('redeemed', 0),
        students_pending=points_data.get('student_patient', {}).get('pending', 0),
        students_bar=generate_progress_bar(points_data.get('student_patient', {}).get('points', 0), max_points),
        
        # Totals
        total_points=sum([v['points'] for v in points_data.values()]),
        total_eligible=sum([v['eligible'] for v in points_data.values()]),
        total_redeemed=sum([v['redeemed'] for v in points_data.values()]),
        total_pending=sum([v['pending'] for v in points_data.values()]),
        
        # Metadata
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M UTC')
    )
    
    with open('README.md', 'w') as f:
        f.write(rendered)
```

---

## 🚀 Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Create `scripts/update_dashboard.py` main orchestrator
- [ ] Set up SQLite database for points tracking
- [ ] Create README template with Jinja2 placeholders
- [ ] Test manual dashboard updates

### Phase 2: CI Integration (Week 3)
- [ ] Create `.github/workflows/update-dashboard.yml`
- [ ] Implement `fetch_ci_status()` using GitHub API
- [ ] Auto-update Build badge on CI runs
- [ ] Test automated commits

### Phase 3: Points System (Week 4-5)
- [ ] Design points earning rules (10 pts per interaction)
- [ ] Create API endpoints for points tracking
- [ ] Implement `fetch_points_data()` aggregator
- [ ] Build role-based dashboards

### Phase 4: Ecological API (Week 6)
- [ ] Partner with OneTreePlanted or similar
- [ ] Create redemption webhook
- [ ] Implement `fetch_ecological_data()`
- [ ] Link redemptions to tree planting

### Phase 5: Real-Time Polish (Week 7-8)
- [ ] Add caching layer (Redis) for API calls
- [ ] Implement rate limiting
- [ ] Create manual override system
- [ ] Add historical trend charts

---

## 🔐 Security Considerations

1. **API Keys**: Store in GitHub Secrets, never commit
2. **Database Access**: Use read-only credentials for dashboard updates
3. **Rate Limiting**: Cache API responses (6-hour refresh)
4. **Webhook Validation**: Verify signatures for external APIs
5. **Audit Logging**: Track all dashboard updates

---

## 📊 Success Metrics

Once live, measure:
- **Update Frequency**: Dashboard refreshes every 6 hours
- **Data Freshness**: CI status < 5 minutes old
- **Redemption Rate**: Track pending claims reduction
- **Contributor Engagement**: Monitor points accumulation velocity
- **Ecological Impact**: Trees claimed per week

---

## 🎯 Future Enhancements

- **Real-time WebSocket updates** for instant dashboard refresh
- **GraphQL API** for contributor-facing queries
- **Mobile app** showing personalized point progress
- **Gamification**: Badges for milestone achievements
- **Social proof**: Top contributors leaderboard (opt-in)

---

*This living integration plan ensures the README becomes a dynamic governance board, not static documentation.*
