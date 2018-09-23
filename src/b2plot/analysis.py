# -*- coding: utf-8 -*-
""" Analysis tools

"""

import numpy as np
import matplotlib.pyplot as plt
from .functions import _hist_init


def plot_flatness(sig, tag, bins=None, ax=None, xrange=None, percent_step=5):
    """ Plotting differences of sig distribution in percentiles of tag distribution

    :param sig:
    :param tag:
    :param ax:
    :param percent_step:
    :return:
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



def profile(x, y, bins=None, range=None, fmt='.', *args, **kwargs):
    import scipy

    xaxis = _hist_init(x, bins, xrange=range)

    means = scipy.stats.binned_statistic(x, y, bins=xaxis, statistic='mean').statistic
    std = scipy.stats.binned_statistic(x, y, bins=xaxis, statistic=scipy.stats.sem).statistic

    bin_centers = (xaxis[:-1] + xaxis[1:]) / 2.
    plt.errorbar(x=bin_centers, y=means, yerr=std, linestyle='none', fmt=fmt, *args, **kwargs)


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