# -*- coding: utf-8 -*-
""" Transfromation of Data

"""

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d, InterpolatedUnivariateSpline
from scipy.interpolate import UnivariateSpline
import scipy


class Transform():
    """
    Base Class for the transformations.
    The function _fit() is overwritten by the sub classes.

    """

    def __init__(self, name="Original", n_bins=None):
        self.n_bins = n_bins
        self.y = []
        self.x = []
        self.max = 0
        self.min = 0
        self.is_processed = False
        self.name = name
        # Base.__init__(self, "Transform."+self.name)

    def initialise(self, x):
        # self.io.debug("Initiating " + self.name)
        if self.n_bins is None:
            self.set_n_bins(len(x))
        #self.y, self.x = np.histogram(x, self.n_bins)
        self.max = np.max(x)
        self.min = np.min(x)

    def fit(self, x, y=None):
        self.initialise(x)
        self._fit(x, y)
        self.is_processed = True

    def __call__(self, x):
        return self.transform(x)

    def _fit(self, x, y=None):
        """
        This is defined in the children and overwritten.
        :param x: array x values
        :param y: class variable [1,0]

        """
        pass

    def transform(self, x):
        """
        This is defined in the children and overwritten.
        In the base class it does nothing and returns the original distribution.

        """
        return x

    def set_n_bins(self, n):
        self.n_bins = get_optimal_bin_size(n)
        # self.io.debug("Bins are set to " + str(self.n_bins) + "\t " + str(n/float(self.n_bins)) + "per bin")

    def set_limits(self, x):
        try:
            l = len(x)
            x[x>self.max] = self.max
            x[x<self.min] = self.min
        except TypeError:
            if x < self.min: x = self.min
            if x > self.max: x = self.max
        return x


def get_optimal_bin_size(n):
    """
    This function calculates the optimal amount of bins for the number of events n.
    :param      n:  number of Events
    :return:        optimal bin size

    """
    return int(2 * n**(1/3.0))


def get_average_in_bins(n):
    return n/float(get_optimal_bin_size(n))


class MySpline():
        """ can be pickled
        """
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __call__(self, x, *args, **kwargs):
            return np.interp(x, self.x, self.y)


class CDF(Transform):
    """
    Calculates the cummulative distribution (CDF)

    """

    def __init__(self, *args):
        Transform.__init__(self, "CDF", *args)
        self.spline = None

    def _fit(self, x, y=None):
        # self.io.debug("Fitting CDF")

        self.y = np.linspace(0, 100, 2*self.n_bins)
        self.x = pd.Series(np.percentile(x, list(self.y)))

        # # Count same values
        # vc = self.x.value_counts()
        # vc = vc.sort_index()

        self.spline = MySpline(self.x, self.y)

    def transform(self, x):
        x = self.set_limits(np.copy(x))
        return self.spline(x)


class ToFlat(Transform):
    """
    This transformation uses the CDF to transform input data to a
    flat transformation.

    """
    def __init__(self, x=None, *args):
        Transform.__init__(self, "Flat", *args)
        self.cdf = CDF(*args)
        if x is not None:
            self.fit(x)

    def _fit(self, x, y=None):
        self.cdf.fit(x)

    def transform(self, x):
        if not self.is_processed:
            self.fit(x)
        return self.cdf.transform(x)


class ToGauss(Transform):

    def __init__(self, *args):
        Transform.__init__(self, "Gauss", *args)
        self.flat = ToFlat(*args)

    def _fit(self, x, y=None):
        self.flat.fit(x)

    def transform(self, x):
        xx = self.flat.transform(x)
        xx[xx>=1] = 0.99999  # erfinv does not want 1
        xx[xx==0] = 0.00001  # erfinv does not want 1
        return scipy.special.erfinv(xx*2-1)


class MapTo(Transform):
    """ Linear map to some values
    """

    def __init__(self, fromlow, fromhigh, tolow, tohigh, limit=False, *args):
        Transform.__init__(self, "MapTo", *args)
        self.x_diff = float(fromlow - tolow)
        self.len_from = float(fromhigh - fromlow)
        self.len_to = float(tohigh - tolow)

    def transform(self, x):
        return self.len_to*x/self.len_from-self.x_diff


class To11(Transform):

    def __init__(self, *args):
        Transform.__init__(self, "Scaled -1 1", *args)

    def transform(self, x):
        length = self.max - self.min
        x -= self.min
        x /= (length*1.0)
        return x*2 - 1



class ToNorm(Transform):

    def __init__(self):
        Transform.__init__(self,"Normalised")
        self.mean = 0
        self.var = 1

    def _fit(self, x, y=None):
        self.mean = np.mean(x)
        self.var = np.var(x)
        if self.var is 0 or np.nan:
            self.var = 1

    def transform(self, x):
        x -= self.mean
        return x/self.var


# class Pipe(Transform):
#     """ Pipeline for the transform functions """

#     def __init__(self, *args):
#         Transform.__init__(self, "Piped", *args)
#         self.functions = []

#     def add(self, f):
#         if f in self.functions:
#             # self.io.warn("Function already in Pipeline!")
#             return
#         self.functions.append(f)

#     def _fit(self, x, y=None):
#         xx = x.copy()
#         for f in self.functions:
#             f.fit(xx)
#             xx = f.transform(xx)
#         self.is_processed = True

#     def transform(self, x):
#         xx = x.copy()
#         for f in self.functions:
#             xx = f.transform(xx)
#         return xx

#     def present(self, x, y):
#         for f in self.functions:
#             print(f)


# class ToPurity(Transform):

#     def __init__(self, n_bins = None):
#         Transform.__init__(self, "Purity", n_bins)
#         self.flat = ToFlat(self.n_bins)
#         self.spline = None
#         self.purity = []
#         self.purity_err = []
#         self.bincenters = None

#     def _fit(self, x, y=None):
#         if y is None:
#             return
#         self.flat.fit(x)
#         y1,x1 = np.histogram(self.flat.transform(x[y == 1]),  self.n_bins)
#         y0,x0 = np.histogram(self.flat.transform(x[y == 0]), x1)
#         n_events_in_bin = y1 + y0
#         self.purity = np.array(y1/(y1+y0*1.0))
#         self.purity_err = (self.purity*(1-self.purity))/(n_events_in_bin*1.0)
#         weight = np.array(1/(np.sqrt(self.purity_err*1.0) + 0.00001)) # Jo that's not good
#         bincenters = np.array(0.5*(x1[1:]+x1[:-1]))
#         bincenters[0] = 0
#         bincenters[self.n_bins -1] = 1
#         nan_values = np.isnan(self.purity)
#         if len(nan_values[nan_values == True]) > 0:
#             self.io.warn(str(len(bincenters)) + 'Nan Values in Spline: ' + str(len(nan_values[nan_values == True])))
#         self.spline = UnivariateSpline(bincenters[~nan_values], self.purity[~nan_values], w=weight[~nan_values]/float(len(nan_values[nan_values == True])+1))
#         self.bincenters = bincenters
#         self.is_processed = True

#     def transform(self, x):
#         return self.spline(self.flat.transform(x))


class ToRawPurity(Transform):

    def __init__(self, n_bins=None):
        Transform.__init__(self, "RawPurity", n_bins)
        self.purity = []
        self.pur_err = []

    def _fit(self, x, y=None):
        if y is None:
            return

        x1 = pd.value_counts(x[y==1])
        n_events_in_bin = pd.value_counts(x)
        self.purity = x1 / (n_events_in_bin)
        self.purity[self.purity.isnull()] = 0
        self.purity_err = (self.purity*(1-self.purity))/(n_events_in_bin*1.0)

    def transform(self, x):
        return self.purity[x].values