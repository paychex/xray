# pylint: disable=import-error,line-too-long,relative-import,logging-format-interpolation,too-many-function-args
import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "classes"))
import json
from datetime import datetime
import dateutil.parser
from mount import Mount, analyze_mounts
from host import Host
from software import Software, check_sofware_if_exists, analyze_packages
from database import compare_and_update_dicts
from version import Version

class TestCase(unittest.TestCase):

    def test_mount_class(self):
        filesystem = "/dev"
        mount = Mount(filesystem)
        self.assertTrue(mount.filesystem == filesystem)

    def test_analyze_mounts(self):
        mount_import  = "Filesystem,Size,Used,Avail,Use%,Mounted,on;/dev/mapper/vg00-root,9.8G,58M,9.7G,1%,/;devtmpfs,3.9G,0,3.9G,0%,/dev;"
        results = analyze_mounts(mount_import)
        self.assertTrue(results[0]['used'] == '58M')
        self.assertTrue(results[0]['use_percentage'] == '1%')
        self.assertTrue(results[0]['filesystem'] == '/dev/mapper/vg00-root')
        self.assertTrue(results[0]['mounted'] == '/')
        self.assertTrue(results[1]['avail'] == '3.9G')
        self.assertTrue(results[1]['filesystem'] == 'devtmpfs')

class HostTestCase(unittest.TestCase):
    def test_host_class(self):
        host_name = "hostname"
        host = Host(host_name)
        self.assertTrue(host.name == host_name)
        self.assertTrue( dateutil.parser.parse(host.last_updated).day == datetime.today().day)
        self.assertTrue(len(host.software) ==  0)

class SoftwareTestCase(unittest.TestCase):
    def test_software_class(self):
        package_name = "test"
        package_names = ["foo", "test"]
        software = Software(package_name)
        package = check_sofware_if_exists(package_name, package_names, [ software ] )
        self.assertTrue(package == software)

        package_names = ["Foo", "bar"]
        package = check_sofware_if_exists(package_name, package_names, [ software ] )
        self.assertTrue(package == None)

    def test_analyze_software(self):
        software = '{"name":"nfs-utils","version":"1.3.0","install_time":"Tue 03 Jul 2018 09:28:11 AM EDT","vendor":"CentOS"}'
        software += ',{"name":"libcmis","version":"0.5.1","install_time":"Thu 28 Jun 2018 12:42:39 PM EDT","vendor":"CentOS"}'
        packages = analyze_packages(software)
        self.assertTrue(packages[0]['package_name'] == 'libcmis')
        self.assertTrue(packages[1]['package_name'] == 'nfs-utils')

    def test_analyze_software_with_parentheses(self):
        software_both = '({"name":"nfs-utils","version":"1.3.0","install_time":"Tue 03 Jul 2018 09:28:11 AM EDT","vendor":"CentOS"})'
        software_front = '({"name":"nfs-utils","version":"1.3.0","install_time":"Tue 03 Jul 2018 09:28:11 AM EDT","vendor":"CentOS"}'
        software_back = '{"name":"nfs-utils","version":"1.3.0","install_time":"Tue 03 Jul 2018 09:28:11 AM EDT","vendor":"CentOS"})'
        packages = analyze_packages(software_both)
        self.assertTrue(packages[0]['package_name'] == 'nfs-utils')
        packages = analyze_packages(software_front)
        self.assertTrue(packages[0]['package_name'] == 'nfs-utils')
        packages = analyze_packages(software_back)
        self.assertTrue(packages[0]['package_name'] == 'nfs-utils')

class DatabaseTestCase(unittest.TestCase):
    def test_version_add(self):
        package_name = "sample package"
        package = Software(package_name)
        version = Version( "1.0",  datetime.now().isoformat() )
        package.add_versions( version )

        software_item = [ package.__dict__ ]
        software = { "software": software_item, "mounts": []  }
        empty =  { "software": [], "mounts": [] }
        result = compare_and_update_dicts(empty, software)
        self.assertTrue(result['software'][0]['package_name'] == package_name)
        self.assertTrue(result['software'][0]['versions'][0]['name'] == "1.0")

    def test_version_removal(self):
        package_name = "sample package"
        package = Software(package_name)
        version = Version( "1.0",  datetime.now().isoformat() )
        package.add_versions( version )

        software_item = [ package.__dict__ ]
        software = { "software": software_item, "mounts": []  }
        empty =  { "software": [], "mounts": [] }
        result = compare_and_update_dicts(software, empty)
        self.assertTrue(result['software'][0]['package_name'] == package_name)
        self.assertTrue(result['software'][0]['versions'][0].get('removal_date', None) != None)

    def test_version_upgrade(self):
        package_name = "sample package"
        package = Software(package_name)
        version = Version( "1.0",  datetime.now().isoformat() )
        package.add_versions( version )

        software_item = [ package.__dict__ ]
        software = { "software": software_item, "mounts": []  }

        package2 = Software(package_name)
        version = Version( "2.0",  datetime.now().isoformat() )
        package2.add_versions( version )
        software_item2 = [ package2.__dict__ ]

        second_software =  { "software": software_item2, "mounts": [] }
        result = compare_and_update_dicts(software, second_software)
        self.assertTrue(result['software'][0]['package_name'] == package_name)
        self.assertTrue(result['software'][0]['versions'][0].get('removal_date', None) != None)
        self.assertTrue(result['software'][0]['versions'][1]['name'] == '2.0')

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule( sys.modules[__name__] )
    ret = not unittest.TextTestRunner(verbosity=3).run( suite ).wasSuccessful()
    sys.exit(ret)