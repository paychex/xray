from unittest import TestCase
from datetime import datetime
from xray.database import compare_and_update_dicts
from xray.software import Software
from xray.version import Version

class DatabaseTestCase(TestCase):
    def test_version_add(self):
        package_name = "sample package"
        package = Software(package_name)
        version = Version("1.0", datetime.now().isoformat())
        package.add_versions(version)

        software_item = [package.__dict__]
        software = {"software": software_item, "mounts": []}
        empty = {"software": [], "mounts": []}
        result = compare_and_update_dicts(empty, software)
        self.assertTrue(result['software'][0]['package_name'] == package_name)
        self.assertTrue(result['software'][0]['versions'][0]['name'] == "1.0")

    def test_version_removal(self):
        package_name = "sample package"
        package = Software(package_name)
        version = Version("1.0", datetime.now().isoformat())
        package.add_versions(version)

        software_item = [package.__dict__]
        software = {"software": software_item, "mounts": []}
        empty = {"software": [], "mounts": []}
        result = compare_and_update_dicts(software, empty)
        self.assertTrue(result['software'][0]['package_name'] == package_name)
        self.assertTrue(
            result['software'][0]['versions'][0].get(
                'removal_date', None) is not None)

    def test_version_upgrade(self):
        package_name = "sample package"
        package = Software(package_name)
        version = Version("1.0", datetime.now().isoformat())
        package.add_versions(version)

        software_item = [package.__dict__]
        software = {"software": software_item, "mounts": []}

        package2 = Software(package_name)
        version = Version("2.0", datetime.now().isoformat())
        package2.add_versions(version)
        software_item2 = [package2.__dict__]

        second_software = {"software": software_item2, "mounts": []}
        result = compare_and_update_dicts(software, second_software)
        self.assertTrue(result['software'][0]['package_name'] == package_name)
        self.assertTrue(
            result['software'][0]['versions'][0].get(
                'removal_date', None) is not None)
        self.assertEqual(result['software'][0]['versions'][1]['name'], '2.0')
