from datetime import date
import math
import pandas as pd
import pytest
from src.pricing import sr1_index,sr3_index,strip_curve,pnl_sr3,third_wednesday,shift_price,_accruals,hypothetical_fair_value_strip

def sample():
    return pd.DataFrame({'date':['2026-06-17','2026-06-18','2026-06-19','2026-06-22'],'sofr_pct':[4.,4.,4.,4.]})

def test_sr1_simple_average_calendar_weighting():
    d=sample();d.loc[d.date=='2026-06-19','sofr_pct']=5.
    # 19/20/21 June carry 5%, 22 June 4% -> (4+4+5*3+4)/6
    assert sr1_index(d,'2026-06-17','2026-06-23')==pytest.approx(100-(4+4+5*3+4)/6)

def test_sr3_composite_uses_weekend_simple_interest():
    d=sample(); price=sr3_index(d,'2026-06-17','2026-06-23')
    product=(1+.04/360)**2*(1+3*.04/360)*(1+.04/360)
    expected=100-(product-1)*360/6*100
    assert price==pytest.approx(expected)

def test_duplicate_or_missing_first_fixing_rejected():
    with pytest.raises(ValueError):sr3_index(sample(),'2026-06-16','2026-06-23')
    with pytest.raises(ValueError):sr1_index(pd.concat([sample(),sample()]),'2026-06-17','2026-06-23')

def test_shock_and_bpv():
    assert shift_price(95.5,25)==pytest.approx(95.25)
    assert pnl_sr3(95.5,95.25)==pytest.approx(-625.)
    assert third_wednesday(2026,6).date()==date(2026,6,17)

def test_contiguous_strip_and_df():
    x=pd.DataFrame({'contract':['A','B'],'start':['2026-06-17','2026-09-16'],'end':['2026-09-16','2026-12-16'],'market_price':[96.,96.1]})
    out=strip_curve(x)
    assert out.projection_df_proxy.iloc[1] < out.projection_df_proxy.iloc[0] < 1
    assert out.plus_25bp_pnl_one_long_usd.iloc[0]==pytest.approx(-625)
    x.loc[1,'start']='2026-09-17'
    with pytest.raises(ValueError):strip_curve(x)


def test_independent_hypothetical_fair_values_and_upshock():
    dates=pd.bdate_range('2026-06-16','2026-12-16')
    rates=pd.DataFrame({'date':dates,'sofr_pct':[4.]*len(dates)})
    strip=pd.DataFrame({'contract':['A'],'start':['2026-06-17'],'end':['2026-09-16'],'market_price':[96.1]})
    baseline=hypothetical_fair_value_strip(rates,strip)
    shifted=hypothetical_fair_value_strip(rates,strip,scenario_rate_shock_bp=25)
    assert baseline.model_fair_index.iloc[0] < 96.1
    assert shifted.model_fair_index.iloc[0] < baseline.model_fair_index.iloc[0]
    assert baseline.fair_minus_market_quote_bp.iloc[0]==pytest.approx((baseline.model_fair_index.iloc[0]-96.1)*100)
