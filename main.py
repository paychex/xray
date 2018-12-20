# pylint: disable=import-error
"""
    :contributors:
        - Daniel Quackenbush
"""
from os import environ
from sys import stdout
import logging
import json
import socket
import time
from random import randint
import argparse

from datetime import datetime

# Independent Classes
from xray.host import Host
from xray.software import get_local_packages, analyze_packages
from xray.version import Version
from xray.mount import get_local_mounts, analyze_mounts
from xray.database import Mongo
from xray.api import Api

def main(results: any):
    """ The main function to take in all arguments, analyze, and post to mongo """
    if results.debug:
        logging.basicConfig(
            stream=stdout,
            format=' %(levelname)s: %(asctime)s %(message)s',
            level=logging.NOTSET)
    else:
        logging.basicConfig(
            stream=stdout,
            format='%(levelname)s: %(asctime)s %(message)s',
            level=logging.INFO)

    if results.sleep:
        logging.debug("Taking a light nap as requested")
        time.sleep(randint(0, 60))
        logging.debug("Starting Execution")

    start = time.time()
    try:
        with open(results.packages, 'r') as file_resource:
            packages = file_resource.read()
        try:
            host = Host(results.server)
        except BaseException:
            raise ValueError(
                "X-RAY: Packages were provided without hostname. Please use the -s flag and provide a hostname")
    except ValueError as error:
        raise error
    except BaseException:
        # Assume if they are running locally they dont provide packages
        host = Host(socket.getfqdn())
        packages = get_local_packages()

    try:
        with open(results.mounts, 'r') as file_resource:
            mounts = file_resource.read()
    except BaseException:
        # Assume if they are running locally they dont provide mounts
        mounts = get_local_mounts()

    if results.runtime:
        host.last_update_duration = float(results.runtime)

    host.software = analyze_packages(packages)
    if mounts is not None:
        host.mounts = analyze_mounts(mounts)

    if not results.test:
        try:
            if environ.get('XRAY_CONNECTION_STRING'):
                mongo = Mongo(environ['CONNECTION_STRING'])
                mongo.post(host.__dict__, start)
            elif environ.get('XRAY_ENDPOINT'):
                api = Api(endpoint=environ['XRAY_ENDPOINT'], host_dict=host.__dict__, start = start)
                results = api.upsert()
                logging.info("Total changes upserted %s", len(results))
            else:
                raise ValueError("Must specify XRAY_ENDPOINT or XRAY_CONNECTION_STRING in envioronment variable")
            exit(0)
        except ValueError as error:
            raise error
        except Exception as error:
            logging.error(f"X-RAY:Error with db: {error}")
            exit(1)
    else:
        logging.info(host.__dict__)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='A module to parse and record host pacakges to a datstore (MongoDB or Rest API)')
    parser.add_argument(
        '-p',
        '--packages',
        action="store",
        help='host packages file',
        type=str)
    parser.add_argument(
        '-s',
        '--server',
        action='store',
        help='server hostname',
        type=str)
    parser.add_argument(
        '-m',
        '--mounts',
        action='store',
        help='mount points file',
        type=str)
    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        default=False,
        help='Debug output')
    parser.add_argument(
        '-r',
        '--runtime',
        action='store',
        default=False,
        help='Run time of the script from end to end')
    parser.add_argument(
        '-t',
        '--test',
        action='store_true',
        default=False,
        help='Test host capture without pointing to db')
    parser.add_argument(
        '--sleep',
        action='store_true',
        default=False,
        help='Sleep a random time')
    main(parser.parse_args())
