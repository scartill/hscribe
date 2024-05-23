import random

import boto3
import zipfile
import os


LAMBDA_NAME = 'hscribe-bot-webhook'
BUCKET_NAME = 'public.resnick'
DIST_FILE = 'dist/hscribe-{0}.zip'
FILES_TO_ZIP = ['hscribe.py', 'lambda_function.py', 'utils.py']

dist_filename = DIST_FILE.format(random.randint(0, 1000))
# List of files to include in the zip file

# Create a new zip file
with zipfile.ZipFile(dist_filename, 'w') as zip_file:
    # Add each file to the zip file
    for file in FILES_TO_ZIP:
        zip_file.write(file, os.path.basename(file))

s3 = boto3.client('s3')
dist_s3_filename = f'hscribe/{dist_filename}'
s3.upload_file(dist_filename, BUCKET_NAME, dist_s3_filename)

lambda_client = boto3.client('lambda')

lambda_client.update_function_code(
    FunctionName=LAMBDA_NAME,
    S3Bucket=BUCKET_NAME,
    S3Key=dist_s3_filename
)
