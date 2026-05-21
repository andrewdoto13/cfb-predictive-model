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

#### Weighted EPA / Contextual Efficiency

Raw EPA treats all plays equally, but a play in the 4th quarter with 2 minutes left and a 7-point deficit is far more important than a garbage-time play in the 3rd quarter. Weighting EPA by game context captures **performance quality when it matters** — a signal that most public models ignore.

**Weighting dimensions:**

| Dimension | Weighting | Rationale |
|-----------|-----------|-----------|
| **Game context** | Higher weight in 3rd/4th quarter | These plays decide games |
| **Score differential** | Higher weight when game is within 10 points | Garbage-time EPA is noise |
| **Situational importance** | Higher weight in red zone, 3rd/4th down, goal line | Higher leverage situations |
| **Opponent strength** | Higher weight against stronger opponents | Performing well against bad teams is less informative |

**Concrete features to compute:**

| Feature | Description | Formula |
|---------|-------------|---------|
| **Weighted EPA per play** | EPA × importance weight, averaged | `sum(EPA × weight) / count` |
| **Clutch EPA** | EPA from games within 7 points in the 4th quarter | Filter plays by score diff ≤ 7 AND quarter = 4 |
| **Leverage EPA** | EPA weighted by game importance | `sum(EPA × weight) / sum(weight)` |
| **Late-game success rate** | Success rate in final 5 minutes, score within 10 | Filter plays by time ≤ 5:00 AND score diff ≤ 10 |
| **Red zone leverage EPA** | EPA weighted by red zone importance | `EPA × 1.3` for all plays inside the 20 |

**Weighting function (reference implementation):**

```python
def epa_weight(play, game_state):
    """Weight EPA by how important the play was."""
    weight = 1.0
    
    # Game context: 4th quarter matters more
    if game_state.quarter == 4:
        weight *= 1.3
    elif game_state.quarter == 3:
        weight *= 1.1
    
    # Clutch: closer games matter more
    score_diff = abs(game_state.home_score - game_state.away_score)
    if score_diff <= 7:
        weight *= 1.4
    elif score_diff <= 14:
        weight *= 1.1
    
    # Situational: red zone and 3rd/4th down
    if game_state.yard_line <= 20:  # red zone
        weight *= 1.3
    if game_state.down in [3, 4] and game_state.yards_to_go <= 4:
        weight *= 1.2
    
    return weight
```

**Why this matters:**
- **Clutch performance** is a real skill — some teams elevate in important moments, others fold
- **EPA already encodes game state** (down, distance, field position, score), but doesn't weight *when* those situations occur
- A team that accumulates EPA on meaningless drives but fails in the red zone late in close games is fundamentally different from a team that's efficient everywhere

**Data requirements:** Play-by-play data with game state (score, quarter, time remaining) — CFBD paid tier or SportsDataverse.

### 2.4 Recruiting Features

| Feature | Description |
|---------|-------------|
| Recruiting class ranking | 247Sports Composite team ranking |
| Returning production % | % of offensive/defensive production returning |
| Star count | Number of 4- and 5-star recruits |
| Recruiting differential | Home team ranking minus away team ranking |
| Transfer portal additions | Net transfer portal impact |

### 2.5 Coaching & Roster Features

Roster-derived features capture **structural team factors** that EPA and ratings often miss or react to slowly. A team losing 3+ OL starters has a rough year even if the skill players are the same — but EPA won't reflect that until they actually play badly.

#### Coaching Features

|| Feature | Description |
|---------|-------------|
| Head coach experience | Years in current role, career win % |
| Offensive/Defensive coordinator | Tenure, scheme type |
| Coordinator continuity | Same OC/DC from prior year? (boolean) |
| Coaching turnover | New head coach in first year? |

#### Roster-Derived Features

These are some of the most predictive features you can add — they tell you about team **structure** before the games even happen.

| Feature | Description | Signal |
|---------|-------------|--------|
| **OL returning experience** | % of OL snaps returned from prior year | Biggest roster predictor — losing 3+ OL starters = rough year |
| **OL average age / weight** | Physical profile of the line | 300+ lb LT vs 270 lb LT changes dynamics vs elite pass rushers |
| **OL star returners** | Number of returning All-Conference OL | Quality matters as much as quantity |
| **Skill position turnover** | % of receiving/rushing yards returned | Losing your top 2 WRs is a bigger hit than losing a backup RB |
| **QB experience** | Returning starter vs. transfer vs. freshman | Returning starter is ~3-5% more accurate predictor than raw EPA |
| **DL experience** | Returning DL snaps, especially interior rushers | Interior pressure drives pass rush more than edge speed |
| **Portal net impact** | # transfers in minus # transfers out | Net positive portal class = roster upgrade |
| **Returning production %** | % of offensive/defensive yards and TDs returned | The single best roster turnover metric |
| **Depth chart changes** | # of position changes from prior year | Instability at key positions = growing pains |
| **Injuries (active)** | Key player absences (if available) | Missing a starting QB or LB is a big deal |

**Highest-signal roster features (start here):**

1. **Returning production %** — easiest to get, very predictive
2. **QB experience** — returning starter flag, very high signal
3. **OL returning experience** — slightly harder to get, but extremely predictive

**Data sources for roster features:**

| Source | What You Get | Access |
|--------|-------------|--------|
| **247Sports / On3** | Roster lists, recruiting rankings, transfer tracker, player bios | Paid API / scraping |
| **ESPN** | Depth charts, player bios, injury reports | Free (scraping) |
| **CFBD** | Recruiting rankings, some roster data | Free tier limited, paid full |
| **Team websites** | Official depth charts, roster lists | Free (scraping) |
| **Sports-Reference** | Returning production data | Free (scraping) |

**Why roster features work:**
- **EPA doesn't know** a team's QB is a freshman until they play badly — roster data tells you *before* the season
- **Size matters** in college football — a massive OL dominates at the point of attack, even if EPA doesn't reflect it yet
- **Roster turnover is a lagging indicator** — EPA reacts to results, roster data predicts them
- **Chemistry matters** — a new OL unit needs time to develop, even if the talent level is similar

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
│ 3. Compute weighted EPA         │  ← clutch EPA, leverage EPA (NEW)
│ 4. Aggregate to team level      │  ← rolling averages, season totals
│ 5. Add opponent context         │  ← opponent-adjusted metrics
│ 6. Add ratings                  │  ← Elo, SP+, FEI, FPI
│ 7. Add betting lines            │  ← spread, O/U, moneyline
│ 8. Add roster features          │  ← OL experience, QB status (NEW)
│ 9. Add context                  │  ← rest, travel, weather, rivalry
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
4. **Build Weighted EPA** — re-weight existing EPA by game context (clutch, leverage, late-game)
5. **Build a LightGBM model** — it handles mixed feature types well and is fast to train
6. **Evaluate against Elo baseline** — track accuracy, log-loss, Brier score
7. **Add roster features** — start with returning production % and QB experience
8. **Iterate** — add OL experience, DL experience, portal impact, weather, and schedule features

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
