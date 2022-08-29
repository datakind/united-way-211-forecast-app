import os
import yaml
import datetime
import pandas as pd
import statsmodels as sm
import statsmodels.tsa.statespace.varmax
from joblib import dump
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_percentage_error


from .abstract.pipeline_abc import model_training

class ModelTraining(model_training):
    def read_input(self):
        self.masterdata = pd.read_csv(self.input)
        
        
    def model_training(self, test_size):
        
        masterdata = self.masterdata
        masterdata['asof_yyyymm'] = pd.to_datetime(masterdata['asof_yyyymm']
                     .astype(str), format=("%Y%m"))
        masterdata = masterdata.set_index('asof_yyyymm').sort_index()
        masterdata = masterdata.asfreq('MS')
        masterdata = masterdata.astype('float32')

        n = len(masterdata)
        train = masterdata.iloc[:n - test_size, :]
        test = masterdata.iloc[n - test_size:, :]

        self._logger().info(f'Train time range: {train.index[0]} -> {train.index[-1]}')
        self._logger().info(f'Test time range: {test.index[0]} -> {test.index[-1]}')

        ets_model = sm.tsa.statespace.varmax.VARMAX(train,
                                                    trend='ct')
        ets_result = ets_model.fit(disp=0)
        
        self._logger().info(f'AIC\t\t{round(ets_result.aic,3)}')
        self._logger().info(f'AICc\t{round(ets_result.aicc,3)}')
        self._logger().info(f'BIC\t\t{round(ets_result.bic,3)}')
        self._logger().info(f'SSE\t\t{round(ets_result.sse,3)}')

        ets_test_pred = ets_result.get_prediction(start=test.index[0], 
                                                  end=test.index[-1], 
                                                  dynamic=True)
        
        ets_test_prediction = ets_test_pred.predicted_mean

        ets_test_ci = ets_test_pred.conf_int()
        
        for c in masterdata.columns:
            self._logger()\
                .info(f'Test MAPE ({c})\t\t{round(mean_absolute_percentage_error(test[c], ets_test_prediction[c]),3)}')


        

        self.model = sm.tsa.statespace.varmax.VARMAX(masterdata,
                                                     trend='ct').fit()
        self.end_time = pd.to_datetime(masterdata.index.values[-1])\
                            .strftime("%Y%m")
        
    def write_output(self):
        dump(self.model, os.path.join(self.output, 'model.pkl'))
        with open(os.path.join(self.output, 'model_info.yaml'), 'w') as fn:
            yaml.dump({'train_end_time': self.end_time}, fn)
        
             
        
        