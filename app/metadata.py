from marshmallow import Schema, fields, validates, ValidationError, post_load


class SKUMetadataSchema(Schema):
    type = fields.Str(missing="misc")


class ServiceMetadataSchema(SKUMetadataSchema):
    provider_id = fields.UUID()

    @post_load
    def set_type(self, item, many, **kwargs):
        item["type"] = "service"
        return item


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


class TransportPointSchema(Schema):
    address = fields.Str()
    longitude = fields.Float()
    latitude = fields.Float()
    timestamp = fields.DateTime()


class TransportMetadataSchema(SKUMetadataSchema):
    method = fields.Str()
    contact = fields.Str()
    points = fields.Nested(TransportPointSchema, many=True)

    @post_load
    def set_type(self, item, many, **kwargs):
        item["type"] = "transport"
        return item


class VoyagePointSchema(Schema):
    intent = fields.Str()
    status = fields.Str()
    longitude = fields.Float()
    latitude = fields.Float()
    timestamp = fields.DateTime()


class JobMetadataSchema(Schema):
    voyage = fields.Nested(VoyagePointSchema, many=True)
