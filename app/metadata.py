from marshmallow import Schema, fields, validates, ValidationError, post_load


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
    contact = fields.Str()

    @post_load
    def set_type(self, item, many, **kwargs):
        item["type"] = "item"
        return item

    # @validates("type")
    # def check_staff_type(self, data, **kwargs):
    #     if data != "item":
    #         raise ValidationError("Item metadata type required")


class TransportPointSchema(Schema):
    address = fields.Str()
    longitude = fields.Decimal()
    latitude = fields.Decimal()


class TransportMetadataSchema(SKUMetadataSchema):
    method = fields.Str()
    contact = fields.Str()
    points = fields.Nested(TransportPointSchema, many=True)

    @post_load
    def set_type(self, item, many, **kwargs):
        item["type"] = "transport"
        return item

    # @validates("type")
    # def check_staff_type(self, data, **kwargs):
    #     if data != "transport":
    #         raise ValidationError("Transport metadata type required")


class VoyagePointSchema(Schema):
    intent = fields.Str()
    status = fields.Str()
    longitude = fields.Decimal()
    latitude = fields.Decimal()


class JobMetadataSchema(Schema):
    voyage = fields.Nested(VoyagePointSchema, many=True)
