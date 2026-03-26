import json
import os
import io

os.environ['TELEGRAM_BOT_NAME'] = 'test_bot'

class MockBoto3Client:
    def get_secret_value(self, SecretId):
        return {'SecretString': json.dumps({'Token': '123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ'})}

import utils
def mock_get_sm_secret(name):
    return {'Token': '123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ'}
utils.get_sm_secret = mock_get_sm_secret

from lambda_function import lambda_handler

event = {
    'requestContext': {
        'http': {
            'method': 'POST'
        }
    },
    'queryStringParameters': {
        'token': '123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ'
    },
    'body': json.dumps({
        'update_id': 12345,
        'message': {
            'message_id': 1,
            'date': 1234567890,
            'chat': {'id': 123, 'type': 'private'},
            'from': {'id': 456, 'is_bot': False, 'first_name': 'Test'},
            'audio': {'file_id': 'fake_file_id', 'file_unique_id': 'fake_uniq_id', 'duration': 10}
        }
    })
}

try:
    response = lambda_handler(event, None)
    print(response)
except Exception as e:
    print(f"Failed with {e}")
