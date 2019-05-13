from urllib.parse import urlparse
import os
import subprocess
import json
import boto3

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(SCRIPT_DIR, 'lib')
TESSDATA_DIR = os.path.join(SCRIPT_DIR, 'tessdata')
TMP_IMAGE = '/tmp/image.png'
OUTPUT_BASE = '/tmp/result'
OUTPUT_FILE = OUTPUT_BASE + '.txt'
LANG = 'fra'


s3 = boto3.client('s3')


def run(event, context):
    print(event['Records'][0]['s3'])
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urlparse(event['Records'][0]['s3']['object']['key']).path
    print("Bucket: " + bucket)
    print("Key: " + key)
    export_file = key + '.txt'  # Just add .txt at the end of original file as export

    try:
        print('Downloading {} into {}'.format(key, TMP_IMAGE))
        s3.download_file(bucket, key, TMP_IMAGE)

        command = 'LD_LIBRARY_PATH={} TESSDATA_PREFIX={} {}/tesseract {} {} --oem 1 -l {}'.format(
            LIB_DIR,
            TESSDATA_DIR,
            SCRIPT_DIR,
            TMP_IMAGE,
            OUTPUT_BASE,
            LANG
        )
        print(command)

        try:
            subprocess.check_output(command, shell=True)
            output = subprocess.check_output(
                'cat {}'.format(OUTPUT_FILE), shell=True)
            print(output)  # Will print Tesseract engine and Leptonica version

            s3.upload_file(OUTPUT_FILE, bucket, export_file)
            subprocess.check_output(
                'rm {}'.format(OUTPUT_FILE), shell=True)

            body = {
                "output": output.decode("utf-8")
            }

            response = {
                "statusCode": 200,
                "body": json.dumps(body)
            }

            return response

        except subprocess.CalledProcessError as e:
            print(e.output)

    except Exception as e:
        print(e)
        raise e
