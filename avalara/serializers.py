from __future__ import unicode_literals

import datetime
from decimal import Decimal, ROUND_HALF_UP
import six

from serpy import BoolField, Field, IntField, Serializer


def get_decimal_value(value):
    if value:
        return str(Decimal(value).quantize(Decimal('.0001'), rounding=ROUND_HALF_UP))


def get_date_value(value):
    if isinstance(value, datetime.datetime):
        value = value.date()
    assert isinstance(value, datetime.date)
    return str(value)


def get_string_value(value):
    if value:
        return six.text_type(value)


class DecimalField(Field):
    to_value = staticmethod(get_decimal_value)


class DateField(Field):
    to_value = staticmethod(get_date_value)


class NullableStrField(Field):
    to_value = staticmethod(get_string_value)


class TaxOverrideSerializer(Serializer):
    reason = NullableStrField(label='Reason')
    tax_override_type = NullableStrField(label='TaxOverrideType')
    tax_date = DateField(label='TaxDate')
    tax_amount = DecimalField(label='TaxAmount')


class AddressSerializer(Serializer):
    address_code = IntField(label='AddressCode')
    address1 = NullableStrField(label='Line1')
    address2 = NullableStrField(label='Line2')
    address3 = NullableStrField(label='Line3')
    # City name, required unless PostalCode is specified and/or Latitude and Longitude are provided.
    city = NullableStrField(label='City')
    # State, province, or region name. Required unless City is specified and/or Latitude and Longitude are provided. length 3
    state = NullableStrField(label='Region')
    # Country code. If not provided, will default to 'US'.  Max. Length: 2
    country = NullableStrField(label='Country')
    # Postal or ZIP code, Required unless City and Region are specified, and/or Latitude and Longitude are provided. length 11
    postal_code = NullableStrField(label='PostalCode')
    latitude = DecimalField(label='Latitude')
    longitude = DecimalField(label='Longitude')
    tax_region_id = DecimalField(label='TaxRegionId')


class OrderLineSerializer(Serializer):
    # destination_code references an address from the Addresses collection
    line_number = IntField(label='LineNo')
    destination_code = IntField(label='DestinationCode')
    origin_code = IntField(label='OriginCode')
    # not required by avalara but I think this should be required for us
    item_code = NullableStrField(label='ItemCode')
    tax_code = NullableStrField(label='TaxCode')
    customer_usage_type = NullableStrField(label='CustomerUsageType')
    business_identification_number = NullableStrField(
        label='BusinessIdentificationNo',
    )
    description = NullableStrField(label='Description')
    qty = IntField(label='Qty')
    amount = DecimalField(label='Amount')
    discounted = BoolField(label='Discounted')
    tax_included = BoolField(label='TaxIncluded')
    ref_1 = NullableStrField(label='Ref1')
    ref_2 = NullableStrField(label='Ref2')


class OverridenOrderLineSerializer(OrderLineSerializer):
    tax_override = TaxOverrideSerializer(label='TaxOverride')


class BaseTaxRequestSerializer(Serializer):
    business_identification_no = NullableStrField(
        label='BusinessIdentificationNo', required=False
    )
    commit = BoolField(label='Commit')
    client = NullableStrField(label='Client')
    company_code = NullableStrField(label='CompanyCode')
    customer_code = NullableStrField(label='CustomerCode')
    currency_code = NullableStrField(label='CurrencyCode')
    customer_usage_type = NullableStrField(label='CustomerUsageType')
    detail_level = NullableStrField(label='DetailLevel')
    discount = DecimalField(label='Discount')
    doc_code = NullableStrField(label='DocCode')
    doc_type = NullableStrField(label='DocType')
    doc_date = DateField(label='DocDate')
    exemption_no = NullableStrField(label='ExemptionNo')
    location_code = NullableStrField(label='LocationCode')
    pos_lane_code = NullableStrField(label='PosLaneCode')
    purchase_order_no = NullableStrField(label='PurchaseOrderNo')
    reference_code = NullableStrField(label='ReferenceCode')
    addresses = AddressSerializer(label='Addresses', many=True,)


class GetTaxRequestSerializer(BaseTaxRequestSerializer):
    olines = OrderLineSerializer(label='Lines', many=True,)


class GetTaxRequestOverrideSerializer(BaseTaxRequestSerializer):
    olines = OverridenOrderLineSerializer(label='Lines', many=True,)

