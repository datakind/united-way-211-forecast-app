import os
import yaml
import argparse
import pandas as pd
import pathlib

from src import pipeline

parser = argparse.ArgumentParser(description='Command Line Arguments For ' +
                                 'Driver Code')
parser.add_argument('config_yaml',
                    help='Path to config.yaml file.')

parser.add_argument('--211', dest='fp_211', required=True,
                    help='Path to 211 data folder'
                   )


def run(config):
    if config['runFLAGS']['runETL']:
        input_url = config['etl_config']['url']
        output_fp = os.path.join(config['output_fp'], 'etl')
        pathlib.Path(output_fp).mkdir(parents=True, exist_ok=True)


        process = pipeline.etl.ETL(input_url, output_fp)
        process.read_input()
        process.etl()
        process.write_output()



    if config['runFLAGS']['runDATA_QUALITY']:
        if config['data_qulaity_config']['data_fp']:
            input_fp = config['data_qulaity_config']['data_fp']
        else:
            input_fp = os.path.join(config['output_fp'], 'etl')
        output_fp = os.path.join(config['output_fp'], 'data_qulaity')
        pathlib.Path(output_fp).mkdir(parents=True, exist_ok=True)

        process = pipeline.data_quality\
                .DataQuality(input_fp, output_fp)
        process.read_input()
        process.data_quality()
        process.write_output()



    if config['runFLAGS']['runPREPROCESSING']:
        if config['preprocessing_config']['data_fp']:
            input_fp = config['preprocessing_config']['data_fp']
        else:
            input_fp = os.path.join(config['output_fp'], 'data_qulaity')
        output_fp = os.path.join(config['output_fp'], 'preprocessing')
        pathlib.Path(output_fp).mkdir(parents=True, exist_ok=True)
        output_fp = os.path.join(output_fp, 'masterdata.csv')

        process = pipeline.preprocessing\
                    .Preprocessing(input_fp, output_fp)
        process.read_input()
        process.preprocessing(config['preprocessing_config']['zip_data_fp'],
                              config['preprocessing_config']['map_fp'],
                              config['preprocessing_config']['filter_time']
                             )
        process.write_output()


    if config['runFLAGS']['runEDA']:
        if config['eda_config']['data_fp']:
            input_fp = config['eda_config']['data_fp']
        else:
            input_fp = os.path.join(config['output_fp'], 'prepprocessing')
        output_fp = os.path.join(config['output_fp'], 'eda')
        pathlib.Path(output_fp).mkdir(parents=True, exist_ok=True)

        process = pipeline.eda\
                    .EDA(input_fp, output_fp)
        process.read_input()
        process.eda()
        process.write_output()


    if config['runFLAGS']['runFEATURE_ENGINEERING']:
        if config['feature_engineering_config']['data_fp']:
            input_fp = config['feature_engineering_config']['data_fp']
        else:
            input_fp = os.path.join(config['output_fp'],
                                    'preprocessing',
                                    'masterdata.csv'
                                   )
        output_fp = os.path.join(config['output_fp'],
                                 'feature_engineering')
        pathlib.Path(output_fp).mkdir(parents=True, exist_ok=True)
        output_fp = os.path.join(output_fp, 'masterdata.csv')


        process = pipeline.feature_engineering\
                    .FeatureEngineering(input_fp, output_fp)
        process.read_input()
        process.feature_engineering()
        process.write_output()


    if config['runFLAGS']['runMODEL_TRAINING']:
        if config['model_training_config']['data_fp']:
            input_fp = config['model_training_config']['data_fp']
        else:
            input_fp = os.path.join(config['output_fp'],
                                    'feature_engineering', 'masterdata.csv')
        output_fp = os.path.join(config['output_fp'],
                                 'model_training')

        if not config['model_training_config']['test_size']:
            config['model_training_config']['test_size'] = 4
        pathlib.Path(output_fp).mkdir(parents=True, exist_ok=True)

        process = pipeline.model_training\
                    .ModelTraining(input_fp, output_fp)
        process.read_input()
        process.model_training(config['model_training_config']['test_size'])
        process.write_output()


    if config['runFLAGS']['runMODEL_SCORING']:
        if config['model_scoring_config']['data_fp']:
            input_fp = config['model_scoring_config']['data_fp']
        else:
            input_fp = os.path.join(config['output_fp'],
                                 'model_training')
        output_fp = os.path.join(config['output_fp'],
                                 'model_scoring')
        pathlib.Path(output_fp).mkdir(parents=True, exist_ok=True)
        output_fp = os.path.join(output_fp, 'predictions.csv')


        if not config['model_scoring_config']['forecast_start']:
            with open(os.path.join(input_fp, 'model_info.yaml'), 'r') as fn:
                train_end = yaml.safe_load(fn)['train_end_time']
            forecast_start = pd.to_datetime(train_end, format=("%Y%m"))+ \
                        pd.DateOffset(months=1)

        if not config['model_scoring_config']['forecast_size']:
            config['model_scoring_config']['forecast_size'] = 3

        forecast_end = forecast_start + \
            pd.DateOffset(months=config['model_scoring_config']\
                                          ['forecast_size'])

        if os.path.isdir(input_fp):
            input_fp = os.path.join(input_fp, 'model.pkl')
        process = pipeline.model_scoring\
                    .ModelScoring(input_fp, output_fp)
        process.read_input()
        process.model_scoring(forecast_start, forecast_end)
        process.write_output()


    if config['runFLAGS']['runPOST_SCORING_ENGINEERING']:
        if config['post_scoring_engineering_config']['data_fp']:
            input_fp = config['post_scoring_engineering_config']['data_fp']
        else:
            input_fp = s.path.join(config['output_fp'],
                                   'model_scoring', 'predictions.csv')
        output_fp = os.path.join(config['output_fp'],
                                 'post_scoring_engineering')
        pathlib.Path(output_fp).mkdir(parents=True, exist_ok=True)
        output_fp = os.path.join(output_fp, 'predictions.csv')


        process = pipeline.post_scoring_engineering\
                    .PostScoringEngineering(input_fp, output_fp)
        process.read_input()
        process.post_scoring_engineering()
        process.write_output()


    if config['runFLAGS']['runCREATE_VIZ']:
        if config['create_viz_config']['data_fp']:
            input_fp = config['create_viz_config']['data_fp']
        else:
            input_fp = config['output_fp']
        output_fp = os.path.join(config['output_fp'],
                                 'create_viz')
        pathlib.Path(output_fp).mkdir(parents=True, exist_ok=True)
        output_fp = os.path.join(output_fp, 'forecast.png')


        process = pipeline.create_viz.CreateViz(input_fp, output_fp)
        process.read_input('feature_engineering', 'model_scoring')
        # process.create_viz()
        # process.write_output()
        process.create_plotly_viz()



if __name__ == '__main__':

    argument = parser.parse_args()
    config_fn = argument.config_yaml
    fp_211 = argument.fp_211

    with open(config_fn, 'r') as fn:
        config = yaml.safe_load(fn)

    config['preprocessing_config']['data_fp'] = fp_211

    run(config)
