# -*- coding: utf-8 -*-
"""
In this file all the matplolib wrappers are located.

"""

import numpy as np
import matplotlib.pyplot as plt

from .helpers import TheManager


def remove_nans(data, weights=None, stacked=False):
    """
    Remove NaN elements in data array, and corresponding weights too.
    """

    if not stacked:
        data_new = data[~np.isnan(data)]
    else:
        data_new = [d[~np.isnan(d)] for d in data]
    weights_new = None
    if weights is not None:
        if not stacked:
            weights_new = weights[~np.isnan(data)]
        else:
            weights_new = [w[~np.isnan(data[idx])] for idx, w in enumerate(weights)]

    return data_new, weights_new


def clip_data(data, bins=None, x_range=None):
    """
    Clip np.array at first, last = x_range
    Use when merging under/overflow into first/last visible bin.
    """

    first = last = None
    if isinstance(x_range, tuple):
        first, last = x_range
    if isinstance(bins, np.ndarray):
        first, last = bins.flat[0], bins.flat[-1]
    if isinstance(bins, list):
        first, last = bins[0], bins[-1]

    if first is not None and last is not None:
        return np.clip(data, first, last)

    return data


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
