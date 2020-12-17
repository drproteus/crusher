from dataclasses import dataclass
from marshmallow import Schema, fields, validates, ValidationError, post_load


@dataclass
class SKUMetadata:
    type: str


@dataclass
class StaffMetadata(SKUMetadata):
    first_name: str
    last_name: str
    billing_address: str
    mailing_address: str
    phone_number: str
    email: str
    affiliate_client_ids: list


@dataclass
class ItemMetadata(SKUMetadata):
    name: str
    stock: float
    upc: str
    vendor: str
    vendor_contact: str


@dataclass
class TransportMetadata(SKUMetadata):
    vendor: str
    vendor_contact: str
    driver_contact: str


# ---


class SKUMetadataSchema(Schema):
    type = fields.Str(missing="misc")


class StaffMetadataSchema(SKUMetadataSchema):
    first_name = fields.Str()
    last_name = fields.Str()
    billing_address = fields.Str()
    mailing_address = fields.Str()
    phone_number = fields.Str()
    email = fields.Str()
    affiliate_client_ids = fields.List(fields.UUID)

    @post_load
    def set_type(self, item, many, **kwargs):
        item["type"] = "staff"
        return item

    # @validates("type")
    # def check_staff_type(self, data, **kwargs):
    #     if data != "staff":
    #         raise ValidationError("Staff metadata type required")


class ItemMetadataSchema(SKUMetadataSchema):
    name = fields.Str()
    stock = fields.Float()
    upc = fields.Str()
    vendor = fields.Str()
    vendor_contact = fields.Str()

    @post_load
    def set_type(self, item, many, **kwargs):
        item["type"] = "item"
        return item

    # @validates("type")
    # def check_staff_type(self, data, **kwargs):
    #     if data != "item":
    #         raise ValidationError("Item metadata type required")


class TransportMetadataSchema(SKUMetadataSchema):
    vendor = fields.Str()
    vendor_contact = fields.Str()
    driver_contact = fields.Str()

    @post_load
    def set_type(self, item, many, **kwargs):
        item["type"] = "transport"
        return item

    # @validates("type")
    # def check_staff_type(self, data, **kwargs):
    #     if data != "transport":
    #         raise ValidationError("Transport metadata type required")
