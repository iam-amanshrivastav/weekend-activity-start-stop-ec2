# After activity completion, this function stops only the servers which were started by the automation and restored the tags which were changes by the start funtion.


import boto3
import csv
import datetime

# AWS Clients
ec2 = boto3.client('ec2')
s3 = boto3.client('s3')

S3_BUCKET = "weekend-activity-ec2-start-stop-logs"
execution_date = datetime.datetime.now().strftime("%Y-%m-%d")
FINAL_LOG_FILE = f"restored_servers_{execution_date}.csv"
START_LOG_FILE = f"started_servers_{execution_date}.csv"
BACKUP_FILE = f"backup_ec2_state_{execution_date}.csv"

def lambda_handler(event, context):
    stopped_instances = []

    # Step 1: Load Backup & Start Log from S3
    s3.download_file(S3_BUCKET, BACKUP_FILE, f"/tmp/{BACKUP_FILE}")
    s3.download_file(S3_BUCKET, START_LOG_FILE, f"/tmp/{START_LOG_FILE}")

    # Step 2: Read Backup Data (to retrieve original Snoozing values)
    original_state = {}
    with open(f"/tmp/{BACKUP_FILE}", mode="r") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            instance_id, instance_name, instance_state, snoozing_tag = row
            original_state[instance_id] = {"name": instance_name, "state": instance_state, "snoozing": snoozing_tag}

    # Step 3: Read Started Instances Data (to track modified instances)
    modified_instances = {}
    with open(f"/tmp/{START_LOG_FILE}", mode="r") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            instance_id, instance_name, prev_state, prev_snoozing_tag, new_state, new_snoozing_tag = row
            modified_instances[instance_id] = {"name": instance_name, "prev_snoozing": prev_snoozing_tag, "new_snoozing": new_snoozing_tag}

    # Step 4: Retrieve Running Instances & Stop Only Those Started by Automation
    instances = ec2.describe_instances(Filters=[{"Name": "instance-state-name", "Values": ["running"]}])

    if not instances['Reservations']:  
        print("No running instances found.")
        return {"status": "No instances to stop"}

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']

            if instance_id in modified_instances:
                instance_name = modified_instances[instance_id]["name"]
                prev_snoozing = modified_instances[instance_id]["prev_snoozing"]
                new_snoozing = modified_instances[instance_id]["new_snoozing"]
                print(f"Stopping instance: {instance_id} ({instance_name})")
                ec2.stop_instances(InstanceIds=[instance_id])
                stopped_instances.append([instance_id, instance_name, "Running", prev_snoozing, new_snoozing, "Stopped", prev_snoozing])

                # Restore Snoozing tag value to its original state from backup
                ec2.create_tags(Resources=[instance_id], Tags=[{"Key": "Snoozing", "Value": prev_snoozing}])

    # Step 5: Log Stopped Instances in CSV
    if stopped_instances:
        csv_file = f"/tmp/{FINAL_LOG_FILE}"
        with open(csv_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Instance ID", "Instance Name", "Previous State", "Previous Snoozing Tag", "New Snoozing Tag", "Current State", "Restored Snoozing Tag"])
            writer.writerows(stopped_instances)

        s3.upload_file(csv_file, S3_BUCKET, FINAL_LOG_FILE)
        return {"status": "Servers stopped & Snoozing tag reverted", "file": FINAL_LOG_FILE}
    else:
        print("No instances needed to be stopped.")
        return {"status": "No instances needed to be stopped"}

  
