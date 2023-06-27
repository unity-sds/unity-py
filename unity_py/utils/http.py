"""
This module contains utility functions to support HTTP calls.
"""

def get_headers(token, additional_headers = None):
    """Returns a dictionary containing headers that will be used in an API call"""

    if token is None:
        raise Exception("No authorization token was provided.")

    if additional_headers is None:
        additional_headers = {}

    base_header = {
        "Authorization": "Bearer " + token,
    }

    return {**base_header, **additional_headers}
