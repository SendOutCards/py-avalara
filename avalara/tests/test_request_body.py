import copy
import datetime
import unittest

from ..models import GetTaxRequest


AVA_LOOKUP = {
    'user_id': 1,
    'doc_date': datetime.date(2016, 5, 5),
    'doc_code': 5,
}


LINE_LOOKUP_1 = {
    # item with no qty (should become 1) and calculated amount
    # also no tax_code so should become default
    'item_code': '12345',
    'amount': 350.37,
    'description': 'some description',
}

LINE_LOOKUP_2 = {
    # item with qty and price to test _set_amount method
    'item_code': '1245',
    # tax code should override default
    'tax_code': '42',
    'price': 15,
    'qty': 5,
    'description': 'some other description',
}

ORIGIN_ADDRESS_LOOKUP = {
    'address1': '123 some street name',
    'address2': 'and another',
    'city': 'a city',
    'state': 'a state',
    'country': 'US',
    'postal_code': '81344',
}


DESTINATION_ADDRESS_LOOKUP = {
    # test address _fix_lines method
    'address1': None,
    'address2': '124 some other street name',
    'address3': 'and another',
    'city': 'another city',
    'state': 'another state',
    'country': 'US',
    'postal_code': '81345',
}

OVERRIDE_LOOKUP_1 = {
    'tax_date': datetime.date(2016, 5, 5),
    'tax_amount': 15.37,
}

OVERRIDE_LOOKUP_2 = {
    'tax_date': datetime.date(2016, 5, 5),
    'tax_amount': 12.00,
}


class GetTaxRequestTest(unittest.TestCase):
    def test_initial_doc(self):
        # test initial doc
        # create avalara GetTaxRequest object
        ava = GetTaxRequest(**AVA_LOOKUP)
        initial_request_body = {
            u'CompanyCode': u'SOC',
            u'CurrencyCode': u'USD',
            u'CustomerCode': u'TEMPCODE',
            u'DetailLevel': u'Document',
            u'DocCode': u'5',
            u'DocDate': '2016-05-05'
        }
        self.assertEqual(initial_request_body, ava.request_body)

    def test_add_address_lines(self):
        # test doc with address1
        ava = GetTaxRequest(**AVA_LOOKUP)
        origin_address = ava.add_address(**ORIGIN_ADDRESS_LOOKUP)
        destination_address = ava.add_address(**DESTINATION_ADDRESS_LOOKUP)
        self.assertEqual(origin_address, 1)
        self.assertEqual(destination_address, 2)
        address_request = {
            u'Addresses': [{
                u'AddressCode': 1,
                u'City': u'a city',
                u'Country': u'US',
                u'Line1': u'123 some street name',
                u'Line2': u'and another',
                u'PostalCode': u'81344',
                u'Region': u'a state'
                },
                {
                    u'AddressCode': 2,
                    u'City': u'another city',
                    u'Country': u'US',
                    u'Line1': u'124 some other street name',
                    u'Line2': u'and another',
                    u'PostalCode': u'81345',
                    u'Region': u'another state'
                }],
            u'CompanyCode': u'SOC',
            u'CurrencyCode': u'USD',
            u'CustomerCode': u'TEMPCODE',
            u'DetailLevel': u'Document',
            u'DocCode': u'5',
            u'DocDate': '2016-05-05'
        }
        self.assertEqual(address_request, ava.request_body)

    def add_line_item(self):
        # test doc with address and lines
        ava = GetTaxRequest(**AVA_LOOKUP)
        origin_code = ava.add_address(**ORIGIN_ADDRESS_LOOKUP)
        destination_code = ava.add_address(**DESTINATION_ADDRESS_LOOKUP)
        line_lookup = copy.deepcopy(LINE_LOOKUP_1)
        line_lookup['destination_code'] = destination_code
        line_lookup['origin_code'] = origin_code
        ava.add_line(**line_lookup)
        # and another!!
        line_lookup_2 = copy.deepcopy(LINE_LOOKUP_2)
        line_lookup_2['destination_code'] = destination_code
        line_lookup_2['origin_code'] = origin_code
        ava.add_line(**line_lookup_2)
        line_items_request_body = {
            u'Addresses': [{
                u'AddressCode': 1,
                u'City': u'a city',
                u'Country': u'US',
                u'Line1': u'123 some street name',
                u'Line2': u'and another',
                u'PostalCode': u'81344',
                u'Region': u'a state'
            },
                {
                    u'AddressCode': 2,
                    u'City': u'another city',
                    u'Country': u'US',
                    u'Line1': u'124 some other street name',
                    u'Line2': u'and another',
                    u'PostalCode': u'81345',
                    u'Region': u'another state'
            }],
            u'CompanyCode': u'SOC',
            u'CurrencyCode': u'USD',
            u'CustomerCode': u'TEMPCODE',
            u'DetailLevel': u'Document',
            u'DocCode': u'5',
            u'DocDate': '2016-05-05',
            u'Lines': [{
                u'Amount': '350.37',
                u'Description': u'some description',
                u'DestinationCode': 2,
                u'ItemCode': u'12345',
                u'LineNo': 1,
                u'OriginCode': 1,
                u'Qty': 1,
                u'TaxCode': u'P0000000'
            },
                {
                    u'Amount': '75.00',
                    u'Description': u'some other description',
                    u'DestinationCode': 2,
                    u'ItemCode': u'1245',
                    u'LineNo': 2,
                    u'OriginCode': 1,
                    u'Qty': 5,
                    u'TaxCode': u'42'
            }]}
        self.assertEqual(line_items_request_body, ava.request_body)

    def test_order_line_tax_override(self):
        ava = GetTaxRequest(**AVA_LOOKUP)
        origin_code = ava.add_address(**ORIGIN_ADDRESS_LOOKUP)
        destination_code = ava.add_address(**DESTINATION_ADDRESS_LOOKUP)
        line_lookup = copy.deepcopy(LINE_LOOKUP_1)
        line_lookup['destination_code'] = destination_code
        line_lookup['origin_code'] = origin_code
        ava.add_line(override_lookup=OVERRIDE_LOOKUP_1, **line_lookup)
        # and another!!
        line_lookup_2 = copy.deepcopy(LINE_LOOKUP_2)
        line_lookup_2['destination_code'] = destination_code
        line_lookup_2['origin_code'] = origin_code
        ava.add_line(override_lookup=OVERRIDE_LOOKUP_2, **line_lookup_2)
        request_body = {
            u'Addresses': [{
                u'AddressCode': 1,
                u'City': u'a city',
                u'Country': u'US',
                u'Line1': u'123 some street name',
                u'Line2': u'and another',
                u'PostalCode': u'81344',
                u'Region': u'a state'
            },
                {
                    u'AddressCode': 2,
                    u'City': u'another city',
                    u'Country': u'US',
                    u'Line1': u'124 some other street name',
                    u'Line2': u'and another',
                    u'PostalCode': u'81345',
                    u'Region': u'another state'
                }],
            u'CompanyCode': u'SOC',
            u'CurrencyCode': u'USD',
            u'CustomerCode': u'TEMPCODE',
            u'DetailLevel': u'Document',
            u'DocCode': u'5',
            u'DocDate': '2016-05-05',
            u'Lines': [{
                u'Amount': '350.37',
                u'Description': u'some description',
                u'DestinationCode': 2,
                u'ItemCode': u'12345',
                u'LineNo': 1,
                u'OriginCode': 1,
                u'Qty': 1,
                u'TaxCode': u'P0000000',
                u'TaxOverride': {
                    u'Reason': u'Imported From External System',
                    u'TaxAmount': '15.37',
                    u'TaxDate': '2016-05-05',
                    u'TaxOverrideType': u'TaxAmount'
                }},
                {
                    u'Amount': '75.00',
                    u'Description': u'some other description',
                    u'DestinationCode': 2,
                    u'ItemCode': u'1245',
                    u'LineNo': 2,
                    u'OriginCode': 1,
                    u'Qty': 5,
                    u'TaxCode': u'42',
                    u'TaxOverride': {
                        u'Reason': u'Imported From External System',
                        u'TaxAmount': '12.00',
                        u'TaxDate': '2016-05-05',
                        u'TaxOverrideType': u'TaxAmount'
                    }
                }]}
        self.assertEqual(request_body, ava.request_body)

