from unittest import TestCase
from json import loads
from datetime import datetime
from responses import add, add_callback, activate, GET, PUT, POST
from mock import patch
from xray.api import Api


class APITestCase(TestCase):
    def test_transform_from_api(self):
        api = Api(endpoint="")
        api_dict = [{
            "url": "http://127.0.0.1/api/v1/software/4/",
            "name": "Test Software",
            "vendor": "Paychex",
            "version": "70",
            "install_date": "2018-12-14T00:00:00Z",
            "removal_date": None,
        }]
        initial_transform = api.transform_from_api(api_dict)
        self.assertEqual(initial_transform[0]['package_name'], 'Test Software')

    def test_transform_from_api_multiple_versions(self):
        api = Api(endpoint="")
        api_dict = [{
            "url": "http://127.0.0.1/api/v1/software/4/",
            "name": "Test Software",
            "vendor": "Paychex",
            "version": "70",
            "install_date": "2018-12-14T00:00:00Z",
            "removal_date": None,
        }, {
            "url": "http://127.0.0.1/api/v1/software/4/",
            "name": "Test Software",
            "vendor": "Paychex",
            "version": "71",
            "install_date": "2018-12-14T00:00:00Z",
            "removal_date": None,
        }]
        second_transform = api.transform_from_api(api_dict)
        self.assertEqual(len(second_transform[0]['versions']), 2)

    def test_transform_from_api_multiple_software(self):
        api = Api(endpoint="")
        api_dict = [{
            "url": "http://127.0.0.1/api/v1/api/software/4/",
            "name": "Test Software",
            "vendor": "Paychex",
            "version": "70",
            "install_date": "2018-12-14T00:00:00Z",
            "removal_date": None,
        }, {
            "url": "http://127.0.0.1/api/v1/software/4/",
            "name": "Another Software",
            "vendor": "Paychex",
            "version": "71",
            "install_date": "2018-12-14T00:00:00Z",
            "removal_date": None,
        }]
        transform = api.transform_from_api(api_dict)
        self.assertEqual(len(transform), 2)

    def test_transform_to_api(self):
        api_dict = [{
            'package_name': 'Test Software',
            'software_vendor': 'Paychex',
            'versions': [{
                'name': '70',
                'install_date': '2018-12-14T00:00:00Z'
            }]
        }]
        api = Api(
            endpoint="http://127.0.0.1/api/v1/api/")
        transform = api.transform_to_api(api_dict)
        self.assertEqual(transform[0]['name'], 'Test Software')

    @activate
    @patch.dict('os.environ', {'username': 'fake', 'password': 'pass'})
    def test_add_when_host_has_software(self):
        add(GET, 'http://127.0.0.1/api/v1/virtualmachine?name=test',
            json={'count': 1, 'results': [{
                "url": "https:///127.0.0.1/api/v1/virtualmachine/4/"
            }]}, status=200)
        add(GET, 'http://127.0.0.1/api/v1/software?vm=4',
            json={'count': 1, 'results': [{
                "url": "http://127.0.0.1/api/v1//software/4/",
                "name": "Test Software",
                "vendor": "Paychex",
                "version": "70",
                "install_date": "2018-12-14T00:00:00Z",
                "removal_date": None,
            }]}, status=200)

        add(GET, "http://127.0.0.1/api/v1/software?name=Test%20Software&version=70&vm=4&vendor=Paychex",
            json={'count': 1, 'results': [{
                "url": "http://127.0.0.1/api/v1//software/4/",
                "name": "Test Software",
                "vendor": "Paychex",
                "version": "70",
                "install_date": "2018-12-14T00:00:00Z",
                "removal_date": None,
            }]}, status=200)

        add(GET, "http://127.0.0.1/api/v1/software?name=Another%20Software&version=&vm=4&vendor=Paychex",
            json={'count': 0, 'results': [{}]}, status=200)

        def request_callback(request):
            return (200, {}, request.body)

        add_callback(
            POST, 'http://127.0.0.1/api/v1/software/',
            callback=request_callback,
            content_type='application/json',
        )

        add_callback(
            PUT, 'http://127.0.0.1/api/v1/software/4/',
            callback=request_callback,
            content_type='application/json',
        )

        api = Api(endpoint="http://127.0.0.1/api/v1", host_dict={
            "name": "test",
            "software": [
                {
                    "package_name": "Test Software",
                    "software_vendor": "Paychex",
                    "versions": [
                        {
                            "name": "70",
                            "install_date": "2018-12-14T00:00:00Z",
                            "removal_date": None,
                        }
                    ]
                },
                {
                    "package_name": "Another Software",
                    "software_vendor": "Paychex",
                    "versions": [
                        {
                            "install_date": "2018-12-14T00:00:00Z",
                            "removal_date": "2018-12-14T00:00:00Z"
                        }
                    ]
                },
            ]
        }).upsert()
        self.assertEqual(api[0]['removal_date'], '2018-12-14T00:00:00+00:00')

    @activate
    @patch.dict('os.environ', {'username': 'fake', 'password': 'pass'})
    def test_add_when_host_has_no_software(self):
        add(GET, 'http://127.0.0.1/api/v1/virtualmachine?name=test',
            json={'count': 1, 'results': [{
                "url": "https:///127.0.0.1/api/v1/virtualmachine/4/"
            }]}, status=200)
        add(GET, 'http://127.0.0.1/api/v1/software?vm=4',
            json={'count': 1, 'results': [{
                "url": "http://127.0.0.1/api/v1/software/4/",
                "name": "Test Software",
                "vendor": "Paychex",
                "version": "70",
                "install_date": "2018-12-14T00:00:00Z",
                "removal_date": None,
            }]}, status=200)

        add(GET, "http://127.0.0.1/api/v1/software?name=Test%20Software&version=70&vm=4&vendor=Paychex",
            json={'count': 1, 'results': [{
                "url": "http://127.0.0.1/api/v1//software/4/",
                "name": "Test Software",
                "vendor": "Paychex",
                "version": "70",
                "install_date": "2018-12-14T00:00:00Z",
                "removal_date": None,
            }]}, status=200)
        add(GET, "http://127.0.0.1/api/v1/software?name=Another%20Software&version=70&vm=4&vendor=Paychex",
            json={'count': 0, 'results': []}, status=200)

        def request_callback(request):
            return (200, {}, request.body)

        add_callback(
            POST, 'http://127.0.0.1/api/v1/software/',
            callback=request_callback,
            content_type='application/json',
        )

        api = Api(endpoint="http://127.0.0.1/api/v1", host_dict={
            "name": "test",
            "software": [
                {
                    "package_name": "Test Software",
                    "software_vendor": "Paychex",
                    "versions": [
                        {
                            "install_date": "2018-12-14T00:00:00Z",
                            "name": "70",
                        }
                    ]
                },
                {
                    "package_name": "Another Software",
                    "software_vendor": "Paychex",
                    "versions": [
                        {
                            "install_date": "2018-12-14T00:00:00Z",
                            "name": "70",
                        }
                    ]
                }
            ]
        }).upsert()
        self.assertEqual(api[0]['name'], 'Another Software')

    @activate
    @patch.dict('os.environ', {'username': 'fake', 'password': 'pass'})
    def test_updating_software(self):
        add(GET, 'http://127.0.0.1/api/v1/virtualmachine?name=test',
            json={'count': 1, 'results': [{
                "url": "https:///127.0.0.1/api/v1/virtualmachine/4/"
            }]}, status=200)
        add(GET, 'http://127.0.0.1/api/v1/software?vm=4',
            json={'count': 1, 'results': [{
                "url": "http://127.0.0.1/api/v1/software/4/",
                "name": "Test Software",
                "vendor": "Paychex",
                "version": "70",
                "install_date": "2018-12-14T00:00:00Z",
                "removal_date": None,
            }]}, status=200)
        add(GET, 'http://127.0.0.1/api/v1/software?name=Test%20Software&version=70&vm=4&vendor=Paychex',
            json={'count': 1, 'results': [{
                "url": "http://127.0.0.1/api/v1/software/4/",
                "name": "Test Software",
                "vendor": "Paychex",
                "version": "70",
                "install_date": "2018-12-14T00:00:00Z",
                "removal_date": None,
            }]}, status=200)

        def request_callback(request):
            from json import dumps, loads
            return (200, {}, request.body)

        add_callback(
            PUT, 'http://127.0.0.1/api/v1/software/4/',
            callback=request_callback,
            content_type='application/json',
        )

        api = Api(endpoint="http://127.0.0.1/api/v1", host_dict={
            "name": "test",
            "software": [
                {
                    "package_name": "Test Software",
                    "software_vendor": "Paychex",
                    "versions": [
                        {
                            "install_date": "2018-12-30T00:00:00Z",
                            "name": "70",
                        }
                    ]
                }
            ]
        }).upsert()
        self.assertEqual(api[0]['install_date'], '2018-12-30T00:00:00+00:00')
    
    @activate
    @patch.dict('os.environ', {'username': 'fake', 'password': 'pass'})
    def test_updating_software_with_no_version_or_vendor(self):
        add(GET, 'http://127.0.0.1/api/v1/virtualmachine?name=test',
            json={'count': 1, 'results': [{
                "url": "https:///127.0.0.1/api/v1/virtualmachine/4/"
            }]}, status=200)
        add(GET, 'http://127.0.0.1/api/v1/software?vm=4',
            json={'count': 0, 'results': []}, status=200)
        add(GET, 'http://127.0.0.1/api/v1/software?name=Test%20Software&version=&vm=4&vendor=',
            json={'count': 0, 'results': []}, status=200)
        def request_callback(request):
            from json import dumps, loads
            return (200, {}, request.body)

        add_callback(
            POST, 'http://127.0.0.1/api/v1/software/',
            callback=request_callback,
            content_type='application/json',
        )

        api = Api(endpoint="http://127.0.0.1/api/v1", host_dict={
            "name": "test",
            "software": [
                {
                    "package_name": "Test Software",
                    "versions": [
                        {
                            "install_date": "2018-12-30T00:00:00Z",
                            "name": None,
                        }
                    ]
                }
            ]
        }).upsert()
        self.assertFalse(api[0]['version'])
       
    @activate
    @patch.dict('os.environ', {'username': 'fake', 'password': 'pass'})
    def test_no_change(self):
        add(GET, 'http://127.0.0.1/api/v1/virtualmachine?name=test',
            json={'count': 1, 'results': [{
                "url": "https:///127.0.0.1/api/v1/virtualmachine/4/"
            }]}, status=200)
        add(GET, 'http://127.0.0.1/api/v1/software?vm=4',
            json={'count': 1, 'results': [{
                "url": "http://127.0.0.1/api/v1//software/4/",
                "name": "Test Software",
                "vendor": "Paychex",
                "version": "70",
                "install_date": "2018-12-14T00:00:00Z",
                "removal_date": None,
            }]}, status=200)
        add(GET, 'http://127.0.0.1/api/v1/software?name=Test%20Software&version=70&vm=4&vendor=Paychex',
            json={'count': 1, 'results': [{
                "url": "http://127.0.0.1/api/v1//software/4/",
                "name": "Test Software",
                "vendor": "Paychex",
                "version": "70",
                "install_date": "2018-12-14T00:00:00Z",
                "removal_date": None,
            }]}, status=200)

        api = Api(endpoint="http://127.0.0.1/api/v1", host_dict={
            "name": "test",
            "software": [
                {
                    "package_name": "Test Software",
                    "software_vendor": "Paychex",
                    "versions": [
                        {
                            "install_date": "2018-12-14T00:00:00Z",
                            "name": "70"
                        }
                    ]
                }
            ]
        }).upsert()
        self.assertEqual(len(api), 0)
