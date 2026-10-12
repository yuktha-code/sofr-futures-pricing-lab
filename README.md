# SOFR Futures Pricing & Rate-Shock Lab

**Original educational code** for a CME-style short-term interest-rate (STIR) research workflow: 1M and 3M SOFR contract settlement calculations, a contiguous 3M futures strip, **futures-implied period rates**, a *projection-curve proxy*, an **independent hypothetical overnight-rate path versus market quote** fair-value comparison, configurable futures-to-forward convexity adjustment, and $25/bp SR3 shock P&L.

## Finance conventions

- Quote conventions: futures index `100 - annualized_rate_percent`.
- SR1 one-month annualized rate is the **calendar-day arithmetic average** of published SOFR observations with the last known rate carried across weekends/holidays.
- SR3 quarterly annualized rate compounds each **published business-day fixing** over the actual calendar-day accrual interval, using ACT/360: `R = (Π(1 + r_i*d_i/360) − 1) × 360/D` (when `r_i` in decimal; output multiplied by 100). Weekends do **not** compound separately.
- SR3 P&L: `$25` per 1 bp rate change, one contract; `price_change * 100 * 25` USD. A +25 bp rate shock causes −0.25 quote points and −$625 P&L for one *long* futures contract.
- A futures-implied rate **is not automatically an OIS forward**. `convexity_bp` is a user-selected scenario spread, **not a calibrated model**.

## Run

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python -m src.demo
```

Produces `results/projection_curve.csv`, `results/independent_hypothetical_fair_value_vs_quotes.csv`, `results/summary.csv`, `figures/synthetic_curve.png` using **artificial** example rates. Sample strip inputs are explicitly synthetic and must not be presented as historical CME prices.

## Repo design

- `src/pricing.py` — transparent functions and input contracts
- `src/demo.py` — reproducible sample output
- `tests/test_pricing.py` — rate convention, weekend, input validation, bp-value regression tests
- `data/` — synthetic SOFR fixings and prices
- `figures/`, `results/` — outputs

## Limitations

This is a pricing and scenario **prototype**, not exchange-certified settlement, a trading system or a production OIS bootstrapper. Dates should match actual contract reference quarters; the sample rows use weekday business dates, not a certified SIFMA calendar. Fixings are assumed complete except for legitimate market holidays: missing published-business-day rates are not distinguishable from holidays without an external calendar. SR3 exchange rounding, live market feeds, historical already-fixed periods, margin, actual convexity calibration, and OIS instrument calibration are not implemented. The projection discount factors assume consecutive zero-arbitrage period rates and do not represent actual market discount factors.

## References and attribution

Implementation and tests are newly written for this project, not copied from example GitHub repositories. Finance convention references:
- [CME SOFR Futures Settlement Calculation](https://www.cmegroup.com/content/dam/cmegroup/education/files/sofr-futures-settlement-calculation-methodologies.pdf)
- [CME Three-Month SOFR Futures](https://www.cmegroup.com/education/articles-and-reports/three-month-sofr-futures-rates-and-future-sofr-levels)
- [CME Convexity Bias](https://www.cmegroup.com/education/courses/understanding-stir-futures/understanding-convexity-bias.html)

Prior art for *study only*: `attack68/rateslib` (respect its license), `siddharthskulkarni/fixed-income`; no source imported.


## Research upgrade (October 2026)

The accompanying `SKILLS_DEMONSTRATED.md` and `REAL_DATA_WORKFLOW.md` explain tested capabilities and how to supply genuine data. See added optional import/analysis modules in `src/`; synthetic runs are not real-market out-of-sample results.
