# -*- coding: utf-8 -*-
""" Analysis tools

Author:
    - Simon Wehle (swehle@desy.de)
    - Henrikas Svidras (henrikas.svidras@desy.de)

"""
import b2plot
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .histogram import _hist_init, to_stack, hist, get_xaxis
from .functions import xlim


def optimal_bin_size(n):
    """ Is this empricially the best?
    """
    return int(2*n**(1/3))


def plot_flatness(sig, tag, bins=None, ax=None, xrange=None, percent_step=5):
    """ Plotting differences of sig distribution in percentiles of tag distribution

    Args:
        sig:
        tag:
        bins:
        ax:
        xrange:
        percent_step:

    """

    if ax is None:
        fix, ax = plt.subplots()

    xaxis = _hist_init(sig, bins=bins, xrange=xrange)

    colormap = plt.get_cmap('magma')
    orig, x = np.histogram(sig, bins=xaxis, range=xrange, normed=True, )
    bin_center = ((x + np.roll(x, 1)) / 2)[1:]
    tmp = orig/orig
    ax.plot(bin_center, tmp, color='black', lw=1)
    for quantil in np.arange(5, 100, percent_step):
        cut = np.percentile(tag, quantil)
        sel = tag >= cut
        y, x = np.histogram(sig[sel], bins=x, range=xrange, normed=True, )
        y /= orig
        ax.fill_between(bin_center, tmp, y, color=colormap(quantil/100.0))
        tmp = y


def ratio(y1, y2, y1_err=None, y2_err= None):
    """ calculate the ratio between two histograms y1/y2

    Args:
        y1: y values of first histogram
        y2: y values of second histogram
        y1_err: (optional) error of first
        y2_err: (optional) error of second

    Returns:
        ratio, ratio_error

    """
    assert len(y1) == len(y2), "y1 and y2 length does not match"
    y1e = np.sqrt(y1) if y1_err is None else y1_err
    y2e = np.sqrt(y2) if y2_err is None else y2_err
    r = y1/y2
    re = np.sqrt((y1/(1.0*y2*y2))*(y1/(1.0*y2*y2))*y2e*y2e+(1/(1.0*y2))*(1/(1.0*y2))*y1e*y1e)
    return r, re


def divideEfficiency(n_nom, n_denom, confidence=0.683):
    """ divides two histograms for an efficiency calculation

    Args:
        n_nom: y values of nominator histogram (1d or 2d)
        n_denom: y values of denominator histogram  (1d or 2d)
        confidence: (optional) confidence level, by default 0.683

    Returns:
        ratio, [lower ratio error, upper ratio error]
    """
    shape = np.shape(n_nom)

    flattened_n_nom = n_nom.flatten()
    flattened_n_denom = n_denom.flatten()

    rat = []
    err_down = []
    err_up = []

    for passes, counts in zip(flattened_n_nom, flattened_n_denom):
        bin_ratio = exact_CI(passes, counts, conf=confidence)
        rat.append(bin_ratio[0])
        err_down.append(bin_ratio[1])
        err_up.append(bin_ratio[2])

    err_down = np.reshape(err_down, shape)
    err_up = np.reshape(err_up, shape)
    rat = np.reshape(rat, shape)

    return rat, (err_down, err_up)


def exact_CI(k, n, conf=0.683):
    """ calculated clopper pearson confidence intervals

    Args:
        k: number of passes ("numerator of proportion")
        n: total sample size ("denominator of proportion")
        conf: (optional) confidence level, by default 0.683

    Returns:
        ratio, [upper ratio error, lower ratio error]
    """

    from scipy.stats import beta
    k = float(k)
    n = float(n)
    p = (k/n) if n > 0 else 0

    alpha = (1 - conf)
    up = 1 if k == n else 1 - beta.ppf(alpha/2, n-k, k+1)
    down = 0 if k == 0 else 1 - beta.ppf(1-alpha/2, n-k+1, k)

    result = (p, p-down, up-p)
    return result


def divhist(h1, h2):
    assert np.mean(h1[1]-h2[1]) < 0.1
    r,re = ratio(h1[0],h2[0], np.mean(h1[2], axis=0),np.mean(h2[2], axis=0) )
    return r, h1[1], [re,re]


def subhist(h1, h2, rethist=False):
    assert np.mean(h1[1]-h2[1]) < 0.1
    r = h1[0] - h2[0]
    re = np.sqrt(np.mean(h1[2], axis=0)**2 + np.mean(h2[2], axis=0)**2)
    if rethist:
        return r,h1[1],  [re,re]
    return h1[1],r, [re,re]


def data_mc_ratio(data, mc, label_data='Data', label_mc="MC",
                  y_label=None, figsize=None, ratio_range=(0, 2),
                  *args, **kwarg):
    """ Perform data mc distributions
    
    returns:
        axes
    """
    f, axes = plt.subplots(2, 1, gridspec_kw={"height_ratios": [3, 1]}, sharex=True, figsize=figsize)
    ax0 = axes[0]

    hm = b2plot.hist(mc, lw=2, ax=ax0, label=label_mc, *args, **kwarg)
    hd = b2plot.errorhist(data, ax=ax0, label=label_data, color='black')
    ax0.legend()

    ax1 = axes[1]
    ry, rye = ratio(hd[0], hm[0])
    b2plot.errorbar(hd[1], ry, rye, ax=ax1, color='grey')
    ax1.axhline(1, color='grey', lw=0.5, ls='--')
    f.subplots_adjust(hspace=0.1)

    ax1.set_ylim(*ratio_range)
    b2plot.xlim()
    if y_label is not None:
        ax0.set_ylabel(y_label)
        ax1.set_ylabel("Ratio")
        ax1.yaxis.set_label_coords(-0.08, 0.5)
        ax0.yaxis.set_label_coords(-0.08, 0.5)
    return axes


def mask_append(xs,xb):
    """ Merge xs and xb into one vector and return it with a boolean mask for each category
    """
    return np.append(xs,xb), np.append(np.ones(len(xs)), np.zeros(len(xb)))==1


def pur_eff_cont(x, mask):
    """ Continuus evaluation of the purity vs efficiency 

    Returns:
        efficiency, purity : arrays of len(x)
    """
    if len(pd.unique(mask)) > 2:
        # if signal and background distribution are given as x and mask
        x, mask = mask_append(x, mask)

    ag = np.argsort(np.array(x))[::-1]
    e = mask[ag].cumsum() 
    eff = e/e[-1]
    pur = e/np.arange(1,len(mask)+1)
    return eff, pur 


def pur_eff(x, mask, nbins=None, reverse_too=False):
    """ Plots the distribution x in an equal frequency binning with the purity regarding mask

    Args:
        x: Distribution or signal distribution
        mask: Boolean mask or background distribution
        nbins:
        do_plot:
        figsize:
        xticks_fontsize:

    Returns:

    """
    if len(pd.unique(mask)) > 2:
        # if signal and background distribution are given as x and mask
        x, mask = mask_append(x, mask)

    nbins = optimal_bin_size(len(x)) if nbins is None else nbins

    x = x[np.isfinite(x)]
    bins = np.percentile(x, np.linspace(0, 100, nbins))

    y_, _ = np.histogram(x, bins)
    y_1, _ = np.histogram(x[mask], bins)
    y_0, _ = np.histogram(x[~mask], bins)

    pur = y_1 / (y_1 + y_0)
    ps = np.argsort(pur)
    # pur_err = (pur * (1 - pur)) / (y_)  

    # Sort by purity
    y1 = y_1[ps]
    y0 = y_0[ps]
    y = y_[ps]

    eff = sum(y1)-y1.cumsum()
    eff_err = np.sqrt(eff)/eff[0] #faster than np.sum(y_1)
    eff = eff/eff[0]

    pur= (y1[::-1].cumsum()/(y1[::-1].cumsum()+y0[::-1].cumsum()))[::-1]
    pur_err = (pur * (1 - pur)) / (y)  

    if reverse_too:
        eff_r = sum(y1)-y1[::-1].cumsum()
        eff_r_err = np.sqrt(eff_r)/eff_r[0]
        eff_r = eff_r/eff_r[0]    

        pur_r= (y1.cumsum()/(y1.cumsum()+y0.cumsum()))[::-1]
        pur_r_err = (pur_r * (1 - pur_r)) / (y)  

        eff = np.append(eff, eff_r[::-1])
        pur = np.append(pur, pur_r[::-1])
        eff_err = np.append(eff_err, eff_r_err[::-1])
        pur_err = np.append(pur_err, pur_r_err[::-1])
    return eff, pur,pur_err, eff_err


def fpr_tpr(x, mask, nbins=None):
    """ Plots the distribution x in an equal frequency binning with the purity regarding mask

    Args:
        x: Distribution or signal distribution
        mask: Boolean mask or background distribution
        nbins: Number of bins for the internal calculation (if None, optimal value is calculated)

    Returns:
        fpr, tpr: False positive rate, True positive rate
    """
    if len(pd.unique(mask)) > 2:
        # if signal and background distribution are given as x and mask
        x, mask = bp.analysis.mask_append(x, mask)

    nbins = optimal_bin_size(len(x)) if nbins is None else nbins

    x = x[np.isfinite(x)]
    bins = np.percentile(x, np.linspace(0, 100, nbins))

    y_, _ = np.histogram(x, bins)
    y_1, _ = np.histogram(x[mask], bins)
    y_0, _ = np.histogram(x[~mask], bins)

    pur = y_1 / (y_1 + y_0)
    ps = np.argsort(pur)

    # Sort by purity
    y1 = y_1[ps]
    y0 = y_0[ps]

    tp = np.cumsum(y1[::-1])[::-1]
    fp = np.cumsum(y0[::-1])[::-1]
    fn = y1.cumsum()
    tn = y0.cumsum()
    tpr = tp/(tp+fn)
    fpr = fp/(tn+fp)
    return fpr, tpr

    
def purity_hist(x, mask, nbins=10, do_plot=True, figsize=None, xticks_fontsize=None, ax=None):
    """ Plots the distribution x in an equal frequency binning with the purity regarding mask

    Args:
        x: Distribution or signal distribution
        mask: Boolean mask or background distribution
        nbins:
        do_plot:
        figsize:
        xticks_fontsize:
        ax:

    Returns:

    """
    if len(pd.unique(mask)) > 2:
        # if signal and background distribution are given as x and mask
        x, mask = mask_append(x, mask)

    x = x[np.isfinite(x)]
    bins = np.percentile(x, np.linspace(0, 100, nbins))
 
    y_, _ = np.histogram(x, bins)
    y_1, _ = np.histogram(x[mask], bins)
    y_0, _ = np.histogram(x[~mask], bins)

    pur = y_1 / (y_1 + y_0)
    pur_err = (pur * (1 - pur)) / (y_)    

    if do_plot:
        x_ = np.arange(len(y_) + 1)
        x_centers = (x_[1:] + x_[:-1]) / 2.

        if ax is None:
            _, ax = plt.subplots(figsize=figsize)
        ax.hist(x_[:-1], x_, weights=y_1, alpha=0.8, label='Signal')
        ax.hist(x_[:-1], x_, weights=y_0, histtype='step', lw=2, label='Background')
        ax.hist(x_[:-1], x_, weights=y_, histtype='step', color='grey', label='Total')

        ax2 = ax.twinx()
        ax2.errorbar(x_centers, pur, np.sqrt(pur_err), color='black', fmt="o--")
        ax2.set_xticklabels([], [])
        ax2.set_xticks([], [])

        ax2.set_ylabel("Purity")
        ax2.set_ylim(0)

        np.append(bins, x.max())
        _ = ax.set_xticks(x_)
        _ = ax.set_xticklabels(['%1.2e' % f for f in bins], rotation=-90, fontfamily='monospace',
                               fontsize=xticks_fontsize)
        plt.xlim(np.min(x_), np.max(x_))
        plt.sca(ax)
    return pur, np.sqrt(pur_err), bins


def flat_bins(x, set=False, nbins=None,  fontsize=None, rotation=-90):
    if nbins is None:
        nbins = len(get_xaxis())-1
    bins = np.percentile(x, np.linspace(0, 100, nbins+1))
    np.append(bins, x.max())
    if set:
        ax = plt.gca()
        x_ = np.linspace(0, 110, len(bins)+1)
        _ = ax.set_xticks(x_)
        _ = ax.set_xticklabels(['%1.2e' % f for f in bins], rotation=rotation, fontfamily='monospace',
                    fontsize=fontsize)
    else:
        return bins, np.linspace(0, 100, len(bins)+1)


def purity_flatness_proba(x, mask, nbins=10, do_plot=False):
    """ Returns the probability that the purity of x[mask] and x[~mask] is flat.

    This can be used as a measure of the information content in this observable regarding the mask.

    Args:
        x: Observable or signal distribution
        mask: Boolean mask, like 'is signal', 'is background' or background distribution
        nbins: Number of bins to calculate the purity
        do_plot (bool): plot the purity distribution

    Returns:
        chi2: probability of CDF(flat) against CDF(purity), where a value of 1 corresponds to the purity being compatible
        with a flat distribution.

    """

    if len(pd.unique(mask)) > 2:
        # if signal and background distribution are given as x and mask
        x, mask = mask_append(x, mask)
    
    if np.std(x)==0:
        return 1

    pur, pure, b = purity_hist(x, mask, nbins=nbins, do_plot=do_plot)

    mask = (np.isfinite(pur)) & (pur != 0)
    p = pur[mask]
    pe = pure[mask] * 100

    cs = np.nancumsum(p) * 100
    cl = np.cumsum(np.full(len(cs), np.mean(p), )) * 100
    chi2 = ((cl - cs) ** 2) / pe ** 2
    try:
        import scipy
        return scipy.stats.distributions.chi2.sf(np.sqrt(np.mean(chi2)), len(chi2))
    except ImportError:
        return chi2



def df_var_by2xy():
    pass


def sig_bkg_plot(df, col, by=None, ax=None, bins=None, range=None, labels=None, normed=False):
    """

    Args:
        df:
        col:
        by:
        ax:
        bins:
        range:
        labels:
        normed:

    Returns:

    """

    # foreseen usage
    if isinstance(df, pd.DataFrame):
        # by is not a boolean index
        if isinstance(by, str):
            x, cats = to_stack(df, col, by, get_cats=True)
            if len(x) > 2 :
                print("Waring, more than two categories in %s!" % by)
                assert len(x) > 1, "Did not found any categories in %s!" % by

            x_sig = x[0]
            x_bkg = x[1]

            if len(cats) == 2:
                if labels is None:
                    labels = [by+f' == {cats[1]}', by+f' == {cats[0]}']

        # by is a boolean index
        else:
           x_sig = df[col][by].values
           x_bkg = df[col][~by].values
    # Alternative usage, passing two arrays
    else:
        if len(pd.unique(col)) == 2:
            # if signal and background distribution are given as x and mask
            x_sig = df[col]
            x_bkg = df[~col]
        else:
            x_sig = df
            x_bkg = col

    xaxis = _hist_init(np.append(x_sig, x_bkg), bins, xrange=range)

    if labels is None:
        labels = ["Background", "Signal"]

    hist(x_bkg, xaxis, style=0, label=labels[0], ax=ax, density=normed)
    hist(x_sig, xaxis, lw=2, color=0, label=labels[1], ax=ax, density=normed)

    plt.legend()
    # xlim()


def get_upper_lim(x, perc=0.1, width=1, maxtries=100):
    xmax = np.max(x)
    xstd = width*np.std(x)
    if xstd == 0:
        return xmax
    lx = len(x)
    cut = xmax
    i = 0
    while i<maxtries:
        cut -= xstd
        px = 100*len(x[x>cut])/lx
        if px>=perc:
            cut+=xstd
            break
        i+=1
    return cut


def get_lower_lim(x, perc=0.1, width=1, maxtries=100):
    xmin = np.min(x)
    xstd = width*np.std(x)
    if xstd == 0:
        return xmin
    lx = len(x)
    cut = xmin
    i = 0
    while i<maxtries:
        cut += xstd
        px = 100*len(x[x<cut])/lx
        if px>=perc:
            cut-=xstd
            break
        
    return cut


def minmax(x,perc=0.1, width=1, maxtries=100):
    return (get_lower_lim(x, perc, width, maxtries), get_upper_lim(x, perc, width, maxtries))


def plot_feature_importance(fi, cols, figsize=None, palette='Blues_d',ax=None, *args, **kwargs):
    if ax is None:
        plt.figure(figsize=figsize)
        ax = plt.gca()
    import seaborn as sns
    imp = np.argsort(fi)[::-1]
    dfplot= pd.DataFrame({'col':np.array(cols)[imp], 'imp':fi[imp]})
    sns.barplot('imp', 'col', data=dfplot, hue_order=fi[imp][::-1], palette=palette, ax=ax, *args, **kwargs )
    ax.set_xlabel("Importance",)
    ax.set_ylabel("Feature",)
    return np.array(cols)[imp]
