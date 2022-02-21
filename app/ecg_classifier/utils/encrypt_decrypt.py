import os
import json
from base64 import b64encode, b64decode
from cryptography.fernet import Fernet


# Decrypts a message that is a base64 string using Fernet and converts to json
def decrypt(message):
    # Convert string message to bytes
    message = str.encode(message)

    # Decrypt using Fernet
    key = str.encode(os.getenv('CRYPTO_KEY'))
    f = Fernet(key)
    decrypted_message = f.decrypt(message)

    # Convert from base64 to bytes
    base64_message = b64decode(decrypted_message)

    # Convert to string from bytes
    string_message = base64_message.decode('ascii')

    # Convert to json
    json_message = json.loads(string_message)
    return json_message


# Converts a json message to base64 and encrypts using Fernet
def encrypt(message):
    # Convert json to string
    string_message = json.dumps(message)

    # Convert string to bytes
    bytes_message = string_message.encode('ascii')

    # Convert bytes to base64
    base64_message = b64encode(bytes_message)

    # Encrypt using Fernet and convert to string (get rid of b'')
    key = str.encode(os.getenv('CRYPTO_KEY'))
    f = Fernet(key)
    encrypted_message = f.encrypt(base64_message)
    encrypted_message = str(encrypted_message)[2:-1]
    return encrypted_message
