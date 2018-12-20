from unittest import TestCase
from xray.mount import Mount, analyze_mounts


class MountsTestCase(TestCase):
    def test_mount_class(self):
        filesystem = "/dev"
        mount = Mount(filesystem)
        self.assertTrue(mount.filesystem == filesystem)

    def test_analyze_mounts(self):
        mount_import = "Filesystem,Size,Used,Avail,Use%,Mounted,on;/dev/mapper/vg00-root,9.8G,58M,9.7G,1%,/;devtmpfs,3.9G,0,3.9G,0%,/dev;"
        results = analyze_mounts(mount_import)
        self.assertTrue(results[0]['used'] == '58M')
        self.assertTrue(results[0]['use_percentage'] == '1%')
        self.assertTrue(results[0]['filesystem'] == '/dev/mapper/vg00-root')
        self.assertTrue(results[0]['mounted'] == '/')
        self.assertTrue(results[1]['avail'] == '3.9G')
        self.assertTrue(results[1]['filesystem'] == 'devtmpfs')
