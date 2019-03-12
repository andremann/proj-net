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
NS = {}


def getAttributeOrNone(node, attr):
    if attr in node.attrib.keys():
        return node.attrib[attr]
    else:
        return None


def getElementOrNone(node, tag):
    if node.find(tag, NS) is not None:
        target = node.find(tag, NS).text
        return target.lower().replace('\n', ' ') if target is not None else None
    else:
        None


def getNode(node, tag):
    return node.find(tag, NS)


def parseProjectDetails(root):
    rcn = getElementOrNone(root, './cordis:rcn')
    reference = getElementOrNone(root, './cordis:reference')
    acronym = getElementOrNone(root, './cordis:acronym')
    title = getElementOrNone(root, './cordis:title')
    total_cost = getElementOrNone(root, './cordis:totalCost')
    ec_contribution = getElementOrNone(root, './cordis:ecMaxContribution')
    teaser = getElementOrNone(root, './cordis:teaser')
    objective = getElementOrNone(root, './cordis:objective')
    start = getElementOrNone(root, './cordis:startDate')
    end = getElementOrNone(root, './cordis:endDate')
    status = getElementOrNone(root, './cordis:status')
    return [rcn, reference, acronym, title, total_cost, ec_contribution,
            teaser, objective, start, end, status]


def parseOrganisations(root):
    rcn = getElementOrNone(root, './cordis:rcn')
    organisations = []
    for org in root.findall('.//cordis:organization', NS):
        contribution = getAttributeOrNone(org, 'ecContribution')
        order = getAttributeOrNone(org, 'order')
        org_type = getAttributeOrNone(org, 'type')
        org_id = getElementOrNone(org, './cordis:id')
        short_name = getElementOrNone(org, './cordis:shortName')
        legal_name = getElementOrNone(org, './cordis:legalName')
        address = getNode(org, './cordis:address')
        city = getElementOrNone(address, './cordis:city') if address is not None else None
        country = getElementOrNone(address, './cordis:country') if address is not None else None
        
        organisations.append([rcn, org_id, order, org_type,
                              short_name, legal_name,
                              city, country, contribution])
    return organisations


def extractInformation(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    return (parseProjectDetails(root), parseOrganisations(root))


def download(env_var, path):
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
        os.remove(unzipped_path + '/search-result-metadata.xml')


def process(env_var, input, output):
    url = os.environ.get(env_var)
    zip_name = urlsplit(url).path.split('/')[-1]
    unzipped_folder = zip_name.split('.')[0]
    unzipped_path = os.path.join(input, unzipped_folder)
    organisations_path = os.path.join(output, env_var.lower()[:-4] + '-organisations.csv')
    projects_path = os.path.join(output, env_var.lower()[:-4] + '-projects.csv')
    
    if not os.path.exists(organisations_path) or not os.path.exists(projects_path):
        with open(organisations_path, 'w') as organisation_tsv,\
             open(projects_path, 'w') as project_tsv:
            proj_writer = csv.writer(project_tsv, delimiter='\t',
                                     quotechar='"', quoting=csv.QUOTE_MINIMAL)
            org_writer = csv.writer(organisation_tsv, delimiter='\t',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for xml in os.listdir(unzipped_path):
                xml_path = os.path.join(unzipped_path, xml)
                logger.info(xml_path)
                info = extractInformation(xml_path)
                proj_writer.writerow(info[0])
                org_writer.writerows(info[1])


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True), envvar='RAW')
@click.argument('output_filepath', type=click.Path(exists=True), envvar='PROCESSED')
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    download('H2020_URL', input_filepath)
    download('FP7_URL', input_filepath)
    download('FP6_URL', input_filepath)
    download('FP5_URL', input_filepath)
    download('FP4_URL', input_filepath)
    download('FP3_URL', input_filepath)
    download('FP2_URL', input_filepath)

    process('H2020_URL', input_filepath, output_filepath)
    process('FP7_URL', input_filepath, output_filepath)
    process('FP6_URL', input_filepath, output_filepath)
    process('FP5_URL', input_filepath, output_filepath)
    process('FP4_URL', input_filepath, output_filepath)
    process('FP3_URL', input_filepath, output_filepath)
    process('FP2_URL', input_filepath, output_filepath)


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
