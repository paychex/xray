# pylint: disable=C0411,C0111,W0102


from xray.version import Version
from xray.software import Software
from xray.database import compare_and_update_dicts
from requests import get, put, post, RequestException
from dateutil.parser import parse
from pytz import timezone
import logging

from os import environ
from time import time
from json import dumps
from getpass import getuser, getpass
from multiprocessing.pool import Pool
from urllib.parse import quote
from urllib3 import disable_warnings, exceptions
disable_warnings(exceptions.InsecureRequestWarning)


class Api():
    def __init__(self, endpoint, host_dict={}, start: time = time()):
        self.host_dict = host_dict
        self.endpoint = endpoint
        self.start = start
        if self.host_dict.get('name'):
            self.hostname = self.host_dict['name'].split(".")[0]
            # pylint: disable=invalid-name
            self.id = self.__get_vm_id(
                endpoint=f"{endpoint}/virtualmachine?name={self.hostname}")
            logging.debug("VM ID %s", self.id)
            self.database = self.__get_api_software()
            try:
                data = {"software": self.transform_from_api(self.database)}
                self.software = compare_and_update_dicts(
                    database=data, local=host_dict)
                self.software = self.transform_to_api(
                    self.software['software'],
                    f"{self.endpoint}/virtualmachine?name={self.hostname}")
            # pylint: disable=W0703
            except Exception as exc:
                logging.error(exc)
                self.software = []

    @staticmethod
    def __get_vm_id(endpoint):
        req = get(endpoint, verify=False)
        req.raise_for_status()

        response = req.json()
        if response.get('count', 0):
            return int((response['results'][0]['url']).split("/")[-2])

        raise Exception("Host not found")

    def __get_api_software(self, url=None, software: [any] = []):
        if not url:
            url = f"{self.endpoint}/software?vm={self.id}"
        results = get(url, verify=False).json()

        if int(results.get("count", 0)) == 0:
            return software

        temp_software = software + results['results']
        if results.get('next'):
            return self.__get_api_software(
                software=temp_software, url=results['next'])

        return temp_software

    def __get_diff(self):
        local_list = [
            (software['name'],
             software['vendor'],
             software['version'],
             software['install_date'],
             software['removal_date']) for software in self.software]
        database_list = [
            (software['name'],
             software['vendor'],
             software['version'],
             software['install_date'],
             software['removal_date']) for software in self.database]
        return [{
            "name": item[0],
            "vendor": item[1],
            "version": item[2],
            "install_date": item[3] if len(item) > 3 else None,
            "removal_date": item[4] if len(item) > 4 else None
        } for item in set(local_list).difference(database_list)]

    @staticmethod
    def __get_creds():
        username = environ['username'] if environ.get(
            'username') else getuser()
        password = environ['password'] if environ.get(
            'password') else getpass()
        return (username, password)

    def _update(self, segment: any):
        headers = {'content-type': 'application/json'}
        segment['vm'] = f"{self.endpoint}/virtualmachine/{self.id}/"

        # First attempt to see if record exists
        temp_name = quote(segment.get('name'))
        url = f"{self.endpoint}/software?name={temp_name}&version={segment['version']}&vm={self.id}"
        logging.debug("Getting software id from url %s", url)
        request = get(url, verify=False).json()

        # If record does not exists POST
        if not request['count']:
            endpoint = (f"{self.endpoint}/software/")
            logging.debug("POST %s - %s", endpoint, dumps(segment))
            response = post(url=endpoint,
                            headers=headers,
                            data=dumps(segment),
                            verify=False,
                            auth=self.__get_creds())
            try:
                response.raise_for_status()
                logging.debug("Response from API %s", response.json())
                return response.json()
            except RequestException as exc:
                logging.error("Error Posting %s", exc)
        else:
            local_tz = timezone('EST')
            install_local = parse(
                segment['install_date']).astimezone(local_tz) if segment.get(
                    'install_date', None) else None
            install_remote = parse(
                request['results'][0]['install_date']).astimezone(local_tz) if request['results'][0].get(
                    'install_date', None) else None
            remove_local = parse(
                segment['removal_date']).astimezone(local_tz) if segment.get(
                    'removal_date', None) else None
            remove_remote = parse(
                request['results'][0]['removal_date']).astimezone(local_tz) if request['results'][0].get(
                    'removal_date', None) else None

            install_same = False
            if install_local and install_remote:
                diff = abs((install_local - install_remote).total_seconds() / 60)
                if diff < 30:
                    install_same = True
            else:
                if install_local == install_remote:
                    install_same = True
            if install_same:
                if remove_local and remove_remote:
                    diff = abs((remove_local - remove_remote).total_seconds() / 60)
                    if diff < 30:
                        return None
                else:
                    if remove_local == remove_remote:
                        return None

            software_url = request['results'][0]['url']
            software_id = int(software_url.split("/")[-2])
            endpoint = f"{self.endpoint}/software/{software_id}/"
            logging.debug("PUT %s - %s", endpoint, segment)
            response = put(url=endpoint,
                           data=dumps(segment),
                           verify=False,
                           headers=headers,
                           auth=self.__get_creds())
            try:
                response.raise_for_status()
                logging.debug("Response from API %s", response.json())
                return response.json()
            except RequestException as exc:
                logging.error("Error putting %s", exc)
            return None

    def upsert(self):
        body = self.__get_diff()
        pool = Pool(50)
        results = [result for result in pool.map(self._update, body) if result]
        logging.debug("Total runtime %s", time() - self.start)
        return results

    @staticmethod
    def transform_to_api(softwares: [any] = [], url=None) -> [any]:
        transformed = []
        for software in softwares:
            for version in software['versions']:
                temp_transform = {
                    "name": software['package_name'],
                    "vendor": software.get(
                        'software_vendor',
                        software.get('vendor')),
                    "version": version.get(
                        'name',
                        "-1"),
                    "install_date": parse(
                        version['install_date']).isoformat(),
                    "removal_date": parse(
                        version['removal_date']).isoformat() if version.get(
                            'removal_date',
                            None) else None,
                    "vm": url}
                transformed.append(temp_transform)
        return transformed

    @staticmethod
    def transform_from_api(softwares: [any] = []) -> [any]:
        transformed = []
        for software in softwares:
            temp_version = Version(
                software['version'],
                software['install_date']).__dict__
            package_exists = False
            # pylint: disable=C0200
            for i in range(len(transformed)):
                package = transformed[i]
                if software['name'] == package['package_name']:
                    package['versions'].append(temp_version)
                    package_exists = True
                    transformed[i] = package
            if not package_exists:
                temp_software = Software(software['name'], software['vendor'])
                temp_software.versions.append(temp_version)
                transformed.append(temp_software.__dict__)
        return transformed
