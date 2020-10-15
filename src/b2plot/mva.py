# -*- coding: utf-8 -*-
""" Tools to analyse data for mva trainings

"""
import pandas as pd
import matplotlib.pyplot as plt
from .helpers import nf
from .histogram import to_stack, errorhist
from .decorations import decorate
from .analysis import sig_bkg_plot
from .colors import cm
from .analysis import mask_append


def mva_input_plot(x_sig, x_bkg, density=True, log=False, *args, **kwargs):
    
    try:
        import seaborn as sns
    except ImportError:
        print("this feature need seaborn")
        return

    x,y = mask_append(x_sig, x_bkg)

    f, axes = plt.subplots(2, 1, gridspec_kw={"height_ratios": [3, 1]}, sharex=True, )
    f.subplots_adjust(hspace=0.0)

    sig_bkg_plot(x_sig, x_bkg,  ax= axes[0], normed=density, labels=["Background", "Signal"],  *args, **kwargs)
    if log:
        axes[0].semilogy()

    if len(x_sig) < 5000:
        errorhist(x_sig, color=1, ax=axes[0], normed=density, box=True, alpha=.2, zorder=-1)
    if len(x_bkg) < 5000:
        errorhist(x_bkg, color=0, ax=axes[0], normed=density, box=True, alpha=.2, zorder=-2)

    axes[0].legend()
    
    sns.boxplot(x=x, y=y,  orient='h', ax=axes[1], palette=cm(2)[::-1],linewidth=1,fliersize=1)
    axes[1].set_yticks([])
    return axes
    # decorate(xlabel)


def plot_features(df, variables, condition, *args, **kwargs):
    
    for v in variables:
        b2plot.nf()
        mva_input_plot(df,v,condition,*args, **kwargs)
        b2plot.decorate(v)
