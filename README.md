# simple-iot-project
A simple project that demonstrates on how to setup a simple IoT application using AWS IoT core, AWS Greengrass.

Below is the high level architecture.



Requirements:
1. A Virtual machine. (Host computer can also be used but VM is preferred)
2. AWS CLI
3. Python runtime
4. Laptop with webcam
5. Install the Oracle extension pack to attach the host webcam to VM:


Steps to setup and run the project
1. Create a s3 bucket.
Copy the artificats (Python code) to the s3 bucket

aws s3 cp  AVPubSub.py s3://autonomous-vehicle-iot-proj-bucket/artifacts/AVPubSub.py

2. Create a AWS user.
    av-edge-server-management-user

    Create Access key, secret key for the user and export them as env vars in the VM.

3. Create and attach policy to the user.

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogStreams",
                "s3:GetBucketLocation",
                "greengrass:*",
                "iot:*",
                "s3:*",
                "iam:*"
            ],
            "Resource": "*"
        }
    ]
}
```


4. Add a new core device in AWS IoT Core.
    Follow the instrcution 
    Core-device-name: AV_Edge_Server
    Create a new group or reuse existing group.

A new IAM policy will be created once the greengrass is installed on the VM
Make sure to update that policy by giving access to s3 bucket creted. Read access


5. Create new component:
    The receipe can be found at this location.

5. Create new Deployment:
    name: AV_Edge_Server_Deployment
    Mention the Core device added in previous step.
    Select components:
        AV_PubSub
        aws.greengrass.nucleus
        aws.greengrass.Cli

    The code from the s3 bucket will be deployed to the edge server

    Run below command in the VM to check logs 
    sudo tail -F  /greengrass/v2/logs/AV_PubSub.log

