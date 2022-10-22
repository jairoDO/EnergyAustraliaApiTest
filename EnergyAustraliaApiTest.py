import allure
import requests
from multiprocessing import dummy

import pytest

from requests.exceptions import InvalidSchema
from requests.status_codes import codes
from schema import Schema

URL_API_REST = 'https://eacp.energyaustralia.com.au/codingtest/api/v1'
URL_FESTIVALS = f'{URL_API_REST}/festivals'


@allure.title(f"Check endpoint api/v1/festivals should response with code 200")
def test_get_festivals_code_request():
    response = get_festivals()
    with allure.step("Check response code status should be 200"):
        assert codes.OK == response.status_code, f'The endpoint is not working properly I should received code ' \
                                                 f'response {codes.OK} but I received {response.status_code}'


@allure.title(f'Check when the user try a POST petition to api/v1/festivals should receiced an error {codes.NOT_FOUND}')
def test_wrong_petition_festival_with_post():
    with allure.step(f'I make a POST petition to {URL_FESTIVALS}'):
        response = requests.request('post', URL_FESTIVALS)
    with allure.step(f"I should got a response with code error {codes.NOT_FOUND}"):
        assert codes.NOT_FOUND == response.status_code, 'The endpoint is allowing to access with a method POST to ' \
                                                        'festivals'


@allure.title('Check the content should be in json format')
def test_validate_content_json():
    with allure.step(f'I make a GET petition to {URL_FESTIVALS}'):
        response = get_festivals()
    with allure.step('I convert the response to json format'):
        try:
            response.json()
        except InvalidSchema as exc:
            pytest.fail(f'The response does not have json format {exc}')
        except Exception as exc:
            pytest.fail(f'The request is not getting 200 {exc}')


@allure.title('Check the response content has a validate schema for festivals')
def test_validate_content_festivals():
    with allure.step(f'I make a GET petition to {URL_FESTIVALS}'):
        response = get_festivals()
    with allure.step('I check the status of the response is ok'):
        assert response.status_code == codes.OK, f'The response status should be 200 but found {response.status_code}'
    with allure.step('I check the response has a validate Schema'):
        json_response = response.json()
        festival_schema = Schema([{'name': str,
                                   'bands': [{'name': str,
                                              'recordLabel': str}]}])

        assert festival_schema.is_valid(json_response), 'The response does not respect the scheme'


@allure.title("I Check that it prevents the overload of requests from the same client")
def test_too_many_request_should_check_throttling():
    petitions = force_overload_petitions()
    with allure.step('I check the server control the overload of requests from the same client'):
        assert any(map(lambda response: response.status_code == codes.TOO_MANY,
                       petitions)), 'The server is not handler throttling'


@allure.title('I check that when an over request occurs, the response is in json format')
def test_format_json_when_check_throttling_happens():
    petitions = force_overload_petitions()
    with allure.step('I check the server control the overload of requests from the same client'):
        overload_petitions = list(filter(lambda response: response.status_code == codes.TOO_MANY, petitions))
        assert len(overload_petitions) >= 1, f'There are not any request with status {codes.TOO_MANY}'
        try:
            overload_petitions[0].json()
        except Exception as exc:
            pytest.fail(f'The response does not have json format {exc}')


def force_overload_petitions():
    with allure.step('Force to make 20 petitions to force overload'):
        with allure.step('I Create a pool of request to festivals'):
            pool = dummy.Pool(5)

            def get_festivals(number_petition):

                print(f'Thread number - {number_petition}')
                return requests.request('get', URL_FESTIVALS)

            petitions = pool.map(get_festivals, range(25))
            pool.close()
            pool.join()
    return petitions


@allure.step(f"I make a get petition to {URL_FESTIVALS}")
def get_festivals(attempt=5):
    """
    This func try to make a request to the endpoint festivals and if the response was with status code TOO_MANY will
    try attempt times if not we raise an Exemption
    :param attempt: the attempt number to try
    :return: Exception or response object
    """
    response = requests.request('get', URL_FESTIVALS)
    if response.status_code == codes.TOO_MANY:
        if attempt <= 0:
            raise Exception(f'Error {codes.TOO_MANY} when I make a get request to {URL_FESTIVALS} ')
        else:
            return get_festivals(attempt=attempt - 1)
    return response
