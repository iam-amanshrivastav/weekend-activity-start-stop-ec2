# store EC2 instance states & Snoozing tags in S3 bucket.
# This will be our first lambda funtion.

import boto3
import csv
import datetime

# AWS Clients
ec2 = boto3.client('ec2')
s3 = boto3.client('s3')

S3_BUCKET = "weekend-activity-ec2-start-stop-logs"
execution_date = datetime.datetime.now().strftime("%Y-%m-%d")
BACKUP_FILE = f"backup_ec2_state_{execution_date}.csv"

def lambda_handler(event, context):
    instances_data = []

    instances = ec2.describe_instances()

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_state = instance['State']['Name']
            tags = {t['Key']: t['Value'] for t in instance.get('Tags', [])}
            snoozing_status = tags.get("Snoozing", "Not Found")
            instance_name = tags.get("Name", "Unknown")

            instances_data.append([instance_id, instance_name, instance_state, snoozing_status])

    csv_file = f"/tmp/{BACKUP_FILE}"
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Instance ID", "Instance Name", "Instance State", "Snoozing Tag"])
        writer.writerows(instances_data)

    s3.upload_file(csv_file, S3_BUCKET, BACKUP_FILE)

    return {"status": "Backup completed", "file": BACKUP_FILE}
