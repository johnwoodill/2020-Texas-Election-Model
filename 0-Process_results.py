import subprocess
import os
import pandas as pd
import numpy as np
import datetime

def pred_mat(p, dat):
    # p is party and can be 'REP', 'DEM', 'OTH'
    # dat is the year of data to use
    
    mat = np.zeros((len(dat.index), len(dat.index)))
    
    for i in range(len(dat.index)):
        for j in range(len(dat.index)):
            mat[i, j] = dat[p][j] / dat[p][i]
    
    return(mat)

# Scrape TX Live Results
print("Process Live Scraper")
os.system("python live_scraper.py")
print("Complete")

# Load election data 
dat_2012 = pd.read_csv('./data/TX_cnty_2012.csv').sort_values('County')
dat_2016 = pd.read_csv('./data/TX_cnty_2016.csv').sort_values('County')
dat_2018 = pd.read_csv('./data/TX_cnty_2018.csv').sort_values('County')

# Get lookup table for ij and county
lookup_county = dat_2012[['County']].reset_index()

# Get live results
ldat = pd.read_csv('data/scraped_live_results.csv')

# Real data
# ldat = pd.read_csv('data/processed_live_results_complete_precincts.csv')




# !!!!!!!!!!!!!!!!!!!!!!!!!
# Test data
ldat = ldat[(ldat['county'] == "ANDERSON") | (ldat['county'] == "ZAVALA")]
ldat = ldat.assign(V = [12262, 3813, 574, 3042])

# !!!!!!!!!!!!!!!!!!!!!!!!!



# Generate two prediction matrices, one for dems and one for repubs for each year of results.
r_mat_2012 = pred_mat('REP', dat_2012)
d_mat_2012 = pred_mat('DEM', dat_2012)

r_mat_2016 = pred_mat('REP', dat_2016)
d_mat_2016 = pred_mat('DEM', dat_2016)

r_mat_2018 = pred_mat('REP', dat_2018)
d_mat_2018 = pred_mat('DEM', dat_2018)


# Generate distributions for each county based on matrices
unique_counties = ldat.county.unique()
retdat = pd.DataFrame()
for i in unique_counties:
    idx = lookup_county[lookup_county['County'] == i].index.values
    rep_V = ldat[(ldat['county'] == i) & (ldat['N'] == 'TRUMP')].V.values
    dem_V = ldat[(ldat['county'] == i) & (ldat['N'] == 'BIDEN')].V.values
    
    ### TRUMP predictions
    r_pred_2012 = rep_V * r_mat_2012[idx, ].ravel()
    r_pred_2012_dat = pd.DataFrame({'corr_county': i, 'pred_year': 2012, 'county': lookup_county['County'], 'N': 'TRUMP', 'pred_v': r_pred_2012})
    
    r_pred_2016 = rep_V * r_mat_2016[idx, ].ravel()
    r_pred_2016_dat = pd.DataFrame({'corr_county': i, 'pred_year': 2016, 'county': lookup_county['County'], 'N': 'TRUMP', 'pred_v': r_pred_2016})
    
    r_pred_2018 = rep_V * r_mat_2018[idx, ].ravel()
    r_pred_2018_dat = pd.DataFrame({'corr_county': i, 'pred_year': 2018, 'county': lookup_county['County'], 'N': 'TRUMP', 'pred_v': r_pred_2018})
    
    ### BIDEN predictions
    d_pred_2012 = dem_V * d_mat_2012[idx, ].ravel()
    d_pred_2012_dat = pd.DataFrame({'corr_county': i, 'pred_year': 2012, 'county': lookup_county['County'], 'N': 'BIDEN', 'pred_v': d_pred_2012})
    
    d_pred_2016 = dem_V * d_mat_2016[idx, ].ravel()
    d_pred_2016_dat = pd.DataFrame({'corr_county': i, 'pred_year': 2016, 'county': lookup_county['County'], 'N': 'BIDEN', 'pred_v': d_pred_2016})
    
    d_pred_2018 = dem_V * d_mat_2018[idx, ].ravel()
    d_pred_2018_dat = pd.DataFrame({'corr_county': i, 'pred_year': 2018, 'county': lookup_county['County'], 'N': 'BIDEN', 'pred_v': d_pred_2018})
    
   
    ### Get timestamp
    ct = datetime.datetime.now() 
    
    ### Bind predictions
    indat = pd.concat([r_pred_2012_dat, r_pred_2016_dat, r_pred_2018_dat,
                      d_pred_2012_dat, d_pred_2016_dat, d_pred_2018_dat])
    
    ### Bind data
    indat = indat.assign(timestamp= ct)
    indat = indat[['timestamp', 'corr_county', 'pred_year', 'county', 'N', 'pred_v']]
    retdat = pd.concat([retdat, indat])
    
    
    

# Save primary data
retdat.to_csv("data/processed_election_results.csv", index=False)    

# Save data by timestamp
retdat.to_csv(f"data/processed_timestamp/processed_election_results_{ct}.csv")   

    

    
    
    


