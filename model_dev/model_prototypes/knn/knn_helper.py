## Helper functions for knn model

import antropy as ant
from scipy.stats import entropy
from scipy.special import kolmogorov
import neurokit2 as nk
from scipy.stats import kstest
import nolds
from pybdm import BDM
import math
import numpy as np

## Approximate entropy
def approximate_entropy(x):
    return ant.app_entropy(x)

## Signal energy
def signal_energy(x):
    return np.sum(x)

## Fuzzy entropy
def fuzzy_entropy(x):
    return nk.entropy_fuzzy(x)

## Kolmogorov Exponent
def kolmogorov_exponent(x):
    return np.mean(kolmogorov(x))

## Perumtation entropy
def permutation_entropy(x):
    return ant.perm_entropy(x, normalize=True)

## TODO: Shannon entropy
def shannon_entropy(x):
    #tmp_series_approx = write_signal_dict_approx[key]
    # tmp_series_coeff = write_signal_dict_coeff[key]
    # pd_series_approx = pd.Series(tmp_series_approx)
    # counts_approx = pd_series_approx.value_counts()
    # shannon_entropy.append(entropy(counts_approx))
    # pd_series_coeff = pd.Series(tmp_series_coeff)
    # counts_coeff = pd_series_coeff.value_counts()
    # shannon_entropy.append(entropy(counts_coeff))
    return x

## Renyi entropy
def renyi_entropy(x, alpha=2):
    return (1.0 / (1.0 - alpha)) * np.log2(np.sum(x ** alpha))

## Tsallis entropy
def tsallis_entropy(x, q=2):
    return (1-sum(x))/(q-1)

## Wavelet entropy
def wavelet_entropy(x):
    return (-sum((x)*np.log(x)))

## Fractal dimension
def fractal_dimension(x):
    return ant.petrosian_fd(x)

## TODO: Kolmogorov complexity
def kolmogorov_complexity(x):
    # bdm = BDM(ndim=1)
    # int_dict_approx = write_signal_dict_approx[key]
    # int_dict_coeff = write_signal_dict_coeff[key]
    # for i in range(len(int_dict_approx)):
    #     int_dict_approx[i] = math.floor((max(int_dict_approx) - int_dict_approx[i])/(max(int_dict_approx)-min(int_dict_approx)))
    #     int_dict_coeff[i] = math.floor((max(int_dict_coeff) - int_dict_coeff[i])/(max(int_dict_coeff)-min(int_dict_coeff)))
    
    # int_dict_approx = int_dict_approx.astype(int)
    # int_dict_coeff = int_dict_coeff.astype(int)
    # kolmogorov_complexity.append(bdm.bdm(int_dict_approx))
    # kolmogorov_complexity.append(bdm.bdm(int_dict_coeff))
    return x

## Largest Lyapuniv Exponent
def largest_lyapuniv_exponent(x):
    return nolds.lyap_r(x)

def extract_features(data_dict):
    for patient in data_dict.keys():
        for recording in data_dict[patient].keys():
            feats_dict = {}
            feats_dict["approximate_entropy"] = approximate_entropy(data_dict[patient][recording])