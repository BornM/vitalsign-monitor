# Reinvent Vital Sign Monitoring

This repository hosts the resources for a student project, conducted in cooperation between the SRH Berlin and Charité Berlin, aimed at demonstrating use cases for the interoperability of medical devices in the context of vital sign monitoring. A cloud-based prototype integrates a centralized vital sign interface, hemodynamic instability prediction, and an alarm management system. The system relies on recorded and simulated data.

The project leverages cloud-native architecture and AWS cloud and services to bring about novel features to vital sign monitoring and improve patient care in intensive care, anesthesia, and surgeries. 

## Project Objectives

1. Promote interoperability of medical devices in intensive care, anesthesia, and surgeries.
2. Introduce novel features to vital sign monitoring.
3. Utilize cloud-native architecture and AWS services.
4. Showcase a concept for streamlining surgery processes, enhance decision-making, and reduce alarm fatigue for healthcare professionals.

## Use Case

**Integrated Cardiac Surgery Support System**: The use case for this project is to create a cloud-based prototype that showcases potential to improve the cardiac surgery process, enhances patient outcomes, and reduces alarm fatigue.

1. **Centralized vital sign interface for surgeons**: Providing cardiac surgeons with a comprehensive view of real-time data from various monitoring devices.

2. **Predict hemodynamic instability**: Developing a system to continuously analyze real-time vital sign data during cardiac surgery and predict potential complications.

3. **Intelligent and contextual alarm system**: Creating an intelligent alarm system that contextually manages alarms.

## Functional Model

1. **Data tier**: Generates and ingests historic and simulated vital sign data.
2. **Alarm management system tier**: Applies rules and machine learning models to detect critical values and predict hemodynamic instability.
3. **Visualization tier**: Presents data and alarms through a self-hosted Grafana instance connected to an AWS Timestream table.

## Prototype

### Vitalsign dashboard when patient is in a stable state
![Image Alt Text](./prototype/pictures/Stable%20State.png)

### Vitalsign dashboard when hemodynamic instability is predicted (countdown in sec)
![Image Alt Text](./prototype/pictures/Prediction%20Alarm%20Countdown.png)

### Vitalsign dashboard when patient is in an unstable state
![Image Alt Text](./prototype/pictures/Instable%20State.png)

### Anticipated system architecture (not fully implemented)
![Image Alt Text](./prototype/pictures/AWSArchitectureDiagram.png)


## Project Structure

```
.
├── README.md
├── aws
│   ├── cloudformation-template.json
│   ├── ecs
│   │   └── vitalSignInjector
│   │       ├── Dockerfile
│   │       ├── main.py
│   │       └── requirements.txt
│   ├── grafana
│   │   └── JSON model
│   │       └── dashboard.json
│   └── lambda
│       ├── invokeVitalSignInjection
│       │   └── function.py
│       ├── readVitalSignData
│       │   └── function.py
│       └── simulateVitalSignData
│           ├── function.py
│           └── python
├── data
│   ├── data_transform.py
│   ├── vitals_time.csv
│   └── vitals_time_labled_demo.csv
├── prediction_model
│   └── hdi_prediction_model.ipynb
└── prototype
    ├── Project_Presentation.pdf
    └── pictures
        ├── AWSArchitectureDiagram.png
        ├── Instable State.png
        ├── Prediction Alarm Countdown.png
        └── Stable State.png
```

## Setup and Installation
**Note:** The CloudFormation template does not include the AWS Timestream, Lambda and ECS resources. 

1. **AWS CloudFormation**: Launch the CloudFormation stack using the provided `cloudformation-template.json` file in the AWS console. This will set up most of the necessary AWS services.

2. **AWS Timestream**: Create a new database and table in AWS Timestream manually. This is where the vital sign data will be stored and retrieved.

3. **VitalSignInjector Container**: Navigate to the `aws/ecs/vitalSignInjector` directory, and build the Docker container using the provided Dockerfile. Once the container is built, push it to the an AWS ECR repository.

4. **ECS Service**: Create a new ECS cluster and service. Use the VitalSignInjector container for the service. 

5. **Lambda Functions**: Deploy the lambda functions provided in the `aws/lambda` directory.

6. **Grafana Setup**: Use the Grafana EC2 instance and import the provided `dashboard.json` from the `aws/grafana/JSON model` directory. Connect Grafana to the AWS Timestream database that you created earlier. 

**Make sure to adjsut all code artifacts according to your aws infrastructure (e.e. sqs que names and urls) and add the data to the s3 bucket**

### Authors

* Maximilian Bornstädt - Maximilian.Bornstaedt@stud.srh-campus-berlin.de
* Varsha Balaji - Varsha.Balaji@stud.srh-campus-berlin.de
* Nibedita Sahoo - Nibedita.Sahoo@stud.srh-campus-berlin.de
* Prof. Gerrit Tamm - gerrit.tamm@srh.de
* Prof. Philipp Landgraf - philipp.landgraf@charite.de

Thank you for your interest in the 'Reinvent Vital Sign Monitoring' project!
