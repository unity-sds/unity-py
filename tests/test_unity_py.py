
from unity_py import Unity

import pytest


@pytest.fixture
def cleanup_update_test():
    yield None
    print("Cleanup...")


@pytest.mark.regression
def test_example_regression_test(cleanup_update_test):
    print("Example regression test")
    assert True == True
