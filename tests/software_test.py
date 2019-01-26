from unittest import TestCase
from xray.software import Software, check_sofware_if_exists, analyze_packages

class SoftwareTestCase(TestCase):
    def test_software_class(self):
        package_name = "test"
        package_names = ["foo", "test"]
        software = Software(package_name)
        package = check_sofware_if_exists(
            package_name, package_names, [software])
        self.assertTrue(package == software)

        package_names = ["Foo", "bar"]
        package = check_sofware_if_exists(
            package_name, package_names, [software])
        self.assertTrue(package is None)

    def test_analyze_software(self):
        software = '{"name":"nfs-utils","version":"1.3.0","install_date":"Tue 03 Jul 2018 09:28:11 AM EDT","vendor":"CentOS"}'
        software += ',{"name":"libcmis","version":"0.5.1","install_date":"Thu 28 Jun 2018 12:42:39 PM EDT","vendor":"CentOS"}'
        packages = analyze_packages(software)
        self.assertTrue(packages[0]['package_name'] == 'libcmis')
        self.assertTrue(packages[1]['package_name'] == 'nfs-utils')

    def test_analyze_software_with_parentheses(self):
        software_both = '({"name":"nfs-utils","version":"1.3.0","install_date":"Tue 03 Jul 2018 09:28:11 AM EDT","vendor":"CentOS"})'
        software_front = '({"name":"nfs-utils","version":"1.3.0","install_date":"Tue 03 Jul 2018 09:28:11 AM EDT","vendor":"CentOS"}'
        software_back = '{"name":"nfs-utils","version":"1.3.0","install_date":"Tue 03 Jul 2018 09:28:11 AM EDT","vendor":"CentOS"})'
        packages = analyze_packages(software_both)
        self.assertTrue(packages[0]['package_name'] == 'nfs-utils')
        packages = analyze_packages(software_front)
        self.assertTrue(packages[0]['package_name'] == 'nfs-utils')
        packages = analyze_packages(software_back)
        self.assertTrue(packages[0]['package_name'] == 'nfs-utils')
    
    def test_analyze_version_none(self):
        software_both = '({"name":"nfs-utils","install_date":"Tue 03 Jul 2018 09:28:11 AM EDT","vendor":"CentOS"})'
        packages = analyze_packages(software_both)
        self.assertFalse(packages[0]['versions'][0]['name'])