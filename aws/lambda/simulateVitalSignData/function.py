import random as rand
import pandas as pd
import boto3

# set parameters for vital sign variables, L(min) and H(max)range:
start = 0
tempL, tempH = 36, 39
hRateL, hRateH = 55, 100
pulseL, pulseH = 55, 100
bpSeq = (120, 121)
respRateL, respRateH = 11, 17
oxySatL, oxySatH = 93, 100
phL, phH = 7.1, 7.6

n = 101

# create function to generate data frame from random data:
def myHealthCare(n):
    # create the vital signs data:
    rand.seed(109)
    tStamp = [i for i in range(start, start + n, 1)]
    temp = [rand.randint(tempL, tempH) for _ in range(n)]
    hRate = [rand.randint(hRateL, hRateH) for _ in range(n)]
    pulse = [rand.randint(pulseL, pulseH) for _ in range(n)]
    bp = [rand.choice(bpSeq) for _ in range(n)]
    respRate = [rand.randint(respRateL, respRateH) for _ in range(n)]
    oxySat = [rand.randint(oxySatL, oxySatH) for _ in range(n)]
    ph = [round(rand.uniform(phL, phH), 1) for _ in range(n)]

    # create data frame from dictionary
    data = {"Timestamp": tStamp,
            "Temperature": temp,
            "Heart Rate": hRate,
            "Pulse": pulse,
            "Blood Pressure": bp,
            "Respiratory Rate": respRate,
            "Oxygen Saturation": oxySat,
            "pH": ph}
    myHealthDf = pd.DataFrame(data)
    # set index to be the same as the time stamp value
    recordIndex = pd.Index([i for i in range(101, 101 + n, 1)])
    myHealthDf = myHealthDf.set_index(recordIndex)
    
    return myHealthDf
    
# create dictionary to map column headers to identifiers
identifier_map = {
    "Timestamp": "time_sim",
    "Temperature": "temp_sim",
    "Heart Rate": "hr_sim",
    "Pulse": "pulse_sim",
    "Blood Pressure": "bp_sim",
    "Respiratory Rate": "res_sim",
    "Oxygen Saturation": "o2_sim",
    "pH": "ph_sim"
}

# create data set
vitalSignData = myHealthCare(n)

# create an SQS client
sqs = boto3.client('sqs')
queue_url = 'https://sqs.eu-central-1.amazonaws.com/<account_id>/SimulatedVitalSignInjectionQueue.fifo'



for index, row in vitalSignData.iloc[1:].iterrows():
    # create identifier-value pairs for each row
    id_values = []
    for i in range(len(row)):
        identifier = identifier_map[vitalSignData.columns[i]]
        value = row[i]
        id_values.append(f"{identifier}:{value}")
    
    # join the identifier-value pairs with commas to create the message body
    message_body = ','.join(id_values)
    
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body
    )
    
    print(f"Message sent: {response['MessageId']}")
