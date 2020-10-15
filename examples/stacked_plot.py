# -*- coding: utf-8 -*-
""" Stacked plot

In data science, often one wants to compare two different sets of data, like signal/background or prediction and
actual data.

In this very brief script we create two sets of data and compare them in one plot.

"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import b2plot as bp

try:
    plt.style.use('belle2')
except OSError:
    print("Please install belle2 matplotlib style")

# Create some pseudo data
nb = 5000
ns = 3000
df = dict({'mass': np.append(np.random.random_sample(nb)*7 - 3.5, np.random.normal(0, 0.5, ns))})
df['exp'] = np.random.randint(0, 6, ns+nb)
df = pd.DataFrame(df)

# Automatic creation of a stacked plot of 'mass' split by values of 'exp'
bp.stacked(df, col="mass", by='exp', bins=50, scale=[1,1,1,1,10,1])
plt.legend()

bp.xlim()
bp.labels('$\Delta M$', "Events", "GeV", 0)
bp.save("stacked_plot.png")
