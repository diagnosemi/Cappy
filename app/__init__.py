from flask import Flask
from flask_restx import Api
from flask_cors import CORS

from app.ecg_classifier import ecg_classifier_ns

# Initialize app and api
app = Flask(__name__)
api = Api(app)
CORS(app)

# Config app by dictionary in config file
# config_name = 'api_{}'.format(os.getenv('FLASK_ENV'))
# config_obj = config_by_name[config_name]
# app.config.from_object(config_obj)

# Attach namespace to api
api.add_namespace(ecg_classifier_ns)

app.app_context().push()

if __name__ == '__main__':
    app.run()


