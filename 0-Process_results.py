import subprocess
import os
import pandas as pd
import numpy as np
from numpy import inf
import datetime
import subprocess as cmd
import time

# Prediction matrix calc
def pred_mat(p, dat):
    # p is party and can be 'REP', 'DEM', 'OTH'
    # dat is the year of data to use
    
    mat = np.zeros((len(dat.index), len(dat.index)))
    
    for i in range(len(dat.index)):
        for j in range(len(dat.index)):
            mat[i, j] = dat[p][j] / dat[p][i]
    
    return(mat)





if __name__ == "__main__":
    
    for i in range(100000):

        # Scrape TX Live Results
        os.system("python live_scraper.py")

        # Load election data 
        dat_2012 = pd.read_csv('./data/TX_cnty_2012.csv').sort_values('County')
        dat_2014 = pd.read_csv('./data/TX_cnty_2014.csv').sort_values('County')
        dat_2016 = pd.read_csv('./data/TX_cnty_2016.csv').sort_values('County')
        dat_2018 = pd.read_csv('./data/TX_cnty_2018.csv').sort_values('County')

        # Get lookup table for ij and county
        lookup_county = dat_2012[['County']].reset_index()

        # Get live results
        ldat = pd.read_csv('data/scraped_live_results.csv')




        # Real data
        # ldat = pd.read_csv('data/processed_live_results_complete_precincts.csv')



        # Test data
        # !!!!!!!!!!!!!!!!!!!!!!!!!

        t_dat_2012 = dat_2018[['County', 'REP', 'DEM', 'OTH']]
        t_dat_2012.columns = ['county', 'TRUMP', 'BIDEN', 'OTH']

        t_dat_2012 = t_dat_2012.melt(id_vars='county')
        t_dat_2012.columns = ['county', 'N', 'V']
        t_dat_2012 = t_dat_2012.sort_values(['county']).reset_index(drop=True)

        ldat = ldat.drop(columns='V').merge(t_dat_2012, how='outer', on=['county', 'N'])

        # !!!!!!!!!!!!!!!!!!!!!!!!!



        # Generate two prediction matrices, one for dems and one for repubs for each year of results.
        r_mat_2012 = pred_mat('REP', dat_2012)
        d_mat_2012 = pred_mat('DEM', dat_2012)
        o_mat_2012 = pred_mat('OTH', dat_2012)

        r_mat_2014 = pred_mat('REP', dat_2014)
        d_mat_2014 = pred_mat('DEM', dat_2014)
        o_mat_2014 = pred_mat('OTH', dat_2014)

        r_mat_2016 = pred_mat('REP', dat_2016)
        d_mat_2016 = pred_mat('DEM', dat_2016)
        o_mat_2016 = pred_mat('OTH', dat_2016)

        r_mat_2018 = pred_mat('REP', dat_2018)
        d_mat_2018 = pred_mat('DEM', dat_2018)
        o_mat_2018 = pred_mat('OTH', dat_2018)

        # Generate distributions for each county based on matrices
        unique_counties = ldat.county.unique()
        retdat = pd.DataFrame()
        for i in unique_counties:
            idx = lookup_county[lookup_county['County'] == i].index.values
            rep_V = ldat[(ldat['county'] == i) & (ldat['N'] == 'TRUMP')].V.values
            dem_V = ldat[(ldat['county'] == i) & (ldat['N'] == 'BIDEN')].V.values
            oth_V = ldat[(ldat['county'] == i) & (ldat['N'] == 'OTH')].V.values

            ### TRUMP predictions
            r_pred_2012 = rep_V * r_mat_2012[idx, ].ravel()
            r_pred_2012_dat = pd.DataFrame({'corr_county': i, 'pred_year': 2012, 'county': lookup_county['County'], 'N': 'TRUMP', 'pred_v': r_pred_2012})

            r_pred_2014 = rep_V * r_mat_2014[idx, ].ravel()
            r_pred_2014_dat = pd.DataFrame({'corr_county': i, 'pred_year': 2014, 'county': lookup_county['County'], 'N': 'TRUMP', 'pred_v': r_pred_2014})

            r_pred_2016 = rep_V * r_mat_2016[idx, ].ravel()
            r_pred_2016_dat = pd.DataFrame({'corr_county': i, 'pred_year': 2016, 'county': lookup_county['County'], 'N': 'TRUMP', 'pred_v': r_pred_2016})

            r_pred_2018 = rep_V * r_mat_2018[idx, ].ravel()
            r_pred_2018_dat = pd.DataFrame({'corr_county': i, 'pred_year': 2018, 'county': lookup_county['County'], 'N': 'TRUMP', 'pred_v': r_pred_2018})

            ### BIDEN predictions
            d_pred_2012 = dem_V * d_mat_2012[idx, ].ravel()
            d_pred_2012_dat = pd.DataFrame({'corr_county': i, 'pred_year': 2012, 'county': lookup_county['County'], 'N': 'BIDEN', 'pred_v': d_pred_2012})

            d_pred_2014 = dem_V * d_mat_2014[idx, ].ravel()
            d_pred_2014_dat = pd.DataFrame({'corr_county': i, 'pred_year': 2014, 'county': lookup_county['County'], 'N': 'BIDEN', 'pred_v': d_pred_2014})

            d_pred_2016 = dem_V * d_mat_2016[idx, ].ravel()
            d_pred_2016_dat = pd.DataFrame({'corr_county': i, 'pred_year': 2016, 'county': lookup_county['County'], 'N': 'BIDEN', 'pred_v': d_pred_2016})

            d_pred_2018 = dem_V * d_mat_2018[idx, ].ravel()
            d_pred_2018_dat = pd.DataFrame({'corr_county': i, 'pred_year': 2018, 'county': lookup_county['County'], 'N': 'BIDEN', 'pred_v': d_pred_2018})

            ### OTH predictions
            o_mat_2012[o_mat_2012 == inf] = 0
            o_mat_2012 = np.where(np.isnan(o_mat_2012), 0, o_mat_2012)
            o_pred_2012 = oth_V * o_mat_2012[idx, ].ravel()
            o_pred_2012_dat = pd.DataFrame({'corr_county': i, 'pred_year': 2012, 'county': lookup_county['County'], 'N': 'OTHER', 'pred_v': o_pred_2012})

            o_mat_2014[o_mat_2014 == inf] = 0
            o_mat_2014 = np.where(np.isnan(o_mat_2014), 0, o_mat_2014)
            o_pred_2014 = oth_V * o_mat_2014[idx, ].ravel()
            o_pred_2014_dat = pd.DataFrame({'corr_county': i, 'pred_year': 2014, 'county': lookup_county['County'], 'N': 'OTHER', 'pred_v': o_pred_2014})

            o_mat_2016[o_mat_2016 == inf] = 0
            o_mat_2016 = np.where(np.isnan(o_mat_2016), 0, o_mat_2016)
            o_pred_2016 = oth_V * o_mat_2016[idx, ].ravel()
            o_pred_2016_dat = pd.DataFrame({'corr_county': i, 'pred_year': 2016, 'county': lookup_county['County'], 'N': 'OTHER', 'pred_v': o_pred_2016})

            o_mat_2018[o_mat_2018 == inf] = 0
            o_mat_2018 = np.where(np.isnan(o_mat_2018), 0, o_mat_2018)
            o_pred_2018 = oth_V * o_mat_2018[idx, ].ravel()
            o_pred_2018_dat = pd.DataFrame({'corr_county': i, 'pred_year': 2018, 'county': lookup_county['County'], 'N': 'OTHER', 'pred_v': o_pred_2018})

            ### Bind predictions
            indat = pd.concat([r_pred_2012_dat, r_pred_2014_dat, r_pred_2016_dat, r_pred_2018_dat,
                            d_pred_2012_dat, d_pred_2014_dat, d_pred_2016_dat, d_pred_2018_dat,
                            o_pred_2012_dat, o_pred_2014_dat, o_pred_2016_dat, o_pred_2018_dat])

            ### Bind data
            indat = indat[['corr_county', 'pred_year', 'county', 'N', 'pred_v']]
            retdat = pd.concat([retdat, indat])


        ### Get timestamp
        ct = datetime.datetime.now() 
        retdat = retdat.assign(timestamp= ct)        

        ### Save primary data
        retdat.to_csv("data/processed_election_results.csv", index=False)    

        ### Save data by timestamp
        retdat.to_csv(f"data/processed_timestamp/processed_election_results_{ct}.csv")   

        ### Process figures
        cmd.run("Rscript Figures.R", check=True, shell=True)

        ### Git commit/push
        cmd.run('git add figures/*', check=True, shell=True)
        cmd.run('git commit -a -m "update"', check=True, shell=True)
        cmd.run("git push origin main", check=True, shell=True)

        print(f"Finished Processing model: {ct} ..... Pausing for 5 minutes")
        time.sleep(60 * 5) # Delay for 5 minutes
        

        
        
        


