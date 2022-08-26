import os
import pandas as pd
os.environ['MPLCONFIGDIR'] = os.getcwd() + "/configs/"
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.pylab import rcParams
from .abstract.pipeline_abc import create_viz


class CreateViz(create_viz):
    def read_input(self, master_step, pred_step):
        self.masterdata = pd.read_csv(os.path.join(self.input,
                                                   master_step,
                                                   'masterdata.csv'
                                                   ))
        self.masterdata['asof_yyyymm'] = \
            pd.to_datetime(self.masterdata['asof_yyyymm']
                           .astype(str), format=("%Y%m"))

        self.masterdata = self.masterdata.set_index('asof_yyyymm')

        self.pred = pd.read_csv(os.path.join(self.input,
                                             pred_step,
                                             'predictions.csv'
                                             ))

        self.pred['asof_yyyymm'] = \
            pd.to_datetime(self.pred['asof_yyyymm']
                           .astype(str), format=("%Y%m"))

        self.pred = self.pred.set_index('asof_yyyymm')

    def create_viz(self):
        matplotlib.style.use('classic')
        matplotlib.style.use('seaborn-white')
        rcParams['figure.figsize'] = (16, 8)

        pred = self.pred
        masterdata = self.masterdata

        endog = masterdata.columns

        fig, axs = plt.subplots(4, 1, figsize=(16, 16))

        for ax, c in zip(axs, endog):

            masterdata[[c]].append(pred[[c]])\
                .rename(columns={c: 'History'}).plot(c='blue', ax=ax, lw=2)

            pred[[c]].rename(columns={c: 'Forecast'}).plot(c='red',
                                                           ax=ax, lw=2)
            ax.fill_between(pred.index,
                            pred.loc[:, 'lower ' + c],
                            pred.loc[:, 'upper ' + c],
                            color='r', alpha=0.1)

            ax.minorticks_on()
            ax.set_xlabel('Month', fontsize=12)
            ax.set_title(f'Monthly 211 demand volume ({c})', fontsize=15)
            ax.legend(loc='best')
            ax.grid(which='both')
        plt.tight_layout()
        plt.show()
        self.fig = fig

    def write_output(self):
        self.fig.savefig(self.output, dpi=self.fig.dpi)
