# Data provenance and reproducibility

**All `data/` CSV files shipped with this repository are artificially simulated examples.** They are generated for deterministic demonstration/testing, not observations from CME, a broker, an exchange, a quoted security, or a market-data vendor. Never report their backtest results as historical investment performance. These synthetic datasets were generated with `numpy.random.default_rng(20261012)` in the project-building workflow; the seed is recorded here for reproducibility.

To use sourced real market data, replace the CSV while retaining the existing input column names and checking instrument specifications, calendars, data licenses, adjustments and the timing of signals. The repo's independent tests use only local fixtures.

The sample futures strip quotes and SOFR fixings are *independent illustrative paths*; they are not calibrated to one another or quoted market screens.
