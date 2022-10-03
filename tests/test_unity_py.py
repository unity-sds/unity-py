from unity_py.unity import Unity

import pytest


@pytest.fixture
def cleanup_update_test():
    yield None
    print("Cleanup...")


def test_default_unity_client():
    client = Unity()
    assert True == True

@pytest.mark.regression
def test_example_regression_test(cleanup_update_test):
    print("Example regression test")
    assert True == True
