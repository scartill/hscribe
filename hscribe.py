from argparse import ArgumentParser
import logging as lg
import random
import time

import requests
import boto3


BUCKET_NAME = 'public.resnick'


def transcribe_and_translate(filename):
    transcribe = boto3.client('transcribe')
    job_name = f'job-{random.randint(0, 1000)}'
    output_key = f'hscribe/{filename}.json'

    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        LanguageCode='he-IL',
        MediaFormat='mp3',
        Media={
            'MediaFileUri': f's3://{BUCKET_NAME}/{filename}'
        },
        OutputBucketName=BUCKET_NAME,
        OutputKey=output_key
    )

    lg.info(f'Started transcription job for {filename}')
    status = 'unknown'

    while True:
        lg.info('Checking job status...')

        response = transcribe.get_transcription_job(
            TranscriptionJobName=job_name
        )

        job = response['TranscriptionJob']
        status = job['TranscriptionJobStatus']

        if status in ['COMPLETED', 'FAILED']:
            break

        time.sleep(5)

    lg.info(f'Transcription job {status.lower()}')

    if status == 'FAILED':
        raise UserWarning('Trascribe job failed')

    results_uri = job['Transcript']['TranscriptFileUri']
    response = requests.get(results_uri)
    results_json = response.json()
    transcript = results_json['results']['transcripts'][0]['transcript']

    lg.info('Printing transcript')
    print(transcript)

    translate = boto3.client('translate')

    response = translate.translate_text(
        Text=transcript,
        SourceLanguageCode='he-IL',
        TargetLanguageCode='en-US'
    )

    return response['TranslatedText']


def process_blob(array):
    s3 = boto3.client('s3')
    filename = f'hscribe/stream_{random.randint(0, 1000)}.mp3'
    s3.put_object(Bucket=BUCKET_NAME, Key=filename, Body=array)
    lg.info(f'Uploaded stream to S3 bucket {BUCKET_NAME}')
    translation = transcribe_and_translate(filename)
    return translation


def main():
    parser = ArgumentParser()
    parser.add_argument('filename', help='File to transcribe.')
    args = parser.parse_args()
    filebase = args.filename.split('\\')[-1]
    s3_key = f'hscribe/{filebase}'
    s3 = boto3.client('s3')
    s3.upload_file(args.filename, BUCKET_NAME, s3_key)
    lg.info(f'Uploaded {args.filename} to S3 bucket {BUCKET_NAME}')
    translation = transcribe_and_translate(s3_key)
    lg.info('Printing translation')
    print(translation)


if __name__ == '__main__':
    lg.basicConfig(level=lg.INFO)
    main()
