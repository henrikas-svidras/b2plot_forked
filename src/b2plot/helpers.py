# -*- coding: utf-8 -*-
"""
Helper function and classes are defined here.

"""

import b2plot
# from .functions import bar

import matplotlib.pyplot as plt
import numpy as np


def hist2root(h, name=None, title=''):
    """ Convert your histograms to a root histogram.. if you really want to

    Args:
        h: array with the histogram h=(y_values, bin_edges, (patches=optional))
        name: Name for the root histogram, optional
        title: Title for the root histogram, optional

    Returns:
        TH1F or TH2F depending on the input array

    Examples:
        >>> data = [1,2,3,4,5,6,7]
        >>> h = b2plot.hist(data)
        >>> from b2plot.helpers import hist2root
        >>> root_hist = hist2root(h)

    """
    import root_numpy
    import random
    import ROOT

    y_values = h[0]
    name = "".join(random.choice("fck_root_wtf") for _ in range(5)) if name is None else name
    if len(h) > 3:
        rh = ROOT.TH2F(name, title, len(h[1]) - 1, h[1], len(h[2]) - 1, h[2])
    else:
        rh = ROOT.TH1F(name, title, len(h[1]) - 1, h[1])
    return root_numpy.array2hist(y_values, rh)


def get_optimal_bin_size(n):
    """
    This function calculates the optimal amount of bins for the number of events n.
    :param      n:  number of Events
    :return:        optimal bin size

    """
    return int(3 * n**(1/3.0))


class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Other than that, there are
    no restrictions that apply to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    Limitations: The decorated class cannot be inherited from.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)


@Singleton
class TheManager:
    def __init__(self):
        self.xaxis = None
        self.toreplot = []

    def get_x_axis(self):
        return self.xaxis

    def set_x_axis(self, axis):
        self.xaxis = axis

    def figure(self, *args, **kwargs):
        # f = plt.figure(tight_layout={'pad': 0})
        f = plt.figure(*args, **kwargs)
        self.xaxis = None
        self.toreplot = []
        return f

    def add_replot(self, h):
        self.toreplot.append(h)

    def replot(self, ecolor='black'):
        for h in self.toreplot:

            b2plot.bar(h[0], h[1], lw=1, histtype='step', color='black' )


manager = TheManager.Instance()


def xaxis():
    return TheManager.Instance().get_x_axis()


def nf():
    return TheManager.Instance().figure()


def figure(*args, **kwargs):
    return TheManager.Instance().figure(*args, **kwargs)

def replot():
    print("replotting")
    TheManager.Instance().replot()


def draw_colz(values, xedges, yedges, errup, errdown,
              XName='X', YName='Y',
              cbarName='efficiency',
              col_min=None, col_max=None,
              annotate=True, cmap='sequential',
              ax=None):
    """ Draws a COLZ plot, can be used in conjunction with divide_efficiency,
    annotates the bins if called.

    Args:
        values: values that correspond to each bin.
        xedges: edges that make up bins for x axis.
        yedges: edges that make up bins for y axis.
        errup, errdown:  upper/lower error for values, must be the same size as values.
        XName, YName: names for x and y axis.
        cbarName: name displayed next to color bar.
        col_min, col_max: minimum and maximum values for the color bar.
        annotate: if True, writes the value and errors.
        cmap: cmap to pass, as string. 'sequential' and 'diverging' exist as predefined defaults.
        ax: axis to draw on. If not specified creates new.

    Outputs:
        fig, ax: drawn figure and axis

    """

    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    fig = plt.gcf()

    if cmap == 'sequential':
        cmap = 'rocket'
    elif cmap == 'diverging':
        cmap = 'coolwarm'
    elif isinstance(cmap, str):
        cmap = cmap
    else:
        print('Neither sequential, nor diverging colormap selected.\
               Failed to read specified colormap. Defaulting to viridis.')
        cmap = 'viridis'

    # For whatever reason values have to be transposed in color mesh.
    colz = ax.pcolormesh(xedges, yedges, np.transpose(values),
                         vmin=col_min, vmax=col_max,
                         cmap=cmap, shading='flat')
    fig.colorbar(colz, ax=ax, label=cbarName)

    # Drawing the errors in each cell when annotate is True.
    if annotate:
        for ix, x in enumerate(xedges[:-1]):
            for iy, y in enumerate(yedges[:-1]):
                ratio = values[ix][iy]
                # Doesn't draw anything in cells with 0 efficiency or with nan.
                if not ratio or ratio != ratio:
                    continue
                err_up = errup[ix][iy]
                err_down = errdown[ix][iy]
                # This draw position and size might need some tweaking in the future.
                draw_position = (x+np.abs(x-xedges[ix+1])/2,
                                 y+np.abs(y-yedges[iy+1])/2.)
                size_points = 80*(np.abs(x-xedges[ix+1]))/np.abs(xedges[0]-xedges[-1])
                ax.annotate(f'${ratio:.3f}\pm^{{{err_up:.3f}}}_{{{err_down:.3f}}}$',
                            draw_position,
                            ha='center', va='center', size=size_points)

    ax.set_xlabel(XName)
    ax.set_ylabel(YName)
    ax.set_xlim(xedges[0], xedges[-1])
    ax.set_ylim(yedges[0], yedges[-1])

    return fig, ax
