from __future__ import unicode_literals

import datetime
from decimal import Decimal, ROUND_HALF_UP
import six

from serpy import Serializer

from . import serializers


DEFAULT_TAX_CODE = 'P0000000'


def strip_if_text(value):
    if isinstance(value, six.string_types):
        value = value.strip()
    return value


def remove_nulls_from_dict(d):
    """
    remove_nulls_from_dict function recursively remove empty or null values
    from dictionary and embedded lists of dictionaries
    """
    if isinstance(d, dict):
        return {k: remove_nulls_from_dict(v) for k, v in six.iteritems(d) if v}
    if isinstance(d, list):
        return [remove_nulls_from_dict(entry) for entry in d if entry]
    else:
        return d


class BaseAvalaraModel(object):
    """
    Base Class for Avalara Models.  includes methods for sanitizing and
    verifying attributes as well as serialization
    """
    # any required fields go in the required list.  Use _validate required
    # method to ensure they are set
    required = list()

    # be sure to set the serializer on the object if you want serialization
    serializer = None

    # defaults is a dictionary of attributes and their values if they have
    # a default.  Set in the __init__
    defaults = dict()

    def __init__(self, *args, **kwargs):
        self.__dict__.update(self._get_fields)
        # set defaults on any attributes not passed in through kwargs
        self.__dict__.update(self.defaults)
        # trimming all text/string fields before setting attributes
        cleaner_kwargs = {k: strip_if_text(v) for k, v in kwargs.items()}
        # set all attributes passed in through kwargs.  These should all
        # match the names of the fields of the appropriate serializer
        self.__dict__.update(remove_nulls_from_dict(cleaner_kwargs))

    @property
    def _get_fields(self):
        keys = dict()
        for k, v in self.serializer._field_map.items():
            if isinstance(v, Serializer) and v.many:
                keys[k] = list()
            else:
                keys[k] = None
        return keys

    def _validate_required(self):
        """validate required fields are present"""
        for i in self.required:
            if not getattr(self, i):
                raise AttributeError

    @property
    def data(self):
        """
        This property serializes object with the appropriate serpy serializer
        set on the class attribute serializer.
        """
        return self.serializer(self).data

    @property
    def request_body(self):
        """
        remove nulls and format python dictionary as json
        """
        return remove_nulls_from_dict(self.data)


class TaxOverride(BaseAvalaraModel):
    serializer = serializers.TaxOverrideSerializer
    required = [
        'reason',
        'tax_override_type',
    ]
    defaults = {
        'reason': 'Imported From External System',
        'tax_override_type': 'TaxAmount',
        'tax_date': datetime.date.today(),
    }


class OrderLine(BaseAvalaraModel):
    serializer = serializers.OrderLineSerializer
    required = [
        'line_number',
        'destination_code',
        'item_code',
        'qty',
    ]
    defaults = {
        'tax_code': DEFAULT_TAX_CODE,
        'qty': 1,
    }

    def __init__(self, **kwargs):
        super(OrderLine, self).__init__(**kwargs)
        self._validate_required()
        if kwargs.get('price') and not self.amount:
            self._set_amount()

    def _set_amount(self):
        """
        use this if you are passing in price and not amount to
        calculate the amount by qty and price
        """
        self.amount = Decimal(self.price).quantize(Decimal('.01'), rounding=ROUND_HALF_UP) * self.qty

    def _override(self, **kwargs):
        override = TaxOverride(**kwargs)
        self.tax_override = override


class Address(BaseAvalaraModel):
    serializer = serializers.AddressSerializer
    required = ['address_code', 'address1', 'city', 'state', 'postal_code']
    defaults = {'country': 'US'}

    def __init__(self, **kwargs):
        super(Address, self).__init__(**kwargs)
        self._fix_lines()
        self._validate_required()

    def _fix_lines(self):
        """shuffle address lines if we are missing line 1 but not 2 or 3"""
        # no address 1 but entry on 2 and possibly 3 but I don't care
        if not self.address1 and self.address2:
            self.address1, self.address2, self.address3 = self.address2, self.address3, None
        # no address 1 or 2 but entry on 3
        if self.address3 and not self.address1 and not self.address2:
            self.address1, self.address3 = self.address3, None


class GetTaxRequest(BaseAvalaraModel):
    serializer = serializers.GetTaxRequestSerializer
    required = ['customer_code', 'doc_code']
    defaults = {
        'detail_level': 'Document',
        'company_code': 'SOC',
        'customer_code': 'TEMPCODE',
        'currency_code': 'USD',
        'doc_date': datetime.date.today(),
    }

    def add_address(self, **kwargs):
        """
        add address line to GetTaxRequest object and return the address_code.
        use the address_codes returned when creating line items
        """
        address_code = len(self.addresses) + 1
        kwargs['address_code'] = address_code
        address = Address(**kwargs)
        self.addresses.append(address)
        return address_code

    def add_line(self, override_lookup=dict(), **kwargs):
        """
        The add_line method adds line to GetTaxRequest object.
        Ensure you pass the address_code in with kwargs.  This is returned
        from the add_address method. Pass in an override_lookup if planning
        to override calculated tax by lines
        DO NOT MIX LINES WITH AND WITHOUT OVERRIDES!!
        I can get the two to work together later if this actually turns out to
        be a thing.
        """
        kwargs['line_number'] = len(self.olines) + 1
        line = OrderLine(**kwargs)
        if override_lookup:
            self.serializer = serializers.GetTaxRequestOverrideSerializer
            line._override(**override_lookup)
        self.olines.append(line)

