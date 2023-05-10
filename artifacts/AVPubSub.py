from datetime import datetime
import time
import traceback
import json
import boto3
import botocore
import sys
import os

import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    IoTCoreMessage,
    QOS,
    SubscribeToIoTCoreRequest,
    PublishToIoTCoreRequest
)

from cv2 import VideoCapture, imshow, imwrite, waitKey, destroyWindow

TIMEOUT = 10
BUCKET = sys.argv[1]
REQUEST_TOPIC = sys.argv[2]
RESPONSE_TOPIC = sys.argv[3]
THING_NAME = os.getenv('AWS_IOT_THING_NAME')

ipc_client = awsiot.greengrasscoreipc.connect()


def respond(event):
    # Capture image
    take_picture()
    image_url = upload_file(BUCKET, event.message.payload)
    response_message = {
        "timestamp": int(round(time.time() * 1000)),
        "image": image_url
    }

    # Publish to our topic
    response = PublishToIoTCoreRequest()
    response.topic_name = RESPONSE_TOPIC
    response.payload = bytes(json.dumps(response_message), "utf-8")
    response.qos = QOS.AT_MOST_ONCE
    response_op = ipc_client.new_publish_to_iot_core()
    response_op.activate(response)


def take_picture():
    cam_port = 0
    cam = VideoCapture(cam_port)
    
    # reading the input using the camera
    result, image = cam.read()
    
    if result:  
        # saving image in local storage
        imwrite("photo.png", image)  
    else:
        print("No image detected. Please! try again")

def upload_file(bucket, pic_filepath):
    # Upload the file to S3.  Note that I'm setting a PUBLIC-READ ACL just for ease of troubleshooting.
    # You probably would not want to do this unless it's truly a public endeavour.
    try:
        s3_client = boto3.client('s3')
        pic_filepath = "photo.png"

        filename = RESPONSE_TOPIC + '/' + THING_NAME + '/' + \
            str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S')) + '.jpg'
        s3_client.upload_file(pic_filepath, bucket, filename,
                              ExtraArgs={'ACL': 'public-read'})
        url = 'https://{}.s3.amazonaws.com/{}'.format(BUCKET, filename)

    except botocore.exceptions.ClientError as e:
        url = e.response

    finally:
        return url


class StreamHandler(client.SubscribeToIoTCoreStreamHandler):
    def __init__(self):
        super().__init__()

    def on_stream_event(self, event: IoTCoreMessage) -> None:
        try:
            respond(event)
        except:
            traceback.print_exc()

    def on_stream_error(self, error: Exception) -> bool:
        # Handle error.
        return True  # Return True to close stream, False to keep stream open.

    def on_stream_closed(self) -> None:
        # Handle close.
        pass

# Setup the MQTT Subscription
request = SubscribeToIoTCoreRequest()
request.topic_name = REQUEST_TOPIC
request.qos = QOS.AT_MOST_ONCE
handler = StreamHandler()
operation = ipc_client.new_subscribe_to_iot_core(handler)
future = operation.activate(request)
future.result(TIMEOUT)

# Keep the main thread alive, or the process will exit.
while True:
    time.sleep(10)

# To stop subscribing, close the operation stream.
operation.close()
