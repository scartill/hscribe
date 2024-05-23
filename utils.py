import json

import boto3


def response(data_or_error=None, rc=200):
    if rc != 200:
        payload = {
            'IsSuccessful': False,
            'Error': data_or_error
        }
    else:
        payload = {'IsSuccessful': True}

        if data_or_error:
            payload.update(data_or_error)

    return {
        'statusCode': rc,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT,PATCH,DELETE'
        },
        'body': json.dumps(payload)
    }


def get_sm_secret(name):
    client = boto3.client('secretsmanager')
    get_secret_value_response = client.get_secret_value(
        SecretId=name
    )
    return json.loads(get_secret_value_response['SecretString'])


def request_params(event):
    params = dict()
    method = event['requestContext']['http']['method']

    pathParams = event.get('pathParameters')
    if pathParams:
        params.update(pathParams)

    qsParams = event.get('queryStringParameters')
    if qsParams:
        params.update(qsParams)

    if method in ['POST', 'PUT', 'PATCH']:
        if 'body' not in event:
            raise UserWarning(
                'A request body must be present for POST and PUT requests'
            )

        params.update(json.loads(event['body']))

    return (method, params)
