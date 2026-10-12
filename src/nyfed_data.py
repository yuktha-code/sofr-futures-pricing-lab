"""Optional official NY Fed historical SOFR downloader. Network access required.

The demo remains offline and synthetic; public endpoint response varies over time.
This client normalizes FRBNY refRates; a live response is NOT included here.
"""
from __future__ import annotations
import json
import urllib.request
from urllib.parse import urlencode
from pathlib import Path
import pandas as pd

API = 'https://markets.newyorkfed.org/api/rates/secured/sofr/search.json'
SOURCE = 'https://markets.newyorkfed.org/static/docs/markets-api.html'

def parse_nyfed(payload: dict) -> pd.DataFrame:
    rows = payload.get('refRates')
    if not isinstance(rows,list) or not rows:
        raise ValueError('Expected nonempty refRates from NY Fed API')
    result = []
    for entry in rows:
        # New York Fed field names: effectiveDate, percentRate.
        if 'effectiveDate' not in entry or 'percentRate' not in entry:
            raise ValueError('Unexpected NY Fed reference-rate response')
        result.append({'date':entry['effectiveDate'],'sofr_pct':float(entry['percentRate'])})
    df=pd.DataFrame(result)
    df['date']=pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    df=df.sort_values('date').reset_index(drop=True)
    if df.date.duplicated().any() or not df.sofr_pct.between(-10,100).all():
        raise ValueError('Duplicate dates or implausible SOFR rates')
    return df

def fetch_sofr(start: str,end: str,timeout: int=25)->pd.DataFrame:
    params=urlencode({'startDate':start,'endDate':end})
    request=urllib.request.Request(API+'?'+params,headers={'User-Agent':'EducationalSOFRResearch/1.0','Accept':'application/json'})
    with urllib.request.urlopen(request,timeout=timeout) as response:
        payload=json.load(response)
    return parse_nyfed(payload)

def write_snapshot(start:str,end:str,path:str):
    df=fetch_sofr(start,end)
    target=Path(path);target.parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(target,index=False)
    target.with_suffix('.metadata.json').write_text(json.dumps({'source':SOURCE,'endpoint':API,'start':start,'end':end,'rows':len(df),'data_kind':'OFFICIAL HISTORICAL FIXINGS: NOT CME FUTURES QUOTES'},indent=2))
    return target

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--start',required=True);p.add_argument('--end',required=True);p.add_argument('--output',default='data/nyfed_sofr_historical.csv')
    a=p.parse_args();print(write_snapshot(a.start,a.end,a.output))
