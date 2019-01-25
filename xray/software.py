# pylint: disable=R0903,C1801,W0703,unused-import
"""
        A file to manage the capturing and storing of software
"""
import json
import logging
from sys import platform
from subprocess import Popen, PIPE
from dateutil import parser

# External Classes
from xray.version import Version


class Software():
    """ A software object contains version, software name, and vendor """

    def __init__(self, package_name, vendor=None):
        self.package_name = package_name
        self.software_vendor = vendor
        self.versions = []

    def add_versions(self, version):
        """ A function to add version to the software """
        self.versions.append(version.__dict__)


def check_sofware_if_exists(package_name, package_names, packages):
    """ A function to check if the package exists already in the json
    :returns none if doesn't exist
    :returns package already defined if exists
    """
    # If we already have the package
    if package_name in package_names:
        for temp_package in packages:
            if temp_package.package_name == package_name:
                return temp_package
    return None


def get_local_packages():
    """ A function to get Packages locally from a machine - Linux or Windows"""
    packages = []
    package_names = []

    if platform.lower() == "linux" or platform.lower() == "linux2":
        query = r'\{"name":"%{NAME}","version":"%{VERSION}","install_date":"%{installtime:date}","vendor":"%{VENDOR}"\},'
        command = f"rpm -qa --qf '{query}'"
        command = command.split()
        p_open = Popen(command, stdout=PIPE, stderr=PIPE, encoding="utf8")
        output, _ = p_open.communicate()
        return output[:-1]

    if platform.lower() == "win32":
        import traceback
        import io
        import wmi
        import winreg

        def get_keys(h_key, s_sub_key):
            """ A function to read registry keys
            :input HKEY_LOCAL_MACHINE
            :input: subKeyCLSID
            """
            with winreg.OpenKey(h_key, s_sub_key, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
                idx = 0
                while True:
                    try:
                        yield winreg.EnumKey(key, idx)
                    except BaseException:
                        # No more indices
                        break
                    idx += 1

        def get_packages(s_sub_key, packages=""):
            """ A function to get locally from registry """
            h_key = winreg.HKEY_LOCAL_MACHINE
            for key_name in get_keys(h_key, s_sub_key):
                with winreg.OpenKey(h_key, "\\".join([s_sub_key, key_name]), 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
                    i = 0
                    temp_package = {}
                    while True:
                        try:
                            name, val, key_type = winreg.EnumValue(key, i)
                            if name == "DisplayName":
                                temp_package['name'] = val
                            elif name == "Publisher":
                                temp_package['vendor'] = val
                            elif name == "InstallDate":
                                temp_package['install_date'] = val
                            elif name == "DisplayVersion":
                                temp_package['version'] = val
                        except BaseException:
                            break
                        i += 1
                    if len(temp_package.keys()) > 1:
                        temp_output = json.dumps(temp_package)
                        packages += f"{temp_output},"
            return packages

        packages = get_packages(
            "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\")
        packages = get_packages(
            "SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\",
            packages)
        return packages[:-1]

    raise Exception(
        f"Script is meant for linux and Windows exclusivly and you are running {platform}")


def analyze_packages(output):
    """ a function to analyze the json result of the software capture
    :input output - output of JSON string capture
    """
    # Some initial etl to catch any ansible issues
    output = "".join(output.split("''"))

    output = output.replace("'", "\"")
    if output[0] == "(":
        output = output[1:]
    if output[-1:] == ")":
        output = output[:-1]
    output = output.replace("\\", "")

    packages = []
    package_names = []

    # When run throught the subprocess rpm qa it added " to the string. Remove
    # those quotes if it fails
    try:
        results = json.loads(f"[{output}]")
    except BaseException:
        results = json.loads(f"[{output[1:-1]}]")
    try:
        for package in results:
            package_name = package.get('name', None)
            if package_name is not None and package_name.strip(
            ).lower() != "none" and "\\" not in package_name:
                if not package.get('install_date').strip():
                    package['install_date'] = '19700101'
                if not package.get('version', '').strip():
                    package['version'] = None
                if not package.get('vendor', '').strip():
                    package['vendor'] = 'n/a'

                software = Software(package_name, package.get('vendor'))

                version = Version(
                    package.get('version'),
                    package.get('install_date')
                )
                temp_software = check_sofware_if_exists(
                    package_name, package_names, packages)
                if temp_software is not None:
                    software = temp_software

                software.add_versions(version)
                packages.append(software.__dict__)
                package_names.append(packages)
    except Exception as error:
        logging.error(error)
    return sorted(packages, key=lambda k: k['package_name'])
