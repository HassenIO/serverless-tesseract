import urllib
import os
import subprocess
import json
import base64

from cgi import parse_header, parse_multipart
from io import BytesIO

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(SCRIPT_DIR, 'lib')
TESSDATA_DIR = os.path.join(SCRIPT_DIR, 'tessdata')
IMG_TEST = os.path.join(SCRIPT_DIR, 'tmp', 'image.png')


def hello(event, context):
    try:
        # content_type = event['headers']['Content-Type']
        # c_type, c_data = parse_header(content_type)
        # assert c_type == 'multipart/form-data'
        # print(event['body'])
        # form_data = parse_multipart(event['body'], c_data)
        # # BytesIO(event['body'].decode('base64')), c_data)
        # print(form_data)

        # img_base64 = event.get('body')
        # print('-----')
        # print(img_base64)
        # body = event['body']
        # with open(IMG_TEST, "wb+") as f:
        #     f.write(base64.b64decode(body))  # .isascii()

        # imgfilepath = '/tmp/image.png'
        imgfilepath = IMG_TEST
        outputfilepath = '/tmp/result'

        command = 'LD_LIBRARY_PATH={} TESSDATA_PREFIX={} {}/tesseract {} {} --oem 1 -l fra'.format(
            LIB_DIR,
            TESSDATA_DIR,
            SCRIPT_DIR,
            imgfilepath,
            outputfilepath,
        )

        try:
            print(command)
            subprocess.check_output(command, shell=True)
            output = subprocess.check_output(
                'cat {}.txt'.format(outputfilepath), shell=True)
            print(output)
            subprocess.check_output(
                'rm {}.txt'.format(outputfilepath), shell=True)

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
