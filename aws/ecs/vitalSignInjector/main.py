import boto3
import time
import json
from collections import OrderedDict

REGION = "eu-central-1"

# Replace with your actual SQS queue URLs
SIMULATED_QUEUE_URL = 'https://sqs.eu-central-1.amazonaws.com/<account_id>/SimulatedVitalSignInjectionQueue.fifo'
REAL_QUEUE_URL = 'https://sqs.eu-central-1.amazonaws.com/<account_id>/RealVitalSignInjectionQueue.fifo'

# Replace with your actual Timestream database and table names
TIMESTREAM_DATABASE_NAME = "monitoring"
TIMESTREAM_TABLE_NAME = "vitalsMon"

# Replace this with the actual Kinesis Data Stream name
KINESIS_STREAM_NAME = "VitalSignStream"

sqs = boto3.client('sqs', region_name=REGION)
timestream_write = boto3.client('timestream-write', region_name=REGION)
kinesis = boto3.client('kinesis', region_name=REGION)


def convert_to_timestream_records(data, source_type):
    # Convert the data into a list of Timestream record dictionaries
    records = []
    for key, value in data.items():
        record = {
            'MeasureName': key,
            'MeasureValue': str(value),
            'MeasureValueType': 'DOUBLE',  # or 'BIGINT', 'VARCHAR', etc. based on the type of 'value'
            'Time': str(int(time.time() * 1000)),  # current time in milliseconds
            'Dimensions': [{'Name': 'Source', 'Value': source_type}],
        }
        records.append(record)
    return records

def main():
    while True:
        # Read one message from each queue
        sim_response = sqs.receive_message(
            QueueUrl=SIMULATED_QUEUE_URL,
            MessageAttributeNames=['All'],
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10
        )
        if 'Messages' in sim_response:
            print("sim-vital-id: " + sim_response['Messages'][0]['MessageId'])
        else:
            print("no simulated vitals")
        
        real_response = sqs.receive_message(
            QueueUrl=REAL_QUEUE_URL,
            MessageAttributeNames=['All'],
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10
        )
        if 'Messages' in real_response:
            print("real-vital-id: " + real_response['Messages'][0]['MessageId'])
        else:
            print("no real vitals")

        # Get the message bodies
        sim_message = sim_response['Messages'][0]['Body'] if 'Messages' in sim_response else None
        real_message = real_response['Messages'][0]['Body'] if 'Messages' in real_response else None

        # Deserialize the JSON messages
        sim_data = json.loads(sim_message) if sim_message else None
        real_data = json.loads(real_message) if real_message else None
        if real_data:
            print('Timestamp: ' + str(real_data['time_real']))

         # Append 'temp_sim' and 'ph_sim' from sim_data to real_data
        if sim_data and real_data:
            data = real_data
            if 'temp_sim' in sim_data:
                data['temp_sim'] = sim_data['temp_sim']
            if 'ph_sim' in sim_data:
                data['ph_sim'] = sim_data['ph_sim']
            if 'temp_sim' in sim_data and 'ph_sim' in sim_data:
                data['temp_sim'] = sim_data['temp_sim']
                data['ph_sim'] = sim_data['ph_sim']
                new_order = ['time_real', 'hr_real', 'res_real', 'o2_real', 'sbp_real', 'dbp_real', 'temp_sim', 'ph_sim', 'hdi_state', 'hdi_alarm']
                data = OrderedDict((k, data[k]) for k in new_order)

            print(json.dumps(data, indent=4))

            # Write the records to the Timestream table
            records = convert_to_timestream_records(data, 'vitals')
            response_ts = timestream_write.write_records(DatabaseName=TIMESTREAM_DATABASE_NAME, TableName=TIMESTREAM_TABLE_NAME, Records=records)
            print("Ingested records: " + str(response_ts['RecordsIngested']['Total']))

            # Write records to Kinesis strean
            response = kinesis.put_record(
                StreamName=KINESIS_STREAM_NAME,
                Data=json.dumps(data, indent=4),
                PartitionKey="vital-signs"
            )
            print("Kinesis injection: " + response['ShardId'])


        # Delete the processed messages from the queues
        if 'Messages' in sim_response:
            sqs.delete_message(QueueUrl=SIMULATED_QUEUE_URL, ReceiptHandle=sim_response['Messages'][0]['ReceiptHandle'])
        if 'Messages' in real_response:
            sqs.delete_message(QueueUrl=REAL_QUEUE_URL, ReceiptHandle=real_response['Messages'][0]['ReceiptHandle'])

        time.sleep(1)

if __name__ == "__main__":
    main()
