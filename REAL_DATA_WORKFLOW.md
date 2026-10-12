# Real-world data workflow and factual limits

Run `python -m src.nyfed_data --start 2025-01-01 --end 2026-01-01 --output data/nyfed_sofr_historical.csv` to **attempt** downloading published historical fixings from the official New York Fed API. Network access is required and the endpoint is not executed by the offline verification environment.

Validate date coverage (including required fixing immediately prior to your reference period), exchange holiday calendars and revisions before computing historical SR3 settlement with `src.settlement_study.quarter_settlement`. Published SOFR is a realized overnight benchmark, **not historical CME futures quotes**. Never combine future realized SOFR fixings with an earlier trading-date forecast and call it an ex-ante strategy. To study actual futures mispricing, obtain separately dated and licensed CME contract prices and use genuinely contemporaneous forecast inputs.

Sources: [FRBNY Markets Data APIs](https://markets.newyorkfed.org/static/docs/markets-api.html), [CME SR3 conventions](https://www.cmegroup.com/education/articles-and-reports/understanding-sofr-futures). A historical OIS curve requires contemporaneous OIS inputs and convexity modeling; the pedagogical strip is explicitly not a calibrated arbitrage-free curve. SR3 BPV USD 25 / bp / contract.
