# pylint: disable=import-error
"""
    :contributors:
        - Daniel Quackenbush
"""
import os
import logging
import json
import socket
import time
from random import randint
import argparse

from datetime import datetime
from sys import stdout, path
path.append(os.path.join(os.path.dirname(__file__), "classes"))
path.append(os.path.join(os.path.dirname(__file__), "lib"))

# Independent Classes
from host import Host
from software import get_local_packages, analyze_packages
from version import Version
from mount import get_local_mounts, analyze_mounts
from database import Mongo


def main():
    """ The main function to take in all arguments, analyze, and post to mongo """
    parser = argparse.ArgumentParser(
        description='A module to parse and record host pacakges to MongoDB')
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
        help='Run time of ansible execution')
    parser.add_argument(
        '-t',
        '--test',
        action='store_true',
        default=False,
        help='Test host capture without pointing to db')
    parser.add_argument(
        '--prod',
        action='store_true',
        default=False,
        help='Write to prod db')
    parser.add_argument(
        '--sleep',
        action='store_true',
        default=False,
        help='Sleep a random time')
    results = parser.parse_args()

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
        if results.prod:
            import mongo_info_prod
            connection = mongo_info_prod.CONNECTION_STRING
        else:
            import mongo_info_nonprod
            connection = mongo_info_nonprod.CONNECTION_STRING
        try:
            mongo = Mongo(connection)
            mongo.post(host.__dict__, start)
            exit(0)
        except Exception as error:
            logging.error(f"X-RAY:Error with db: {error}")
            exit(1)
    else:
        logging.debug(host.__dict__)


if __name__ == "__main__":
    main()
