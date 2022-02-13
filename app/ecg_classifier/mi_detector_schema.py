from marshmallow import Schema, fields


# The payload has key "body" and value is a base64 string
class RequestBodySchema(Schema):
    body = fields.String()


# Data with key 'ecg_signal' must be a list of floats
class EcgDataSchema(Schema):
    ecg_signal = fields.List(fields.Float(allow_nan=True, allow_none=True))
