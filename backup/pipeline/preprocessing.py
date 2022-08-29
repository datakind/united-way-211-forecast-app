import os
import glob
import pandas as pd
import datetime

from .abstract.pipeline_abc import preprocessing

class Preprocessing(preprocessing):
    def read_input(self):
        self.raw_211_fp = self.input
        self.years = os.listdir(self.raw_211_fp)
        
    def preprocessing(self, zip_file=None, map_fp=None, filter_time=None):
        global logger
        logger=self._logger()
        data_211 = merge_211_files(self.raw_211_fp, 
                                   self.years, 
                                   zip_file=zip_file)
        data_211 = map_211_service_category(data_211, map_fp, verbose=True)
        data_211 = create_211_volume(data_211, zip_agg=False)
        if filter_time:
            logger.info(f'Filter times priot to {filter_time}')
            data_211 = data_211.loc[(data_211['year'].astype(str) +
                                     data_211['month'].astype(str)
                                     .apply(lambda x: 
                        f'{datetime.datetime.strptime(x, "%B").month:02}'))\
                        .astype(int) >= filter_time, :]
        
        self.data_211 = data_211
        
        
    def write_output(self):
        self.data_211.to_csv(self.output, index=False)
    

def merge_211_files(path: str, years: list, zip_file: str = None):

    """

    Combines date, time and service files on 'Transaction ID'.  Files
    must be saved in 'path' directory as [file]_[year].xls.  Ex. date_2018.xls

    :param self: reference to current class instant.
    :param path: full or relative path to time, date and service files.
    :param years: years for which 211 data needs to be merged.
    :param zipcode: (optional) if provided, adds zip code to 211 call data 

    :returns: data_frame_211, a pandas dataframe with transaction id, contact
    start time and date and referred service

    """

    data_files = []
    try:
        years.remove('.DS_Store')
    except:
        pass

    for year in years:

        try: 
            assert os.path.isdir(path) 
        except AssertionError:
            logger.info(f'{path} is not a directory')
            raise
        try: 
            assert os.path.isfile(f'{path}/{year}/time_{year}.xls') 
        except AssertionError:
            logger.info(f'time file for year {year} not found')
            raise
        try: 
            assert os.path.isfile(f'{path}/{year}/date_{year}.xls') 
        except AssertionError:
            logger.info(f'date file for year {year} not found')
            raise
        try: 
            assert os.path.isfile(f'{path}/{year}/service_{year}.xls') 
        except AssertionError:
            logger.info(f'service file for year {year} not found')
            raise

        # time file
        time_file = pd.read_excel(f'{path}/{year}/time_{year}.xls',
                               sheet_name='Report Raw Data')
        time_file = time_file.loc[time_file['Contact Start Time'].notna()]

        # date file
        date_file = pd.read_excel(f'{path}/{year}/date_{year}.xls',
                               sheet_name='Report Raw Data')
        date_file = date_file.loc[date_file['Contact Start Date'].notna(), # drop 211 calls without time stamp
                                  ['Transaction ID', 'Contact Start Date']]

        # service file
        service_file = pd.read_excel(f'{path}/{year}/service_{year}.xls',
                               sheet_name='Report Raw Data')
        service_file['count'] = service_file.groupby('Transaction ID')['Transaction ID'].transform('count')

        # drop NA service if other service is associated with Transaction ID
        service_file = service_file.loc[~((service_file['count'] > 1) & service_file['Referred Services'].isna()) 
                     & service_file['Transaction ID'].notna(),
                     ['Transaction ID', 'Referred Services']]

        final_file = time_file.merge(date_file, on='Transaction ID', how='inner')\
                              .merge(service_file, on='Transaction ID', how='inner')

        data_files.append(final_file)

    data_frame_211 = pd.concat(data_files, axis=0)

    data_frame_211['Contact Start Date'] = pd.to_datetime(data_frame_211['Contact Start Date'])

    if zip_file is not None: # if zip code file provided, add zip code column

        try:
            assert os.path.isfile(f'{zip_file}')  
        except AssertionError:
            logger.info(f'zip code file not found')
            raise

        zip_211 = pd.read_csv(f"{zip_file}")

        data_frame_211 = data_frame_211.merge(zip_211, how='left', left_on='Transaction ID', right_on='ContactID')

        data_frame_211 = data_frame_211.rename(columns={'SearchOptionZIPCode':'zip'})

    return data_frame_211

def map_211_service_category(data_frame_211: pd.DataFrame, map_file_path: str, verbose: bool = True):

    """

    Maps 211 service to high-level service category

    :param self: reference to current class instant.
    :param data_frame_211: data frame of 211 calls with 'Referred Service' column
    :param map_file_path: path to map (csv) file with 'Referred Service' and 'AIRS Problem Needs' columns
    :param verbose: if True (default) print % of 211 call services that map to high-level category

    :returns: data_frame_211, a pandas dataframe with new high-level service category column

    """
    try:
        assert os.path.isfile(f"{map_file_path}")  
    except AssertionError:
        logger.info('Map File Not Found, check file name and path')
        raise

    tax_211 = pd.read_csv(f"{map_file_path}")\
              .loc[:,['Referred Services', 'AIRS Problem Needs']]\
              .drop_duplicates()

    service_dict = dict(zip(tax_211['Referred Services'],
                       tax_211['AIRS Problem Needs']))

    data_frame_211['Referred Services Category'] = data_frame_211['Referred Services'].map(service_dict)

    if verbose:
        map_percent = data_frame_211.loc[data_frame_211['Referred Services'].notna(), 'Referred Services Category'].notna().mean()
        logger.info(f"{map_percent:.2%} of Referred Services map to high-level service category")

    return data_frame_211

def create_211_volume(data_frame_211, zip_agg=True):

    """

    Converts long 211 data file to wide to create 211 volume dataset for forecast prediction

    :param self: reference to current class instant.
    :param data_frame_211: data frame of 211 calls with 'Contact Start Date', 'Referred Service' columns
    :param zip_agg: if True (defualt) aggregate 211 call volume using 'zip' column

    :returns: volume_211: Monthly 211 call volume aggregated by county or zip level.  One column for each of 
    housing, utility service, food assistance and total calls.  

    """

    data_frame_211['month'] = data_frame_211['Contact Start Date'].dt.month_name()
    data_frame_211['year'] = data_frame_211['Contact Start Date'].dt.year.astype(str)

    if zip_agg:

        total = data_frame_211.groupby(['zip', 'month', 'year']).size()
        house = data_frame_211.loc[data_frame_211['Referred Services Category'] == 'Housing'].groupby(['zip', 'month', 'year']).size()
        utx = data_frame_211.loc[data_frame_211['Referred Services Category'] == 'Utility Assistance'].groupby(['zip', 'month', 'year']).size()
        food = data_frame_211.loc[data_frame_211['Referred Services Category'] == 'Food/Meals'].groupby(['zip', 'month', 'year']).size()

    else:

        total = data_frame_211.groupby(['month', 'year']).size()
        house = data_frame_211.loc[data_frame_211['Referred Services Category'] == 'Housing'].groupby(['month', 'year']).size()
        utx = data_frame_211.loc[data_frame_211['Referred Services Category'] == 'Utility Assistance'].groupby(['month', 'year']).size()
        food = data_frame_211.loc[data_frame_211['Referred Services Category'] == 'Food/Meals'].groupby(['month', 'year']).size()

    volume_211 = pd.concat([total, house, utx, food],
                           axis=1)

    volume_211.columns = ['total_calls', 'housing_calls', 'utx_calls', 'food_calls']

    volume_211 = volume_211.fillna(0.0)

    volume_211 = volume_211.reset_index()

    return volume_211

