from unittest import TestLoader, TextTestRunner, TestSuite
from api_test import APITestCase
from software_test import SoftwareTestCase
from database_test import DatabaseTestCase
from host_test import HostTestCase
if __name__ == '__main__':
    TEST_CLASSES_TO_RUN = [
        APITestCase,
        SoftwareTestCase,
        DatabaseTestCase,
        HostTestCase
    ]

    LOADER = TestLoader()
    SUITES_LIST = [LOADER.loadTestsFromTestCase(
        test_class) for test_class in TEST_CLASSES_TO_RUN]
    BIG_SUITE = TestSuite(SUITES_LIST)
    exit(TextTestRunner(verbosity=2).run(BIG_SUITE).wasSuccessful())
