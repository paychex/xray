from unittest import TestCase
from datetime import datetime
import dateutil.parser
from xray.host import Host


class HostTestCase(TestCase):
    def test_host_class(self):
        host_name = "hostname"
        host = Host(host_name)
        self.assertTrue(host.name == host_name)
        self.assertTrue(
            dateutil.parser.parse(
                host.last_updated).day == datetime.today().day)
        self.assertTrue(len(host.software) == 0)
