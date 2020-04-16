 # -*- coding: utf-8 -*-
"""
In this file all the matplolib wrappers are located.

"""

from .helpers import get_optimal_bin_size, TheManager
from .colors import b2cm
import pandas as pd
import numpy as np
from matplotlib.colors import hex2color

import matplotlib.pyplot as plt


def _hist_init(data, bins=None, xrange=None):
    """ Performs and stores or returns the binning

    Args:
        data:
        bins:
        xrange:

    Returns:

    """
    xaxis = TheManager.Instance().get_x_axis()

    if xaxis is None or bins is not None or xrange is not None:
        if bins is None:
            bins = get_optimal_bin_size(len(data))
        _, xaxis = np.histogram(data, bins, xrange)

    return xaxis


def set_xaxis(bins, flat=False):
    TheManager.Instance().set_x_axis(bins)


def get_xaxis():
    return TheManager.Instance().get_x_axis()


def flat_x(x, nbins=25):
    set_xaxis(np.percentile(x, np.linspace(0, 100, nbins)))


def text(t, x=0.8, y=0.9, fontsize=22, *args, **kwargs):
    """

    :param t:
    :param x:
    :param y:
    :param fontsize:
    :param args:
    :param kwargs:
    :return:
    """
    plt.text(x, y, t, transform=plt.gca().transAxes, fontsize=fontsize, *args, **kwargs)


STYLES_facecolor = [None, 'none', 'none', 'none', 'none', 'none']
STYLES_hatches = [None, '///', r"\\\ ",  'xxx', '--', '++', 'o', ".+", 'xx', '//', '*',  'O', '.']


def hist(data, bins=None, fill=False, range=None, lw=1., ax=None, style=None, color=None, scale=None, weights=None,
         label=None, edgecolor=None, fillalpha=0.5, *args, **kwargs):
    """

    Args:
        data:
        bins:
        fill:
        range:
        lw:
        ax:
        style:
        color:
        scale:
        weights:
        *args:
        **kwargs:

    Returns:

    """


    if ax is None:
        ax = plt.gca()

    xaxis = _hist_init(data, bins, xrange=range)

    if type(data) is pd.Series:
        data = data.values

    if isinstance(color, int):
        color = b2cm[color % len(b2cm)]

    if color is None:
        color = next(ax._get_lines.prop_cycler)["color"]

    # convert color
    if not isinstance(color, list) or isinstance(color, tuple):
        color = hex2color(color)

    if style is not None:
        fill = True
        if style==0 and edgecolor is None:
            edgecolor = 'black'
    else:
        style = 0

    if weights is None:
        weights = np.ones(len(data))

    if scale is not None:
        if isinstance(scale, int) or isinstance(scale, float):
            if not isinstance(scale, bool):
                weights *= scale
        else:
            print("Please provide int or float with scale")

    edgecolor = color if edgecolor is None else edgecolor

    if fill:
        # edgecolor = 'black' if style == 0 else color
        fc = (*color, fillalpha) if style == 0 else 'none'
        # y, xaxis, _ = ax.hist(data, xaxis, range=range, histtype='step',
        #                       lw=lw, color=color, weights=weights, *args, **kwargs)
        y, xaxis, patches = ax.hist(data, xaxis, range=range, lw=lw, histtype='stepfilled', hatch=STYLES_hatches[style],
                                    edgecolor=edgecolor, facecolor=fc, linewidth=lw, weights=weights, label=label,
                                    color=color, *args, **kwargs)
    else:
        y, xaxis, patches = ax.hist(data, xaxis, range=range, histtype='step', lw=lw, color=color, weights=weights,
                                    label=label, *args, **kwargs)

    TheManager.Instance().set_x_axis(xaxis)
    return y, xaxis, patches


def bar(y, binedges, ax=None, *args, **kwargs):

    if ax is None:
        ax = plt.gca()

    x = (binedges[1:] + binedges[:-1]) / 2.0

    return ax.hist(x, bins=binedges, weights=y,
               *args, **kwargs)

def _notransform(x):
    return x

def to_stack(df, col, by, transform=None):

    g = df.groupby(by)
    transform = _notransform if transform is None else transform
    x_data = []
    for gr in g.groups:
        x_data.append(transform(g.get_group(gr)[col].values))
    
    cats = np.array([gg for gg in g.groups])
    x_len = np.array([len(x) for x in x_data])
    inds = x_len.argsort()
    # print(cats)
    # print(inds)
    return [x_data[i] for i in inds], cats[inds]


def stacked(df, col=None, by=None, bins=None, color=None, range=None, lw=.5, ax=None, edgecolor='black', weights=None,
            scale=None, label=None, transform=None, *args, **kwargs):
    """ Create stacked histogram

    Args:
        df (DataFrame or list of arrays):
        col:
        by:
        bins:
        color:
        lw:
        *args:
        **kwargs:

    Returns:

    """

    if isinstance(df, pd.DataFrame):
        assert col is not None, "Please provide column"
        assert by is not None, "Please provide by"

        data, cats = to_stack(df, col, by, transform)
        if label is None:
            label = cats

    else:
        assert isinstance(df, list), "Please provide DataFrame or List"
        data = df

    if ax is None:
        ax = plt.gca()

    if color is None:
        from b2plot.colors import b2helix
        n_stacks = len(data)
        if n_stacks < 20:
            color = b2helix(n_stacks)

    if weights is None:
        weights = []
        for d in data:
            wei = np.ones(len(d))
            if scale is not None:
                if isinstance(scale, int) or isinstance(scale, float):
                    if not isinstance(scale, bool):
                        wei *= scale
                else:
                    print("Please provide int or float with scale")
            weights.append(wei)


    xaxis = _hist_init(data[0], bins, xrange=range)

    y, xaxis, stuff = ax.hist(data, xaxis, histtype='stepfilled',
                          lw=lw, color=color, edgecolor=edgecolor, stacked=True, weights=weights, label=label, *args, **kwargs)

    TheManager.Instance().set_x_axis(xaxis)

    return y[-1], xaxis, stuff  # dangerous list index


def errorhist(data, bins=None, color=None, normed=False, fmt='.', range=None, scale=None,
              x_err=False, box=False, ax=None, weights=None, plot_zero=True, label=None, *args, **kwargs):
    """

    :param data:
    :param xaxis:
    :param color:
    :param normed:
    :param range:
    :param args:
    :param kwargs:
    :return:
    """

    xaxis = _hist_init(data, bins, xrange=range)

    if ax is None:
        ax = plt.gca()

    if type(data) is pd.Series:
        data = data.values

    if weights is None:
        weights = np.ones(len(data))

    if scale is not None:
        if isinstance(scale, int) or isinstance(scale, float):
            if not isinstance(scale, bool):
                weights *= scale
        else:
            print("Please provide int or float with scale")

    y, x = np.histogram(data, xaxis, normed=normed, weights=weights)
    err = (-0.5 + np.sqrt(np.array(y + 0.25)), +0.5 + np.sqrt(np.array(y + 0.25)))  # np.sqrt(np.array(y))
    bin_centers = (x[1:] + x[:-1]) / 2.0

    if isinstance(color, int):
        color = b2cm[color % len(b2cm)]

    if color is None:
        color = next(ax._get_lines.prop_cycler)["color"]

    # https://www-cdf.fnal.gov/physics/statistics
    if normed:
        yom, x = np.histogram(data, xaxis, weights=weights)
        err = (np.sqrt(np.array(yom)) *(y/yom), np.sqrt(np.array(yom)) * (y/yom))
    if x_err is not False or box:
        x_err = (x[1]-x[0])/2.0
    else:
        x_err = None

    errorbar(bin_centers, y, err, x_err, box, plot_zero, fmt, color, ax, label=label, *args, **kwargs)


    TheManager.Instance().set_x_axis(xaxis)

    return y, bin_centers, err


def errorbar(bin_centers, y, y_err, x_err=None, box=False, plot_zero=True, fmt='.',
             color=None, ax=None, label=None, *args, **kwargs):

    if ax is None:
        ax = plt.gca()

    if len(y_err) != 2:
        y_err = y_err, y_err

    if color is None:
        color = next(ax._get_lines.prop_cycler)["color"]

    toplot = np.ones(len(y)).astype(bool)

    if plot_zero is False:
        toplot[y == 0] = False
        y_err = (y_err[0][[toplot]], y_err[1][toplot])
        if x_err is not None:
            x_err = x_err[toplot]
        bin_centers = bin_centers[toplot]
        y = y[toplot]

    if box:
        assert x_err is not None, "Please provide x-err"
        hi = y_err[0] + y_err[1]
        lo = y - y_err[0]
        ax.errorbar(bin_centers, y, color=color, xerr=x_err, fmt=' ')
        ax.bar(bin_centers[toplot], hi, bottom=lo, align='center', color=color, alpha=.7,
                width=2 * x_err, label=label,
                edgecolor=color, *args, **kwargs)
    else:
        ax.errorbar(bin_centers, y, yerr=y_err, xerr=x_err, fmt=fmt, color=color,label=label, *args, **kwargs)


def xlim(low=None, high=None, ax=None):
    """

    Args:
        low:
        high:
        ax:

    Returns:

    """
    xaxis = TheManager.Instance().get_x_axis()
    if xaxis is not None:
        if ax is None:
            ax = plt.gca()
        ax.set_xlim(np.min(xaxis), np.max(xaxis))
    if low is not None or high is not None:
        ax.set_xlim(low, high)


def save(filename,  *args, **kwargs):
    """ Save a file and do the subplot_adjust to fit the page with larger labels

    Args:
        filename:
        *args:
        **kwargs:

    Returns:

    """
    plt.savefig(filename, bbox_inches='tight', *args, **kwargs)


def save_adjust(filename, bottom=0.15, left=0.13, right=0.96, top=0.95, *args, **kwargs):
    """ Save a file and do the subplot_adjust to fit the page with larger labels

    Args:
        filename:
        bottom:
        left:
        right:
        top:
        *args:
        **kwargs:
bbox_inches='tight',
    Returns:

    """
    plt.subplots_adjust(bottom=bottom, left=left, right=right, top=top)
    plt.savefig(filename,  *args, **kwargs)


def profile(x, y, bins=None, range=None, fmt='.', *args, **kwargs):
    """ Profile plot of x vs y; the mean and std of y in bins of x as errorbar

    Args:
        x:
        y:
        bins:
        range:
        fmt:
        *args:
        **kwargs:

    Returns:

    """
    import scipy

    xaxis = _hist_init(x, bins, xrange=range)

    means = scipy.stats.binned_statistic(x, y, bins=xaxis, statistic='mean').statistic
    std = scipy.stats.binned_statistic(x, y, bins=xaxis, statistic=scipy.stats.sem).statistic

    bin_centers = (xaxis[:-1] + xaxis[1:]) / 2.
    return plt.errorbar(x=bin_centers, y=means, yerr=std, linestyle='none', fmt=fmt, *args, **kwargs)
