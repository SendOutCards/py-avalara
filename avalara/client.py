from __future__ import unicode_literals
import base64
import os

import requests
from six.moves.urllib.parse import urljoin


DEFAULT_BASE_URL = 'https://development.avalara.net/1.0/'


class Avalara(object):

    def __init__(self, account_number=None, license_key=None, **kwargs):
        self.account_number = account_number or os.getenv('AVALARA_ACCOUNT_NUMBER')
        self.license_key = license_key or os.getenv('AVALARA_LICENSE_KEY')
        self.base_url = os.getenv('AVALARA_BASE_URL') or DEFAULT_BASE_URL

    @property
    def _auth_token(self):
        return base64.b64encode(
            ':'.join([self.account_number, self.license_key]).encode('ascii')
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

        return urljoin(self.base_url, endpoint)

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


class GetTaxRequest(Avalara):
    def __init__(self, account_number=None, license_key=None, **kwargs):
        super(GetTaxRequest, self).__init__(account_number=account_number, license_key=license_key, **kwargs)
        self.get_tax_request = {
            "CustomerCode": kwargs.get('user_id', 'TEMPCODE'),
            "CompanyCode": "SOC",
            "DetailLevel": "Document",
            "CurrencyCode": "USD",
            "Addresses": [],
            "Lines": []
        }

    def _get_tax(self):
        url = self._build_url('tax/get')
        return self._make_request('post', url, json=self.get_tax_request)

    def get_tax(self):
        self.get_tax_request['DocType'] = 'SalesOrder'
        self.get_tax_request['Commit'] = 'false'
        return self._get_tax()

    def commit_tax(self):
        self.get_tax_request['DocType'] = 'SalesInvoice'
        self.get_tax_request['Commit'] = 'true'
        return self._get_tax()

    def add_line_item(self, address_number, tax_code, item_code, qty, price, desc=''):
        """
        add all lines for get tax request using this method.  Ensure you create
        address lines and use appropriate address_numbers using the add_address_line method
        """
        self.get_tax_request['Lines'].append({
            'LineNo': len(self.get_tax_request['Lines']) + 1,
            'TaxCode': tax_code,
            'ItemCode': item_code,
            'Qty': qty,
            'Amount': qty * price,
            'Description': desc[:255],
            'DestinationCode': address_number,
        })

    def add_address_line(self, **kwargs):
        """
        add all address lines here and use the returned address_number when
        creating line items for add_line_item method
        """
        address_number = len(self.get_tax_request['Addresses']) + 1
        self.get_tax_request['Addresses'].append({
            'AddressCode': address_number,
            'Line1': kwargs.get('address1', ''),
            'Line2': kwargs.get('address2', ''),
            'City': kwargs.get('city', ''),
            'Region': kwargs.get('state', ''),
            'Country': kwargs.get('country', ''),
            'PostalCode': kwargs.get('postal_code', '')
        })
        return address_number

