import json
import logging
import random
from typing import Dict
from urllib.parse import urlencode

from cloudscraper import create_scraper

USER_AGENTS = [
    # Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36',

    # Firefox
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',

    # Safari
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.7 (KHTML, like Gecko) Version/9.1.2 Safari/601.7.7',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15',

    # Edge
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586'
]


class ResyApiWrapper:
        def __init__(self, resy_url, resy_api_key, logger: logging.Logger, resy_token=''):
                self.session = create_scraper()
                self.session.headers.update(
                        {
                                'authorization': "ResyAPI api_key=\"{resy_api_key}\"".format(resy_api_key=resy_api_key),
                                'user-agent': self.random_user_agent(),
                                'x-origin': "https://resy.com"
                        })
                self.resy_token = resy_token
                self.base_url = f"https://{resy_url}"
                self.api_wrapper_logger = logger

        def auth_user(self, user_creds):
                # basically dead because resy api refuses any attempt to auth through the api
                self.api_wrapper_logger.info(f"Attempting to authenticate user {user_creds['email']}")
                self.session.headers.update({"Content-Type": "application/x-www-form-urlencoded"})
                resy_resp = self.session.post(f"{self.base_url}/3/auth/password", data=user_creds)
                if resy_resp.status_code == 200:
                        return resy_resp.json()
                self.api_wrapper_logger.error(
                        f"Received {resy_resp.status_code} on request for resources. Resy Reason: {resy_resp.text}")
                return {'error': "error, view logs"}

        def set_resy_token(self, resy_token):
                self.resy_token = resy_token
                self.session.headers.update({"x-resy-auth-token": resy_token})

        def find_venue(self, search_request: Dict):
                self.api_wrapper_logger.info(f"Attempting to get venues with available reservations: {search_request}")
                find_venues_url = f"{self.base_url}/4/find?" + urlencode(search_request)
                return self.session.get(url=find_venues_url)

        def get_venue_details(self, venue_id):
                self.api_wrapper_logger.info(f"Attempting to get venue details for {venue_id}")
                return self.session.get(f"{self.base_url}/3/venue?id={venue_id}")

        def get_reservation_details(self, booking_request):
                self.api_wrapper_logger.info(f"Attempting to get reservation details for {booking_request['config_id']}")
                res_details_url = f"{self.base_url}/3/details?" + urlencode(booking_request, encoding='UTF-8')
                return self.session.get(res_details_url)

        def create_reservation(self, payment_method_id, booking_token):
                self.session.headers.update({"Content-Type": "application/x-www-form-urlencoded"})
                query_params = {
                        "book_token": booking_token,
                        "struct_payment_method": json.dumps({'id': payment_method_id})
                }
                self.api_wrapper_logger.info(f"Attempting to create reservation for {booking_token}")
                resp = self.session.post(f"{self.base_url}/3/book", data=query_params)
                return resp

        def get_res_list(self, uid):
                self.api_wrapper_logger.info(f"Attempting to check reservation for {uid}")
                return self.session.get(f"{self.base_url}/3/user/reservations")

        def search_availability(self, availability_input: Dict):
                self.api_wrapper_logger.info(
                f"Searching availability with: {availability_input}")
                self.session.headers.update({"Content-Type": "application/json"})
                payload = {
                "operationName": "SearchAvailability",
                "variables": {"input": availability_input},
                "query": (
                "query SearchAvailability($input: AvailabilityInput!) {"
                " availability(input: $input) {"
                "  ... on AvailabilitySuccess {"
                "   slots {"
                "    id\n    start_at\n    config_token\n    table_type {"
                "     id\n     name"
                "    }"
                "   }"
                "  }"
                "  ... on AvailabilityError {"
                "   code\n   message"
                "  }"
                " }"
                "}"
                ),
                }
                return self.session.post(f"{self.base_url}/graphql", json=payload)

        def random_user_agent(self):
                return random.choice(USER_AGENTS)
