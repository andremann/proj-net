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


def download_zip(env_var, path):
    url = os.environ.get(env_var)
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


def download_csv(env_var, path):
    urls = os.environ.get(env_var)
    for url in urls.split(','):
        csv_name = urlsplit(url).path.split('/')[-1]
        csv_path = os.path.join(path, csv_name)
        if not os.path.exists(csv_path):
            logger.info('downloading %s' % csv_name)
            urlretrieve(url, csv_path)


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True), envvar='RAW')
def main(input_filepath):
    """ Downloads data into ../raw.
    """
    download_zip('HORIZON_URL', input_filepath)
    download_zip('H2020_URL', input_filepath)
    download_zip('FP7_URL', input_filepath)
    download_csv('CSV_FILES', input_filepath)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    NS = json.loads(os.environ.get('NAMESPACES'))
    main()
