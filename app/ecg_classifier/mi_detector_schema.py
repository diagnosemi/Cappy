from marshmallow import Schema, fields


# Data with key 'ecg_signal' must be a list of floats
class EcgClassifierSchema(Schema):
    ecg_signal = fields.List(fields.Float(allow_nan=True, allow_none=True))
