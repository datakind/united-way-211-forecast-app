import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    STATIC_FOLDER = f"{os.getenv('APP_HOME')}/project/static"
    MEDIA_FOLDER = f"{os.getenv('APP_HOME')}/project/media"
    UPLOAD_FOLDER = f"{os.getenv('APP_HOME')}/project/uploads"

    runFLAGS = {
        'runETL': False,
        'runDATA_QUALITY': False,
        'runPREPROCESSING': False,
        'runEDA': False,
        'runFEATURE_ENGINEERING': True,
        'runMODEL_TRAINING': True,
        'runMODEL_SCORING': True,
        'runPOST_SCORING_ENGINEERING': False,
        'runCREATE_VIZ': False
    }

    ################################################################################
    #
    # Local Configs:
    #
    ################################################################################

    output_fp = "./run"

    etl_config = {
        'url': None
    }
    data_quality_config = {
        'data_fp': None
    }

    preprocessing_config = {
        'data_fp': None,
        # zip_data_fp:
        'map_fp': "211_map.csv",
        'filter_time': 201907
    }

    eda_config = {
        'data_fp': None
    }
    feature_engineering_config = {
        'data_fp': None
    }
    model_training_config = {
        'data_fp': None,
        'test_size': 4
    }
    model_scoring_config = {
        'data_fp': None,
        'forecast_start': None,
        'forecast_size': None
    }
    post_scoring_engineering_config = {
        'data_fp': None
    }
    create_viz_config = {
        'data_fp': None,
    }
