from __future__ import unicode_literals
import base64
import os
from urlparse import urljoin

import requests


class Avalara(object):

    #TODO have a switch to a live enviroment when testing is complete
    BASE_URL = 'https://development.avalara.net/1.0/'

    def __init__(self, account_number=None, license_key=None):
        self.account_number = account_number or os.getenv('AVALARA_ACCOUNT_NUMBER')
        self.license_key = license_key or os.getenv('AVALARA_LICENSE_KEY')

    @property
    def _auth_token(self):
        return base64.b64encode(
            ':'.join([self.account_number, self.license_key])
        ).decode()

    def _make_request(self, method, url, params=None, json=None):
        response = requests.request(
            method, url, params=params, json=json, headers={
                'Authorization': 'Basic %s' % str(self._auth_token),
                'Content-Type': 'application/json'
            }
        )
        return response.json()

    def _build_url(self, endpoint, **replacements):
        for k, v in replacements:
            #TODO build estimate tax url with replacements
            pass

        return urljoin(self.BASE_URL, endpoint)

    def get_tax(self, get_tax_request):
        url = self._build_url('tax/get')
        return self._make_request('post', url, json=get_tax_request)

    def validate_address(self, address1, country, address2='',
                         address3='', city='', region='', postal_code=''):

        url = self._build_url('address/validate')
        request_data = {
            'Line1': address1,
            'Line2': address2,
            'Line3': address3,
            'Country': country,
            'City': city,
            'Region': region,
            'PostalCode': postal_code
        }
        return self._make_request('get', url, params=request_data)

    def estimate_tax(self, latitude, longitude, sale_amount):
        url = self._build_url('{{longitude}},{{latitude}}/tax/estimate?{{saleamount}}',
                              latitude=latitude, longitude=longitude, saleamount=sale_amount)
        return self._make_request('get', url)

    def void_document(self, cancel_tax_request):
        url = self._build_url('tax/cancel')
        return self._make_request('post', url, json=cancel_tax_request)