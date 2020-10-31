# Generate two prediction matrices, one for dems and one for repubs for each year of results.

import pandas as pd
import numpy as np

def pred_mat(p, dat):
    # p is party and can be 'REP', 'DEM', 'OTH'
    # dat is the year of data to use
    
    dat[p] = pd.to_numeric(dat[p])
    
    mat = np.zeros((len(dat.index), len(dat.index)))
    
    for (i in len(dat.index)):
        for (j in len(dat.index)):
            mat[i, j] = dat[p][i] / dat[p][j]
    
    return(mat)

# Read data
cnty_dat = pd.read_csv('./data/TX_cnty_2012.csv')  

