from flask_restx import Resource, Namespace
from flask import jsonify, make_response, request
from marshmallow import ValidationError

from .mi_detector_schema import EcgClassifierSchema
from .mi_detector_service import apply_preprocessing, classify_ecg_cnn_lstm

ecg_classifier_ns = Namespace('ecg_classifier', description='Detects MI in ECG.')


@ecg_classifier_ns.route('/classify', methods=['POST'])
class Records(Resource):
    @ecg_classifier_ns.doc('An endpoint for classifying an ECG as healthy, MI, or other CVD.')
    def post(self):
        # Convert input payload to json and throw error if it doesn't exist
        data = request.get_json()
        if not data:
            return {"message": "No input payload provided"}, 400

        # Validate input payload
        schema = EcgClassifierSchema()
        try:
            schema.load(data)
        except ValidationError as err:
            return make_response(err.messages, 422)

        # Extract ecg signal and perform pre processing
        ecg_signal = data.get('ecg_signal')
        ecg_signal = apply_preprocessing(ecg_signal, old_fs=500, is_ptb_data=True)

        # Run model
        result = classify_ecg_cnn_lstm(ecg_signal)
        print(result)
        print(type(result))
        return jsonify("hi")
