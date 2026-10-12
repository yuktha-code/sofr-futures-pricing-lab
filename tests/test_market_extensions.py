import pandas as pd
import pytest
from src.nyfed_data import parse_nyfed
from src.settlement_study import quarter_bounds,forward_rate_from_discount_factors,shocked_futures_pnl
from src.pricing import sr3_index

def test_nyfed_payload_normalization():
    p={'refRates':[{'effectiveDate':'2025-01-03','percentRate':4.3},{'effectiveDate':'2025-01-02','percentRate':'4.25'}]}
    x=parse_nyfed(p);assert x.date.tolist()==['2025-01-02','2025-01-03']

def test_nyfed_rejects_unexpected_schema():
    with pytest.raises(ValueError):parse_nyfed({'other':[]})

def test_quarter_third_wednesdays():
    assert quarter_bounds(2026,9)==('2026-09-16','2026-12-16')
    assert quarter_bounds(2026,12)==('2026-12-16','2027-03-17')

def test_act360_forward_relation():
    r=forward_rate_from_discount_factors(1.,1/1.01,90)
    assert abs(r-4.)<1e-10

def test_rate_shock_long_futures_loses():
    assert shocked_futures_pnl(2,25)==-1250
    assert shocked_futures_pnl(2,25,-1)==1250

def test_three_day_accrual_once_not_three_compounds():
    f=pd.DataFrame({'date':['2026-09-18','2026-09-21'],'sofr_pct':[3.6,3.6]})
    price=sr3_index(f,'2026-09-18','2026-09-21')
    assert price==pytest.approx(96.4,abs=1e-8)
