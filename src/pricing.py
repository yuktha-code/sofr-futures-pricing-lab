"""Illustrative CME-style SOFR futures calculations. Not an exchange settlement engine."""
from __future__ import annotations
import math
import pandas as pd
import numpy as np

BPV_SR3 = 25.0  # USD per 1 bp of annualized rate per one standard SR3 contract


def _accruals(obs: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """Expand daily accrual dates and carry observed SOFR over nonpublishing days.

    Published fixings are NOT invented. Each unreported calendar day carries
    the most recent provided fixing, assuming omitted days are holidays.
    """
    start, end = pd.Timestamp(start).normalize(), pd.Timestamp(end).normalize()
    if end <= start:
        raise ValueError("end must be after start")
    a = obs.copy()
    if not {"date", "sofr_pct"} <= set(a.columns):
        raise ValueError("expected date, sofr_pct columns")
    a["date"] = pd.to_datetime(a["date"]).dt.normalize()
    if a.date.duplicated().any() or not a.date.is_monotonic_increasing:
        raise ValueError("observation dates must be unique and sorted")
    if a.sofr_pct.isna().any() or not np.isfinite(a.sofr_pct.to_numpy(dtype=float)).all():
        raise ValueError("rates must be finite")
    # Need at least one known fixing on or before first day.
    if a[a.date <= start].empty:
        raise ValueError("missing first-day or prior SOFR fixing")
    dates = pd.date_range(start, end - pd.Timedelta(days=1), freq="D")
    daily = pd.DataFrame({"date": dates})
    daily = pd.merge_asof(daily, a[["date", "sofr_pct"]], on="date", direction="backward")
    if daily.sofr_pct.isna().any():
        raise ValueError("missing fixing coverage")
    return daily


def sr1_index(obs: pd.DataFrame, start: str, end: str) -> float:
    """Unrounded 1M SOFR price: 100 - calendar-day arithmetic mean rate."""
    x = _accruals(obs, start, end)
    return 100.0 - float(x.sofr_pct.mean())


def sr3_index(obs: pd.DataFrame, start: str, end: str) -> float:
    """Unrounded 3M SOFR index using realized business-day SOFR, ACT/360.

    Each published fixing compounds once with the actual number of calendar
    days until the next published fixing or the end of the reference quarter.
    Period start/end must match the contract's reference interval. The routine
    leaves exchange rounding and full holiday-calendar validation to users.
    """
    x = _accruals(obs, start, end)
    # Don't compound daily through weekends: aggregate consecutive equal fixing
    # intervals as one simple ACT/360 interest factor.
    daily = x.reset_index(drop=True)
    # Start at reference-period boundary and group until next published date.
    published = set(pd.to_datetime(obs.date).dt.normalize())
    boundaries = daily.index[daily.date.isin(published)].to_list()
    if not boundaries or boundaries[0] != 0:
        boundaries = [0] + boundaries
    boundaries = sorted(set(boundaries))
    logsum = 0.0
    for j, lo in enumerate(boundaries):
        hi = boundaries[j + 1] if j + 1 < len(boundaries) else len(daily)
        d = hi - lo
        rate = float(daily.sofr_pct.iloc[lo]) / 100.0
        logsum += math.log1p(rate * d / 360.0)
    annualized = math.expm1(logsum) * 360.0 / len(daily) * 100.0
    return 100.0 - annualized


def third_wednesday(year: int, month: int) -> pd.Timestamp:
    first = pd.Timestamp(year=year, month=month, day=1)
    return first + pd.Timedelta(days=((2 - first.weekday()) % 7) + 14)


def futures_implied_rate(price: float) -> float:
    if not (0 < price < 110):
        raise ValueError("invalid SOFR futures index")
    return 100 - float(price)


def shift_price(price: float, rate_shock_bp: float) -> float:
    """+25 bp to the implied rate -> -0.25 futures price index."""
    return price - rate_shock_bp / 100.0


def pnl_sr3(price_before: float, price_after: float, contracts: int = 1) -> float:
    """Standard SR3 $25/bp: one index point = $2,500 per contract."""
    return (float(price_after) - float(price_before)) * 100.0 * BPV_SR3 * contracts


def strip_curve(contracts: pd.DataFrame, convexity_bp: float = 0.0) -> pd.DataFrame:
    """Construct a pedagogical *projection* discount-factor proxy from contiguous SR3.

    Treat the futures rate as a compounded period-forward after optionally
    subtracting a supplied futures-minus-forward adjustment, in basis points.
    Not a fully bootstrapped OIS curve: historical fixings, valuation dates,
    convexity models, cash/discounting differences are outside scope.
    """
    need = {"contract", "start", "end", "market_price"}
    if not need <= set(contracts.columns):
        raise ValueError(f"missing required fields {need-set(contracts.columns)}")
    df = contracts.copy()
    df["start"] = pd.to_datetime(df["start"])
    df["end"] = pd.to_datetime(df["end"])
    df = df.sort_values("start").reset_index(drop=True)
    if (df.end <= df.start).any():
        raise ValueError("nonpositive interval")
    if any(df.loc[i, "start"] != df.loc[i-1, "end"] for i in range(1, len(df))):
        raise ValueError("strip must cover contiguous intervals")
    if not np.isfinite(df.market_price).all():
        raise ValueError("non-finite price")
    df["implied_futures_pct"] = df.market_price.apply(futures_implied_rate)
    df["approx_forward_pct"] = df.implied_futures_pct - convexity_bp / 100
    df["days"] = (df.end - df.start).dt.days
    period_interest = df.approx_forward_pct / 100 * df.days / 360
    if (period_interest <= -1).any():
        raise ValueError("invalid discount factor")
    df["projection_df_proxy"] = (1 / (1 + period_interest)).cumprod()
    df["plus_25bp_price"] = df.market_price.apply(lambda p: shift_price(p, 25))
    df["plus_25bp_pnl_one_long_usd"] = df.apply(lambda z: pnl_sr3(z.market_price, z.plus_25bp_price), axis=1)
    return df


def hypothetical_fair_value_strip(overnight_forecast: pd.DataFrame,
                                  contracts: pd.DataFrame,
                                  scenario_rate_shock_bp: float = 0.0) -> pd.DataFrame:
    """Independently price SR3 periods from an assumed complete overnight-rate path.

    This is a deterministic illustrative model, not an arbitrage-free futures
    valuation or a calibrated risk-neutral forecast. Contrast its projected
    index with *independent* quote inputs, without using quotes to fit path.
    """
    if not np.isfinite(scenario_rate_shock_bp):
        raise ValueError('scenario shock must be finite')
    rates=overnight_forecast.copy()
    rates['sofr_pct']=rates['sofr_pct'].astype(float)+scenario_rate_shock_bp/100.0
    strip=strip_curve(contracts)
    strip['model_fair_index']=[sr3_index(rates, str(r.start.date()),str(r.end.date())) for r in strip.itertuples()]
    strip['fair_minus_market_quote_bp']=(strip.model_fair_index-strip.market_price)*100
    strip['fair_minus_market_usd_one_long']=(strip.model_fair_index-strip.market_price)*2500
    return strip
