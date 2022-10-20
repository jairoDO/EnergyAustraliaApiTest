import unittest
import requests
from requests.status_codes import codes
from schema import Schema

URL_API_REST = 'https://eacp.energyaustralia.com.au/codingtest/api/v1'

class EnergyAustraliaApiTest(unittest.TestCase):

    def test_get_festivals_code_request(self, attemp=0):
        url = f'{URL_API_REST}/festivals'
        response = requests.request('get', url)
        if response.status_code == codes.TOO_MANY:
            if attemp >= 5:
                self.fail(f'The endpoint is not working propertly error:{codes.TOO_MANY}')
            else:
                return self.test_get_festivals_code_request(attemp=attemp+1)
        self.assertEqual(codes.OK, response.status_code, 'The endpoint is not working properly')

    def test_wrong_petition_festival_with_post(self):
        url = f'{URL_API_REST}/festivals'
        response = requests.request('post', url)
        self.assertEqual(codes.NOT_FOUND, response.status_code, 'The endpoint is not working properly')

    def test_validate_content_json(self):
        url = f'{URL_API_REST}/festivals'
        response = requests.request('get', url)
        try:
           response.json()
        except Exception as e:
            self.fail(f'The response- does not respect json schema {response.text}')

    def test_validate_content_festivals(self, attemp=0):
        url = f'{URL_API_REST}/festivals'
        response = requests.request('get', url)
        json_response = response.json()
        festival_schema = Schema([{'name': str,
                                   'bands': [{'name': str,
                                              'recordLabel': str}]}])
        if response.status_code == codes.TOO_MANY:
            if attemp >= 5:
                self.fail(f'The endpoint is not working propertly error:{codes.TOO_MANY}')
            else:
                return self.test_validate_content_festivals(attemp=attemp+1)
        self.assertEqual(response.status_code, codes.OK)
        self.assertTrue(festival_schema.is_valid(json_response), 'The response does not respect the scheme')


    def test_too_many_request_should_check_throttling(self):
        from multiprocessing import dummy
        pool = dummy.Pool(5)

        def get_festival(number_petition):
            url = f'{URL_API_REST}/festivals'
            print(f'Thread number - {number_petition}')
            return requests.request('get', url)
        petitions = pool.map(get_festival, range(20))
        pool.close()
        pool.join()
        ## iter from the petitions and check if there are any request with code TOO_MANY
        self.assertTrue(any(map(lambda response: response.status_code == codes.TOO_MANY, petitions)), 'The server is not handler throttling')



if __name__ == '__main__':
    unittest.main()
