import json
from pandas.io.json import json_normalize
import pandas as pd
import requests
import numpy as np

url = "https://results.texas-election.com/static/data/election/44144/108/County.json"

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
}
response = requests.get(url, headers=headers).json()

# ### Dump json results to server
with open("data/county_results.json", "w") as output:
    json.dump(response, output, indent=4, sort_keys=True)

 
# 9240 "Trump/Pence"
# 9160 = "Biden/Harris"

outdat = pd.DataFrame()
for v in response.values():    
    for id_, race_data in v["Races"].items():
        county = v["N"]
        total_precincts = v["Summary"]['PRP']
        reported_precincts = v["Summary"]['PRR']
        regist_voters = v["Summary"]["RV"]
        if id_ == "1001":
            indat = pd.DataFrame(race_data["C"]).T
            indat = indat.assign(county = county,
                                 total_precincts = total_precincts,
                                 reported_precincts = reported_precincts,
                                 regist_voters = regist_voters)
            indat = indat[(indat['id'] == 9240) | (indat['id'] == 9160)]
            indat = indat[(indat['P'] == "REP") | (indat['P'] == "DEM")]
            indat = indat.dropna()
            outdat = pd.concat([outdat, indat])
            
            
outdat = outdat.assign(N = np.where(outdat['P'] == 'DEM', "BIDEN", "TRUMP"))
outdat = outdat[['county', 'id', 'N', 'P', 'V', 'PE', 'total_precincts', 'reported_precincts']].reset_index(drop=True)

outdat.to_csv('data/processed_live_results.csv', index=False)



