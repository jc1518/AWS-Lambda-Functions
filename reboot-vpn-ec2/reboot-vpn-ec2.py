# VPN ec2 self-healing lambda function
# Version 1.0 16/01/2017 by Jackie Chen
from __future__ import print_function

import time
import boto3

region = 'ap-southeast-2'

instances = {
    "vpn01": "i-a2XXXXXX",
    "vpn02": "i-34XXXXXX",
    "vpn03": "i-f8XXXXXX"
}


def find_instance(alarm):
    for key, value in instances.items():
        if key in alarm:
            print("instance_id is: " + value)
            return value


def instance_action(instance_id):
    ec2 = boto3.resource('ec2', region_name=region)
    instance = ec2.Instance(instance_id)
    instance_status = instance.state['Name']
    while instance_status == 'stopping':
        print("Instance is stopping...")
        time.sleep(5)
        instance_status = instance.state['Name']
    if instance_status == 'running':
        print("Rebooting " + instance_id)
        instance.reboot()
    elif instance_status == 'stopped':
        print("Starting " + instance_id)
        instance.start()
    else:
        print("Instance status is: " + instance_status)


def lambda_handler(event, context):
    message = event['Records'][0]['Sns']['Message']
    instance_id = find_instance(str(message))
    instance_action(instance_id)




