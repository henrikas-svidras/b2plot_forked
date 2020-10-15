import pkg_resources

__version__ = pkg_resources.get_distribution(__name__).version

from .functions import xlim, save, save_adjust
from .histogram import hist, errorbar, stacked, to_stack, errorhist, set_xaxis
from .analysis import sig_bkg_plot
from .helpers import xaxis, nf, figure
from .decorations import draw_y_label, decorate, expand, watermark, lumi, labels, text
from .colors import cm, b2helix
from .correlations import flat_correlation, flat_corr_matrix
from .mva import plot_features, mva_input_plot

print("For optimal usage set `plt.style.use('belle2')`")
