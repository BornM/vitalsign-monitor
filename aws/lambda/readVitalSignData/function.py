import boto3
import csv
import json
import itertools
from io import StringIO

# Replace these variables with your actual S3 bucket and object key
BUCKET_NAME = "demovitalsignmonitoring"
OBJECT_KEY = "vitals_time_labled_demo.csv"

# Replace this with the actual SQS queue URL
QUEUE_URL = "https://sqs.eu-central-1.amazonaws.com/<account_id>/RealVitalSignInjectionQueue.fifo"

s3 = boto3.client('s3')
sqs = boto3.client('sqs')

# number of rows to be read from file and sent as SQS messages
n = 1200

def lambda_handler(event, context):
    # Download the CSV file from S3 and read its contents
    file_obj = s3.get_object(Bucket=BUCKET_NAME, Key=OBJECT_KEY)
    file_content = file_obj['Body'].read().decode('utf-8')
    csv_reader = csv.reader(StringIO(file_content))
    
    # save file header
    headers = next(csv_reader)
    
    # create dictionary to map column headers to identifiers
    identifier_map = {
        "Time": "time_real",
        "heartrate": "hr_real",         # Heart Rate
        "resprate": "res_real",         # Respiratory Rate
        "o2sat": "o2_real",             # Oxygen Saturation
        "sbp": "sbp_real",              # Systolic Blood Pressure
        "dbp": "dbp_real",              # Diastolic Blood Pressure
        "unstable_in": "hdi_alarm",     # Hemodynamic Instability Alarm
        "unstable": "hdi_state"         # Hemodynamic Instability Status
    }

    # Iterate through the CSV file and send each row as a message to the SQS queue
    count = 0
    for row in itertools.islice(csv_reader, n):
        # store index for message duplication ID
        index = row[0]
        
        # create identifier-value pairs for each row
        row_data = {}
        for i in range(len(row)):
            identifier = identifier_map[headers[i]]
            value = row[i]
            row_data[identifier] = value
        
        # join the identifier-value pairs with commas to create the message body
        message_body = json.dumps(row_data)
        
        response = sqs.send_message(
            QueueUrl=QUEUE_URL, 
            MessageBody=message_body,
            MessageGroupId='real_vitalsigns',
            MessageDeduplicationId=str(index)
        )
        
        count += 1
        # print(f"Message sent: {response['MessageId']} " + message_body)
        

    return {
        'statusCode': 200,
        'body': f'Successfully processed CSV file {OBJECT_KEY} from S3 bucket {BUCKET_NAME}',
        'count': count
    }
