import json

import boto3


def get_sm_secret(name):
    client = boto3.client('secretsmanager')
    get_secret_value_response = client.get_secret_value(
        SecretId=name
    )
    return json.loads(get_secret_value_response['SecretString'])


def request_params(event):
    params = dict()
    method = event['httpMethod']

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
