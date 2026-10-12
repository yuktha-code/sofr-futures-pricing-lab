# SKILLS DEMONSTRATED — SOFR Futures Pricing & Rate-Risk Engine

## Languages, libraries, quantitative methods and tools

Python; Pandas/NumPy; ACT/360 arithmetic vs business-day compounding; SR1/SR3 exchange quotation conventions; yield-curve proxy; futures vs forwards/convexity caveat; DV01-style bp shock and dollar P&L; hypothetical forecast vs quote comparison; parser validation; pytest; GitHub Actions; Matplotlib.

## Verified implementation vs unverified claims

SR1 and SR3 rate-index computations on synthetic fixings; CME $25/bp SR3 risk; third-Wednesday contract calendar; contiguous strip validation; independently assumed forward overnight path; optional NY Fed API client with mocked parser tests; 12 local tests. There is no live CME quote data or empirically calibrated OIS curve.

## Interview questions you should be able to answer

Why is SR3 priced 100 minus compounded SOFR? How do weekends accrue? Explain $25/bp per long contract; distinguish futures-implied rates from actual risk-neutral forwards; know what the independent forecast is and why it is hypothetical.

## How to verify

`python -m pip install -r requirements.txt` then `python -m pytest -q` and `python -m src.demo`. Offline fixtures are **synthetic** and intentionally labeled.
