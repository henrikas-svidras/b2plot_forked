# -*- coding: utf-8 -*-
"""

"""

from .helpers import manager
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties


def draw_y_label(label='Entries', unit=None, ha='right', brackets=True, *args, **kwargs):
    """ Plotting scientific notation y label


    Args:
        label:
        unit:
        ha:
        brackets:
        *args:
        **kwargs:

    Returns:

    """
    br_open = ''
    br_close = ''
    if brackets:
        br_open = ' ('
        br_close = ')'
    if brackets == 'square':
        br_open = ' ['
        br_close = ']'

    x_axis = manager.get_x_axis()
    if unit is None:
        plt.ylabel(label, ha=ha, *args, **kwargs)
    else:
        try:
            width = x_axis[1] - x_axis[0]
        except TypeError:
            plt.ylabel(label+' /' + br_open + ' ' + unit + br_close, ha=ha, *args, **kwargs)
        else:
            plt.ylabel(label+' /' + br_open + "{0:.3f}".format(width).rstrip('0').rstrip('.') + ' ' + unit + br_close, ha=ha, *args, **kwargs)


def watermark(t=None,logo="Belle II", px=0.033, py=0.915, fontsize=16, alpha=0.8, alpha_logo=0.95, shift=0.15, bstyle='italic', *args, **kwargs):
    """

    Args:
        t:
        logo:
        px:
        py:
        fontsize:
        alpha:
        shift:
        *args:
        **kwargs:

    Returns:

    """
    if t is None:
        import datetime
        t = " %d (internal)" % datetime.date.today().year

    plt.text(px, py, logo, ha='left',
             transform=plt.gca().transAxes,
             fontsize=fontsize,
             style=bstyle,
             alpha=alpha_logo,
             weight='bold',
             *args, **kwargs,
             # fontproperties=font,
             # bbox={'facecolor':'#377eb7', 'alpha':0.1, 'pad':10}
             )
    plt.text(px + shift, py, t, ha='left',
             transform=plt.gca().transAxes,
             fontsize=fontsize,
             #          style='italic',
             alpha=alpha,  *args, **kwargs
             #          fontproperties=font,
             # bbox={'facecolor':'#377eb7', 'alpha':0.1, 'pad':10}
             )


def lumi(l="$5\; \mathrm{pb}^{-1}$", px=0.033, py=0.839,  *args, **kwargs):
    plt.text(px, py, "$\int\,L\,\mathrm{dt}\;=\;$" + l, transform=plt.gca().transAxes, *args, **kwargs )


def text(t, px=0.033, py=0.763,  *args, **kwargs):
    plt.text(px, py, t, transform=plt.gca().transAxes, *args, **kwargs)


def expand(factor =1.2):
    plt.ylim(0, plt.ylim()[1] * factor)


def set_style():
    plt.ticklabel_format(style='sci', axis='y', scilimits=(-3, 4), useMathText=True)
    ax = plt.gca()
    ax.yaxis.set_ticks_position('both')
    ax.xaxis.set_ticks_position('both')
    plt.minorticks_on()
    # plt.tight_layout()

    plt.subplots_adjust(left=0.15, right=0.92, top=0.92, bottom=0.15)


def labels(xlabel=None, ylabel=None, unit=None, root_style=False, brackets=True, overwrite=None, *args, **kwargs):

    br_open = ''
    br_close = ''
    if brackets:
        br_open = ' ['
        br_close = ']'
    if brackets == 'round':
        br_open = ' ('
        br_close = ')'

    ha = 'center'
    x, y = .5, .5

    if root_style:
        ha = 'right'
        x, y = 1, 1

    if overwrite is not None:
        if xlabel in overwrite:
            try:
                xlable = overwrite[xlabel]
            except:
                pass

    if xlabel is not None:
        plt.xlabel(xlabel, horizontalalignment=ha, x=x, *args, **kwargs)

    if unit is not None:
        if unit is not '':
            plt.xlabel(xlabel + br_open + unit + br_close, ha=ha, x=x, *args, **kwargs)
        if ylabel is not None:
            draw_y_label(ylabel, unit,  horizontalalignment=ha, y=y, brackets=brackets, *args, **kwargs)
    else:
        if xlabel is not None:
            plt.xlabel(xlabel, horizontalalignment=ha, x=x,  *args, **kwargs)
        if ylabel is not None:
            draw_y_label(ylabel,  horizontalalignment=ha, y=y, brackets=brackets, *args, **kwargs)


def decorate(*args, **kwargs):
    labels(*args, **kwargs)
