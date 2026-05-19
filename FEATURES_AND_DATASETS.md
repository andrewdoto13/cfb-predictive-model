# CFB Predictive Model — Datasets & Features Guide

A comprehensive guide to data sources, feature engineering, and advanced analytics for building a state-of-the-art college football prediction model.

---

## 1. DATA SOURCES

### 1.1 Free Tier

| Source | What You Get | Limitations |
|--------|-------------|-------------|
| **CollegeFootballData.com (Free)** | Game results, team stats, box scores, schedules, betting lines, play-by-play (limited), EPA/PPA metrics, recruiting rankings | 1,000 API calls/month, no live data, some advanced metrics gated |
| **Sports-Reference (scraping)** | Historical scores, box scores, team/player stats from 1900s onward | No official API, scraping may break, rate-limited |
| **NCAA.com (ncaa-api)** | Live scores, schedules, standings, box scores, play-by-play | Unofficial, can break with NCAA site changes |
| **SportsDataverse (sdv-py)** | ESPN play-by-play, box scores, schedules, win probability | Free, no rate limits, depends on ESPN API |

### 1.2 Paid Tier

| Source | Price | What You Get |
|--------|-------|-------------|
| **CFBD Starter Pack** | ~$25/mo | Full API access, historical EPA/PPA, drive/play-level data, betting lines, SP+ data, weekly CSV drops |
| **CFBD Premium** | ~$50+/mo | GraphQL API, live data, higher rate limits, basketball API included |
| **The Odds API** | Free tier + paid | Betting odds (moneyline, spreads, totals) from multiple sportsbooks |
| **OddsMatrix** | Custom | Historical odds, live metrics, red zone performance, settlement data |

### 1.3 Recommended Starting Point

**CFBD Free Tier + SportsDataverse** gives you the most coverage without spending money:
- CFBD: game results, team stats, EPA/PPA, betting lines, recruiting
- SportsDataverse: play-by-play data, win probability, box scores

---

## 2. FEATURE CATEGORIES

### 2.1 Basic Score-Based Features (from your current data)

These are the minimum you need — they're in your CSV already:
- `date`, `home_team`, `away_team`, `home_score`, `away_score`

**Derived features you can compute:**
- Point differential (`home_score - away_score`)
- Total points scored
- Margin of victory (binary: win/loss)

### 2.2 Rating-Based Features

| Feature | Description | Source |
|---------|-------------|--------|
| Elo ratings | Your current baseline | Self-computed |
| SP+ | ESPN's predictive efficiency metric (offense + defense) | CFBD API |
| FEI | Football Efficiency Index (college-specific) | CFBD API |
| FPI | Football Power Index (ESPN) | ESPN / CFBD |
| Sagarin | Mathematical ratings used by sportsbooks | CFBD / scraping |
| DRR (Dynamic Rating Rating) | Updated Elo variant | Self-computed |

**How to use:** Take the rating differential (`rating_home - rating_away`) as a feature. You can also use the raw ratings, the log-ratio, or the expected win probability derived from the ratings.

### 2.3 Advanced Analytics (Play-by-Play Level)

These are the **most predictive features** for college football. They come from drive/play-level data.

#### Expected Points Added (EPA) / Predicted Points Added (PPA)
- Measures how much a play changed a team's expected points
- **EPA per play (overall)** — the single most predictive aggregate metric
- **EPA per play (passing)** — passing efficiency
- **EPA per play (rushing)** — rushing efficiency
- **EPA per play (down & distance)** — situational efficiency
- **EPA per play (field position)** — how well teams leverage field position
- **EPA per play (red zone)** — efficiency inside the 20-yard line

#### Success Rate
- Percentage of plays that achieve a "success" threshold (varies by down/distance)
- **Success rate (overall)** — baseline team success
- **Success rate (passing / rushing)** — split by play type
- **Success rate (standard / passing down / goal-to-go)** — situational
- **Power Success** — percentage of short-yardage runs (≤2 yards on 3rd/4th down or inside the 2) converted to a 1st down or TD

#### Explosiveness
- Percentage of plays gaining 10+ yards
- **Explosiveness (overall / passing / rushing)**
- Indicates a team's ability to change games with big plays

#### Drive Efficiency
- Points per drive (overall, by field position)
- Drive starting position average
- Drives per game

#### Other Play-Level Metrics
- **WEP (Win Expectancy Per play)** — how much each play changed win probability
- **Turnover margin** — giveaways minus takeaways
- **Third-down conversion rate** (offense and defense)
- **Red zone conversion rate** (offense and defense)
- **Penalty yardage per game**
- **Time of possession**

### 2.4 Recruiting Features

| Feature | Description |
|---------|-------------|
| Recruiting class ranking | 247Sports Composite team ranking |
| Returning production % | % of offensive/defensive production returning |
| Star count | Number of 4- and 5-star recruits |
| Recruiting differential | Home team ranking minus away team ranking |
| Transfer portal additions | Net transfer portal impact |

### 2.5 Coaching & Roster Features

| Feature | Description |
|---------|-------------|
| Head coach experience | Years in current role, career win % |
| Offensive/Defensive coordinator | Tenure, scheme type |
| Quarterback experience | Returning vs. new starting QB |
| Offensive line experience | Returning starts, snap % |
| Injuries | Key player absences (if available) |

### 2.6 Schedule & Context Features

| Feature | Description |
|---------|-------------|
| Strength of schedule (SOS) | Opponents' combined win % or rating |
| Rest days | Days since last game |
| Travel distance | Miles between last game and current |
| Neutral site | Boolean: is this a neutral field game? |
| Rivalry game | Boolean |
| Conference game | Boolean |
| Bye week | Boolean (week after bye) |
| Weather | Temperature, wind, precipitation (CFBD API) |

### 2.7 Betting Market Features

| Feature | Description |
|---------|-------------|
| Spread | Point spread (market's expected margin) |
| Over/Under | Total points line |
| Moneyline | Implied win probability |
| Line movement | How the spread changed from open to current |
| Public betting % | Where the money is going |

**Why betting lines matter:** The market aggregates enormous information — injuries, weather, public sentiment, sharp money. Using the spread as a feature is one of the strongest signals you can add.

### 2.8 Temporal / Lag Features

Since games happen in sequence over a season, you can engineer time-based features:

| Feature | Description |
|---------|-------------|
| Rolling EPA (last 3/5/10 games) | Recent form |
| Rolling success rate | Recent efficiency |
| Momentum score | Weighted recent performance |
| Week number | Captures seasonal trends |
| Games since last loss | Streak tracking |
| Year-over-year comparison | Same team, different season |

---

## 3. FEATURE ENGINEERING PIPELINE

Here's how to structure your feature computation:

```
Raw Game Data
    │
    ▼
┌─────────────────────────────────┐
│ 1. Compute per-game stats       │  ← score differential, total points
│ 2. Compute per-drive/play stats │  ← EPA, success rate, explosiveness
│ 3. Aggregate to team level      │  ← rolling averages, season totals
│ 4. Add opponent context         │  ← opponent-adjusted metrics
│ 5. Add ratings                  │  ← Elo, SP+, FEI, FPI
│ 6. Add betting lines            │  ← spread, O/U, moneyline
│ 7. Add context                  │  ← rest, travel, weather, rivalry
└─────────────────────────────────┘
    │
    ▼
Feature Matrix (team1 vs team2 per game)
```

**Key principle:** Always compute features using data available **before** the game you're predicting. Never leak future data.

---

## 4. MODEL RECOMMENDATIONS

### Phase 1: Baseline (current)
- **Elo rating system** — your current implementation
- Good for: establishing a baseline, interpretability
- Expected accuracy: ~60-65%

### Phase 2: Statistical Models
- **Logistic regression** with hand-engineered features
- **Gradient Boosting** (XGBoost, LightGBM, CatBoost)
- Good for: leveraging all the advanced features above
- Expected accuracy: ~65-70%

### Phase 3: Advanced
- **Ensemble methods** — combine multiple models
- **Neural networks** — if you have enough data (deepCFB achieves ~84% on validation)
- **Bayesian hierarchical models** — account for team strength uncertainty
- Expected accuracy: ~70-75%

### Phase 4: State of the Art
- **Meta-modeling** — combine predictions from multiple rating systems (CFB metamodel research shows this outperforms any single system)
- **EPA-based simulation** — simulate each game using play-level probabilities
- **Market-adjusted models** — use betting lines as priors, then predict against the market
- Expected accuracy: ~75-80%

---

## 5. QUICK START: FREE DATASET SETUP

If you want to get started immediately with no cost:

1. **Get a free CFBD API key** at https://collegefootballdata.com/
2. **Install the Python client:**
   ```bash
   pip install cfbd
   ```
3. **Pull historical data:**
   ```python
   import cfbd
   
   api_client = cfbd.ApiClient(cfbd.Configuration(api_key={"Authorization": "Bearer YOUR_API_KEY"}))
   
   # Get game results
   games_api = cfbd.GamesApi(api_client)
   games = games_api.get_games(year=2024)
   
   # Get team stats
   stats_api = cfbd.StatsApi(api_client)
   team_stats = stats_api.get_team_stats(year=2024)
   
   # Get betting lines
   betting_api = cfbd.BettingApi(api_client)
   lines = betting_api.get_lines(year=2024)
   
   # Get EPA/PPA metrics
   metrics_api = cfbd.MetricsApi(api_client)
   ppa = metrics_api.get_ppa_team_stats(year=2024)
   ```

4. **Install SportsDataverse for play-by-play:**
   ```bash
   pip install sdv-cfb
   ```

---

## 6. RECOMMENDED NEXT STEPS

1. **Get a CFBD API key** (free tier) and pull 2020-2024 team stats + EPA/PPA
2. **Add betting lines** from CFBD or The Odds API
3. **Engineer rolling features** (3-game, 5-game, 10-game windows)
4. **Build a LightGBM model** — it handles mixed feature types well and is fast to train
5. **Evaluate against Elo baseline** — track accuracy, log-loss, Brier score
6. **Iterate** — add recruiting, weather, and schedule features

---

## References

- [CFBD 10 Tips for Building a CFB Model](https://blog.collegefootballdata.com/college-football-modeling-tips/)
- [CFBD Model Training Pack](https://cdn.collegefootballdata.com/CFBD+Model+Training+Pack+-+Notebook+Fact+Sheet.pdf)
- [CFBD: ML to Predict Spreads (GBDT)](https://blog.collegefootballdata.com/predicting-spreads-gbdt/)
- [cfbfastR Documentation](https://cfbfastr.sportsdataverse.org/)
- [SportsDataverse Python](https://py.sportsdataverse.org/)
- [Graphing College Football](https://graphingcollegefootball.com/)
- [Creating a CFB Win Totals Model (M-FANS)](https://mfootballanalytics.com/2021/08/17/creating-a-college-football-win-totals-model/)
- [College Football Score Prediction (GitHub)](https://github.com/campbelltaylor32/College_Football_Score_Prediction)
- [deepCFB: Deep Learning for CFB (GitHub)](https://github.com/bszek213/deepCFB)
