import os

import pytest

py_test_mark = pytest.mark.skipif(
    os.getenv("GITHUB_ENV") is not None, reason="We are not running locally, Dorothy."
)

from typing import List

import requests
from requests.exceptions import ConnectionError

from api_client.endpoint import Endpoint
from api_client.request import RestRequest


def is_responsive(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except ConnectionError:
        return False


@pytest.fixture(scope="module")
def httpbin_service(docker_ip, docker_services):
    """Ensure that HTTP service is up and responsive."""

    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("httpbin", 80)
    url = "http://{}:{}".format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_responsive(url)
    )
    return url


@pytest.fixture(scope="module")
def request_client_http_bin_local(http_service) -> RestRequest:
    endpoints: List[Endpoint] = []
    endpoints.append(Endpoint(name="get_gzip", path="/gzip"))
    return RestRequest(httpbin_service, endpoints, "abc")


def test_get_request_gzipped_local(
    request_client_http_bin: RestRequest,
):
    response = request_client_http_bin.call_endpoint(
        "get_gzip",
        headers={"Accept": "application/json", "Accept-Encoding": "gzip"},
    )
    assert response.is_json()
    assert response.data()["gzipped"]