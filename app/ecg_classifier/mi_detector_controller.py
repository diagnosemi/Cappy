from flask_restx import Resource, Namespace
from flask import jsonify, make_response, request
from marshmallow import ValidationError

from .mi_detector_schema import RequestBodySchema, EcgDataSchema
from .mi_detector_service import apply_preprocessing, classify_ecg_cnn_lstm
from .utils import encrypt, decrypt

ecg_classifier_ns = Namespace('ecg_classifier', description='Detects MI in ECG.')


@ecg_classifier_ns.route('/classify', methods=['POST'])
class Records(Resource):
    @ecg_classifier_ns.doc('An endpoint for classifying an ECG as healthy, MI, or other CVD.')
    def post(self):
        # Convert input payload to json and throw error if it doesn't exist
        request_json = request.get_json()
        if not request_json:
            return {"message": "No input payload provided"}, 400

        # Validate the format of the input payload
        payload_schema = RequestBodySchema()
        try:
            payload_schema.load(request_json)
        except ValidationError as err:
            return make_response(err.messages, 422)

        # Extract the actual data in the message and decrypt it to get a json
        body = request_json['body']
        data = decrypt(body)

        # Validate the schema of the ecg data
        schema = EcgDataSchema()
        try:
            schema.load(data)
        except ValidationError as err:
            return make_response(err.messages, 422)

        # Extract ecg signal and perform pre processing
        ecg_signal = data.get('ecg_signal')
        ecg_signal = apply_preprocessing(ecg_signal, old_fs=500, is_ptb_data=True)

        # Run model
        result = classify_ecg_cnn_lstm(ecg_signal)

        # Encrypt result
        result = encrypt(result)
        result = {"result": result}
        return jsonify(result)
