"""Run from repository root: python -m src.demo"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .pricing import sr1_index, sr3_index, strip_curve, third_wednesday, hypothetical_fair_value_strip
ROOT=Path(__file__).resolve().parents[1]

def main():
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'figures').mkdir(exist_ok=True)
    overnight=pd.read_csv(ROOT/'data'/'synthetic_sofr_fixings.csv')
    strips=pd.read_csv(ROOT/'data'/'synthetic_contract_strip.csv')
    a=sr1_index(overnight,'2026-07-01','2026-08-01')
    b=sr3_index(overnight,'2026-06-17','2026-09-16')
    curve=strip_curve(strips,convexity_bp=1.5)
    curve.to_csv(ROOT/'results'/'projection_curve.csv',index=False)
    model=hypothetical_fair_value_strip(overnight,strips)
    up25=hypothetical_fair_value_strip(overnight,strips,scenario_rate_shock_bp=25)
    model['model_fair_index_if_up25bp']=up25.model_fair_index
    model.to_csv(ROOT/'results'/'independent_hypothetical_fair_value_vs_quotes.csv',index=False)
    metrics=pd.DataFrame({'metric':['SR1 Jul simulated index','SR3 Jun-Sep simulated index','SR3 long PnL +25bp (USD)','IMM Jun 2026'],
       'value':[f'{a:.6f}',f'{b:.6f}',f"{curve.iloc[0]['plus_25bp_pnl_one_long_usd']:.2f}",str(third_wednesday(2026,6).date())]})
    metrics.to_csv(ROOT/'results'/'summary.csv',index=False)
    fig,ax=plt.subplots(figsize=(8,4)); ax.plot(curve.contract,curve.implied_futures_pct,marker='o',label='Futures-implied rate')
    ax.plot(curve.contract,curve.approx_forward_pct,marker='s',label='Forward proxy, -1.5bp assumption')
    ax.plot(model.contract,100-model.model_fair_index,marker='^',label='Independent hypothetical SOFR path')
    ax.set_ylabel('Annualized rate (%)');ax.set_title('Synthetic SR3 Strip | Illustrative Curve');ax.legend();fig.tight_layout()
    fig.savefig(ROOT/'figures'/'synthetic_curve.png',dpi=170);plt.close(fig)
    print(metrics.to_string(index=False));print('Wrote results/projection_curve.csv and figures/synthetic_curve.png')
if __name__=='__main__':main()
