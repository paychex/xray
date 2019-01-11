# pylint: disable=R0903,C1801,W0703
"""
    A file to manage the capturing and storing of mounts
"""
from sys import platform
from subprocess import Popen, PIPE
import json
import logging


class Mount():
    """  A mount object is a system mount on an individual OS """

    def __init__(self, filesystem=None):
        self.filesystem = filesystem
        self.use_percentage = None
        self.used = None
        self.avail = None
        self.mounted = None
        self.size = None


def get_local_mounts():
    """ Gets the local mounts of a given windows or linux system """
    output = ""
    if platform.lower() == "linux" or platform.lower() == "linux2":
        # bash output eqivalent of:
        # df -hP | sed ':a;N;$!ba;s/\n/;/g' | sed 's/ \{1,\}/,/g' | sed -e "s/
        # /,/g"
        p_open = Popen(['df', '-hP'], stdout=PIPE,
                       stderr=PIPE, encoding='utf-8')
        temp_output, error = p_open.communicate()
        for line in temp_output.split("\n"):
            temp_str = ""
            for item in line.split(" "):
                if item:
                    temp_str += item + ","
            output += temp_str[:-1] + ";"
    elif platform.lower() == "win32":

        # Local Mounts
        command = [
            'C:\\WINDOWS\\system32\\WindowsPowerShell\\v1.0\\powershell.exe',
            '-ExecutionPolicy',
            'Unrestricted',
            'Get-WmiObject',
            'Win32_Volume',
            '|',
            'ConvertTo-Json']
        p_open = Popen(command, stdout=PIPE, stderr=PIPE, encoding='utf-8')
        temp_output, error = p_open.communicate()
        if len(error) > 0:
            logging.error("X-RAY Local Mount Error: %s", error)
        else:
            if len(temp_output) > 0:
                temp_json = json.loads(temp_output)
                for drive in temp_json:
                    try:
                        used = int(drive['Capacity']) - int(drive['FreeSpace'])
                        percent = (used / float(drive['Capacity'])) * 100
                        percentage_used = "{:.2f}%".format(percent)
                    except BaseException:
                        used = "None"
                        percentage_used = "None"
                    try:
                        temp_str = "{Label},{Capacity},{used},{FreeSpace},{percentage_used},{Name};".format(
                            used=used, percentage_used=percentage_used, **drive)
                        output += temp_str
                    except Exception as error:
                        logging.error(error)

        # NAS Shares
        command = [
            'C:\\WINDOWS\\system32\\WindowsPowerShell\\v1.0\\powershell.exe',
            '-ExecutionPolicy',
            'Unrestricted',
            'Get-WmiObject',
            'Win32_MappedLogicalDisk',
            '|',
            'ConvertTo-Json']
        p_open = Popen(command, stdout=PIPE, stderr=PIPE, encoding='utf-8')
        temp_output, error = p_open.communicate()
        if len(error) > 0:
            logging.error("X-RAY NAS Mount Error: %s", error)
        else:
            if len(temp_output) > 0:
                temp_json = json.loads(temp_output)
                for drive in temp_json:
                    try:
                        used = int(drive['Size']) - int(drive['FreeSpace'])
                        percent = (used / float(drive['Size'])) * 100
                        percentage_used = "{:.2f}%".format(percent)
                    except BaseException:
                        used = "None"
                        percentage_used = "None"
                    try:
                        temp_str = "{VolumeName},{Size},{used},{FreeSpace},{percentage_used},{ProviderName};".format(
                            used=used, percentage_used=percentage_used, **drive)
                        output += temp_str
                    except Exception as error:
                        logging.error(error)

    return output[:-1]


def analyze_mounts(output):
    """ Converts the mount string provided into a mounts object
    :input output - mounts string
    :return mounts - mounts json object
    """
    mounts = []
    for mount in output.split(";")[1:]:
        try:
            point = mount.split(",")
            mount = Mount(point[0])
            if point[1] and point[1].strip() != "None":
                mount.size = point[1].strip()
            if point[2] and point[2].strip() != "None":
                mount.used = point[2].strip()
            if point[3] and point[3].strip() != "None":
                mount.avail = point[3].strip()
            if point[4] and point[4].strip() != "None":
                mount.use_percentage = point[4].strip()
            if point[5] and point[5].strip() != "None":
                mount.mounted = point[5].strip()
            mounts.append(mount.__dict__)
        except IndexError:
            # When it reaches the end it becomes out of index
            pass
        except Exception as error:
            logging.error(error)
    return mounts
