# simple-iot-project
A simple project that demonstrates how to setup an IoT application using AWS IoT core and AWS Greengrass.

Below is the high level architecture.

![component-diagram](/images/components.png)


## Requirements:
1. A Virtual machine with access to a webcam. (Host computer can also be used but VM is preferred)
with following tools installed
    1. AWS CLI
    2. Python runtime

2. AWS Account


If you are using an Oracle Virual box to create VM then chekout this article which explains how to connect host webcam to VM.

## Steps
### Create AWS resources 
1. Create a s3 bucket.
    bucket name: autonomous-vehicle-iot-proj-bucket
    bucket configuration: Provide public access to the bucket.

Copy the artificats (Python code) to the s3 bucket

aws s3 cp  AVPubSub.py s3://autonomous-vehicle-iot-proj-bucket/artifacts/AVPubSub.py


2. Create an IAM policy with the below permissions.
Policy-name: greengrass-access-policy

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

3. Create an IAM user.
    username: av-edge-server-management-user
    Policy: greengrass-access-policy
    
    Create Access key, secret key for the user and export them as environment variables in the VM.

### VM Setup
Install python and AWS CLI tool.
Export the AWS ACCESS KEY and SECRET KEY that was created in earlier steps.

### AWS Greengrass setup
Go to AWS IOT Service: https://us-east-1.console.aws.amazon.com/iot/home?region=us-east-1#/home

Go to core devices section which is under Manage -> GreenGrass Devices 

1. Add a new core device in AWS IoT Core.
    Core-device-name: AV_Edge_Server.
    Create a new group or reuse existing group.

    Follow the instrcutions mentioned in the wizard.

Once this step is completed, you should see a new core device in the AWS.

add image here

A new IAM policy also will be created once the greengrass is installed on the VM
Make sure to update that policy by giving access to s3 bucket (autonomous-vehicle-iot-proj-bucket) that was created.


5. Create new component:
    The receipe JSON can be found at this location.

5. Create new Deployment:
    name: AV_Edge_Server_Deployment
    Mention the Core device added in previous step.
    Select components:
        AV_PubSub
        aws.greengrass.nucleus
        aws.greengrass.Cli

    The code from the s3 bucket (autonomous-vehicle-iot-proj-bucket) will be deployed to the edge server.

    
## Debugging steps:
Run below command in the VM to check logs 
```
sudo tail -F  /greengrass/v2/logs/AV_PubSub.log
```

If Camera is not accessible to the python application, it might be user permission issue. Run the below command to provide access
```
sudo usermod -a -G video ggc_user 
```
## Testing:
AWS IoT Core platform provides a MQTT Test client which is available under Test section.


https://github.com/SagarTrimukhe/simple-iot-project/assets/46806187/e58f31d6-32d0-4e43-a178-d304e5064517

