import os
import sys
# import logging
from loguru import logger

from abc import ABC, abstractmethod


class init_abc(ABC):
    """

    Init Abstract Base Class (ABC) that will be used as parend ABC for other pipelin

    :param input_path: Path to input file/directory name
    :type input_path: str (input_data.csv)
    :param output_path: Path to output file/directory name
    :type output_path: str (output_data.csv)


    :returns: self, a reference to current class instant (customizable)

    """

    def __init__(
        self,
        input_path,
        output_path,
    ):
        self.input = input_path
        self.output = output_path


    def __version__(self):
        print("0.1")
        return "0.1"

    def _logger(self):
        # logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        # log = logging.getLogger(__name__)
        # return log
        logger.add("run/job.log", format="{time} - {message}")
        return logger

    @abstractmethod
    def read_input(self):
        """

        Read Input Abstract Method that needs to be implemented to read input
        data.

        :param self: reference to current class instant.

        :returns: self, a reference to current class instant (customizable)

        """

    @abstractmethod
    def write_output(self):
        """

        Write Output Abstract Method that needs to be implemented to write
        output data.

        :param self: reference to current class instant.

        :returns: self, a reference to current class instant (customizable)

        """



class etl(init_abc):

    @abstractmethod
    def extract(self, api_url, api_key, table):

        """

        Extract Abstract Method that needs to be implemented to extract the data
        from source.

        :param self: reference to current class instant.
        :param api_url: str, API URL path
        :param api_key: str, API key value
        :param table: str, Name of the table to be extracted.

        :returns: self, a reference to current class instant (customizable)

        """


    @abstractmethod
    def transform(self):
        """

        Transform Abstract Method that needs to be implemented to transform the
        data prior to loading.

        :param self: reference to current class instant.

        :returns: self, a reference to current class instant (customizable)

        """


    @abstractmethod
    def load(self):
        """

        Load Abstract Method that needs to be implemented to load the data
        into final location for preprocessing.

        :param self: reference to current class instant.

        :returns: self, a reference to current class instant (customizable)

        """

        pass


class data_quality(init_abc):

    @abstractmethod
    def data_quality(self):
        """

        Data Quality Abstract Method that needs to be implemented to check
        the quality of input data.

        :param self: reference to current class instant.

        :returns: self, a reference to current class instant (customizable)

        """


class eda(init_abc):

    @abstractmethod
    def eda(self):
        """

        Exploratory Data Analysis Abstract Method that needs to be implemented to produce
        eda report.

        :param self: reference to current class instant.

        :returns: self, a reference to current class instant (customizable)

        """

class preprocessing(init_abc):

    @abstractmethod
    def preprocessing(self):

        """

        Preprocessing Abstract Method that needs to be implemented to perform
        preprocessing steps such as cleanup and data joins

        :param self: reference to current class instant.

        :returns: self, a reference to current class instant (customizable)

        """


class feature_engineering(init_abc):

    @abstractmethod
    def feature_engineering(self):

        """

        Feature Engineering Abstract Method that needs to be implemented to perform
        feature engineering computation

        :param self: reference to current class instant.

        :returns: self, a reference to current class instant (customizable)

        """


class model_training(init_abc):

    @abstractmethod
    def model_training(self):

        """

        Model Training Abstract Method that needs to be implemented to perform
        model training computation

        :param self: reference to current class instant.

        :returns: self, a reference to current class instant (customizable)

        """

class model_scoring(init_abc):

    @abstractmethod
    def model_scoring(self):

        """

        Model Scoring Abstract Method that needs to be implemented to perform
        model scoring computation

        :param self: reference to current class instant.

        :returns: self, a reference to current class instant (customizable)

        """

class post_scoring_engineering(init_abc):

    @abstractmethod
    def post_scoring_engineering(self):

        """

        Post Scoring Engineering Abstract Method that needs to be implemented to perform
        any post scoring engineering computation

        :param self: reference to current class instant.

        :returns: self, a reference to current class instant (customizable)

        """

class create_viz(init_abc):

    @abstractmethod
    def create_viz(self):

        """

        Create Viz Abstract Method that needs to be implemented to produce
        reporting visualizations

        :param self: reference to current class instant.

        :returns: self, a reference to current class instant (customizable)

        """
