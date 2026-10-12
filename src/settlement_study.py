"""Verified rate-index mathematics and reproducible historical-fixing research.

Only use strictly full SOFR fixing histories in comparison; absence of a date may
be a holiday OR a missing source record. Real NY Fed data is never bundled by default.
"""
from __future__ import annotations
import math
import pandas as pd
from .pricing import sr1_index,sr3_index,third_wednesday,pnl_sr3

def quarter_bounds(year:int,month:int)->tuple[str,str]:
    if month not in (3,6,9,12): raise ValueError('SR3 quarterly month must be Mar/Jun/Sep/Dec')
    end_year=year+(month==12)
    end_month=3 if month==12 else month+3
    return str(third_wednesday(year,month).date()),str(third_wednesday(end_year,end_month).date())

def quarter_settlement(fixings:pd.DataFrame,year:int,month:int)->dict:
    a,b=quarter_bounds(year,month)
    price=sr3_index(fixings,a,b)
    return {'start':a,'end_exclusive':b,'realized_compounded_rate_pct':100-price,'unrounded_settlement_index':price,
            'long_pnl_from_96_index_usd':pnl_sr3(96.0,price)}

def forward_rate_from_discount_factors(df_start:float,df_end:float,days:int)->float:
    """ACT/360 simple annualized forward, rate *in percent* (not a futures fair value)."""
    if not(0<df_end<=df_start<=1) or days<=0:raise ValueError('Invalid discount factors or accrual days')
    return (df_start/df_end-1)*360/days*100

def future_price_from_projected_rate(rate_pct:float,convexity_adjustment_bp:float=0)->float:
    """Assumed futures-minus-forward adjustment in bp, not a calibrated pricing model."""
    return 100-rate_pct-convexity_adjustment_bp/100

def shocked_futures_pnl(contracts:int,shift_bp:float,side:int=1)->float:
    if side not in(-1,1) or not isinstance(contracts,int) or contracts<0:raise ValueError('bad position')
    return -25*contracts*shift_bp*side
