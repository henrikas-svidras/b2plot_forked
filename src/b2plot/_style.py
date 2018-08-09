# -*- coding: utf-8 -*-
"""
Controls the style for matplolib via seaborn.

"""

import seaborn as sns
import matplotlib.pyplot as plt


def set_default_style():
    plt.style.use("classic")
    sns.set_style('white')
    sns.set_context("notebook", font_scale=1.5, rc={'axes.labelsize': 22})
    sns.set_style('ticks', {'axes.axisbelow': False,'xtick.direction': u'in','ytick.direction': u'in'})
    plt.ticklabel_format(style='sci', axis='x', scilimits=(-2, 4))
    plt.ticklabel_format(style='sci', axis='y', scilimits=(-2, 4))
    plt.rc('axes', linewidth=1.2)
    import matplotlib as mpl
    mpl.rcParams['mathtext.fontset'] = 'cm'
    mpl.rcParams['mathtext.rm'] = 'serif'
    # mpl.rcParams['axes.autolimit_mode'] = 'round_numbers'
    plt.style.use("belle2")

def set_small_style():
    sns.set_context("paper", font_scale=1.5, rc={'axes.labelsize': 18})
    sns.set_style('ticks', {'axes.axisbelow': False,'xtick.direction': u'in','ytick.direction': u'in'})
