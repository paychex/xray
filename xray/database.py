# pylint: disable=W0703
"""
A class that interacts with data bases directly
"""
# Standard classes
import logging
from time import time
from datetime import datetime

# External Classes
from pymongo import MongoClient
from xray.version import Version


class Mongo():
    """ A Mongo Object is a mongo database connection """

    def __init__(self, connection_string=None):
        if connection_string:
            self.mongo = MongoClient(connection_string).host_inventory

    def check_local(self, host_dict):
        """ Checks local to see if system inventory file exists """
        # TODO: Create a local inventory file and utilize that versus querying
        # database
        try:
            inventory = self.mongo.host_collection.find(
                {'name': host_dict['name']})[0]
            #logging.debug("No local file exists. Utilizing database file for {name}".format(**host_dict))
        except IndexError:
            logging.debug(
                "No record in database. Skipping external inventory check")
            inventory = None

        except Exception as error:
            logging.error(error)

        if inventory:
            logging.debug("Checking for differences local versus inventory")
            host_dict = compare_and_update_dicts(
                database=inventory, local=host_dict)

        return host_dict

    def post(self, temp_dict, start):
        """ Post all data to mongo database
        :input temp_dict - dictionary to post to database
        :input start - start datetime
        """
        host_dict = self.check_local(temp_dict)

        software_bulk = self.mongo.software.initialize_ordered_bulk_op()
        for package in host_dict.get('software', {}):
            # if it is an insert operation write, otherwise
            software_bulk.find({'package_name': package['package_name']}).upsert().update(
                {'$setOnInsert': package})
        software_upsert = software_bulk.execute()
        logging.debug("X-RAY: Software upsert results %s", software_upsert)

        total_runtime = time() - start
        if host_dict['last_update_duration'] == -1:
            host_dict['last_update_duration'] = total_runtime
        logging.debug("Total runtime %s", total_runtime)

        host_dict['last_updated'] = datetime.now().isoformat()

        # Remove and Replace the record
        host_remove = self.mongo.host_collection.remove(
            {'name': host_dict['name']})
        if host_remove.get("ok", 0) == 1:
            self.mongo.host_collection.insert(host_dict)
            logging.debug(host_dict)


def compare_and_update_dicts(database, local):
    """ Compare the local against the database and return merged diff """
    database_list = []
    local_list = []
    for software in database.get('software', {}):
        database_list += [(software['package_name'].encode('utf8',
                                                           'replace'),
                           version['name'],
                           version['install_date']) for version in software['versions']]
    for software in local.get('software', {}):
        local_list += [(software['package_name'], version.get('name', ''),
                        version['install_date']) for version in software['versions']]

    for item in set(database_list).difference(local_list):
        counter = 0
        version = 0
        found = False
        for package in database.get('software', {}):
            if package['package_name'] == item[0].decode('utf8'):
                for software_version in package.get('versions', {}):
                    if software_version['name'] == item[1]:
                        found = True
                        break
                    else:
                        version += 1
                break
            else:
                counter += 1
        if found:
            database['software'][counter]['versions'][version]['removal_date'] = datetime.now(
            ).strftime("%a %d %B %Y %I:%M %p EDT")

    for item in set(local_list).difference(database_list):
        # package has been added
        software_exists = False
        software_counter = 0
        for package in database.get('software', {}):
            if package['package_name'] == item[0]:
                software_exists = True
                version_exists = False
                version_counter = 0
                for version in package.get('versions', {}):
                    if version['name'] == item[1]:
                        database['software'][software_counter]['versions'][version_counter]['removal_date'] = None
                        database['software'][software_counter]['versions'][version_counter]['install_date'] = item[2]
                        version_exists = True
                        break
                    else:
                        version_counter += 1
                if not version_exists:
                    version = Version(item[1], item[2])
                    if package['package_name'].strip(
                    ) is not None and "\\" not in package['package_name']:
                        package['versions'].append(version.__dict__)
                        logging.debug(
                            "X-RAY: New version detected for %s-%s",
                            package['package_name'],
                            version.__dict__)
            else:
                software_counter += 1

        if not software_exists:
            # append the software object
            for software_package in local['software']:
                if software_package['package_name'] == item[0]:
                    database['software'].append(software_package)
                    logging.debug(
                        "X-RAY: New Package detected: %s",
                        software_package)

    try:
        # if not mounts provided, just ignore
        database['mounts'] = local['mounts']
    except Exception:
        pass

    database['last_update_duration'] = local.get(
        'last_update_duration', datetime.now().isoformat())
    return database
