import boto3
import json

def lambda_handler(event, context):
    # Create a low-level service client by the boto3 library
    lambda_client = boto3.client('lambda')
    ecs_client = boto3.client('ecs')

    # Invoke LambdaFunction1
    response1 = lambda_client.invoke(
        FunctionName='readVitalSignData',
        InvocationType='Event'
    )

    # Invoke LambdaFunction2
    response2 = lambda_client.invoke(
        FunctionName='simulateVitalSignData',
        InvocationType='Event'
    )
    
    # Update ECS service
    response3 = ecs_client.update_service(
        cluster='VitalSignInjector',
        service='VitalSignInjectionService',
        desiredCount=1
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Vital sign injection initiated!')
    }
