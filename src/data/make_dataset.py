# -*- coding: utf-8 -*-
import os
import json
from urllib.request import urlretrieve, urlopen
from urllib.parse import urlsplit
import zipfile
import csv
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

RAW = 'data/raw'
PROCESSED = 'data/processed'

HORIZON_URL = 'https://cordis.europa.eu/data/cordis-HORIZONprojects-csv.zip'
H2020_URL = 'http://cordis.europa.eu/data/cordis-h2020projects-csv.zip'
FP7_URL = 'http://cordis.europa.eu/data/cordis-fp7projects-csv.zip'
CSV_FILES = ['https://cordis.europa.eu/data/FP6/cordis-fp6projects.csv',
             'https://cordis.europa.eu/data/FP6/cordis-fp6organizations.csv',
             'https://cordis.europa.eu/data/FP5/cordis-fp5organizations.csv',
             'https://cordis.europa.eu/data/FP5/cordis-fp5projects.csv',
             'https://cordis.europa.eu/data/FP4/cordis-fp4organizations.csv',
             'https://cordis.europa.eu/data/FP4/cordis-fp4projects.csv',
             'https://cordis.europa.eu/data/FP3/cordis-fp3organizations.csv',
             'https://cordis.europa.eu/data/FP3/cordis-fp3projects.csv',
             'https://cordis.europa.eu/data/FP2/cordis-fp2projects.csv',
             'https://cordis.europa.eu/data/FP2/cordis-fp2organizations.csv',
             'https://cordis.europa.eu/data/FP1/cordis-fp1organizations.csv',
             'https://cordis.europa.eu/data/FP1/cordis-fp1projects.csv']


def download_zip(url, path):
    zip_name = urlsplit(url).path.split('/')[-1]
    unzipped_folder = zip_name.split('.')[0]
    zip_path = os.path.join(path, zip_name)
    unzipped_path = os.path.join(path, unzipped_folder)
    if not os.path.exists(unzipped_path):
        if not os.path.exists(zip_path):
            logger.info('downloading %s' % url)
            urlretrieve(url, zip_path)

        logger.info('unzipping zip_name')
        zip_ref = zipfile.ZipFile(zip_path, 'r')
        zip_ref.extractall(unzipped_path)
        zip_ref.close()

        logger.info('cleaning')
        os.remove(zip_path)


def download_csv(urls, path):
    for url in urls:
        csv_name = urlsplit(url).path.split('/')[-1]
        csv_path = os.path.join(path, csv_name)
        if not os.path.exists(csv_path):
            logger.info('downloading %s' % csv_name)
            urlretrieve(url, csv_path)


def main():
    """ Downloads data into ../raw.
    """
    download_zip(HORIZON_URL, RAW)
    download_zip(H2020_URL, RAW)
    download_zip(FP7_URL, RAW)
    download_csv(CSV_FILES, RAW)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
