import os
import glob
import datetime
import pandas as pd
from functools import reduce
from .abstract.pipeline_abc import feature_engineering


class FeatureEngineering(feature_engineering):

    def read_input(self):
        self.masterdata = pd.read_csv(self.input)
        
        
    def feature_engineering(self):
        
        masterdata = self.masterdata
        self._logger().info('Creating asof_yyyymm index column')
        masterdata['asof_yyyymm'] = (masterdata['year'].astype(str) +
                                     masterdata['month'].astype(str)
                                    .apply(lambda x: 
                        f'{datetime.datetime.strptime(x, "%B").month:02}'))\
                        .astype(int)

#         masterdata = masterdata.drop(columns=['zip', 'month', 'year'])
        masterdata = masterdata.drop(columns=['month', 'year'])
        self.masterdata = masterdata
        
    def write_output(self):
        self.masterdata.to_csv(self.output, index=False)

