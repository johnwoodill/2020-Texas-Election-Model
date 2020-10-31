# Generate two prediction matrices, one for dems and one for repubs for each year of results.

import pandas as pd
import numpy as np

def pred_mat(p, dat):
    # p is party and can be 'REP', 'DEM', 'OTH'
    # dat is the year of data to use
    
    mat = np.zeros((len(dat.index), len(dat.index)))
    
    for i in range(len(dat.index)):
        for j in range(len(dat.index)):
            mat[i, j] = dat[p][j] / dat[p][i]
    
    return(mat)

# Test for 2012
dat = pd.read_csv('./data/TX_cnty_2012.csv')  

m = pred_mat('REP', dat)

# Test prediction
pred_test = 12262 * m[0,]

pred_test = 3639 * m[1,]

print(pred_test.sum())

print(dat['REP'].sum())