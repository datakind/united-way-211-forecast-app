import pandas as pd
import statsmodels as sm
from joblib import load
from .abstract.pipeline_abc import model_scoring

class ModelScoring(model_scoring):
    def read_input(self):
        self.model = load(self.input)
        
        
    def model_scoring(self, start, end):
        ets_model = self.model
        pred = ets_model.get_prediction(start=start, end=end, dynamic=True)
        
        pred_ci = pred.conf_int()
        pred = pred.predicted_mean
        
            
        self.pred = pd.concat([pred, pred_ci], axis=1)
        self.pred = self.pred.rename_axis('asof_yyyymm')
        self.pred.index = self.pred.index.strftime("%Y%m")
        
    def write_output(self):
        self.pred.to_csv(self.output)