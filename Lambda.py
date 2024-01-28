"""
serializeImageData
"""

import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""

    # Get the s3 address from the Step Function event input
    key = event['s3_key'] ## TODO: fill in
    bucket = event['s3_bucket'] ## TODO: fill in

    # Download the data from s3 to /tmp/image.png
    s3.download_file(bucket, key, '/tmp/image.png') ## TODO: fill in

    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }


"""
classifyImage
"""

import boto3
import json
import base64
# import sagemaker
# from sagemaker.serializers import IdentitySerializer

# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2024-01-28-08-02-05-351" ## TODO: fill in

def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event["image_data"]) ## TODO: fill in

    # Instantiate a Predictor
    # predictor = sagemaker.predictor.Predictor(endpoint_name=ENDPOINT, sagemaker_session=sagemaker.Session()) ## TODO: fill in

    # For this model the IdentitySerializer needs to be "image/png"
    # predictor.serializer = IdentitySerializer("image/png")

    # Make a prediction:
    # inferences = predictor.predict(image) ## TODO: fill in
    
    # We return the data back to the Step Function    
    # event["inferences"] = inferences.decode('utf-8')
    
    # Make a prediction:
    runtime = boto3.Session().client('sagemaker-runtime')
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT, ContentType='image/png',Body=image)
    inferences = json.loads(response['Body'].read().decode('utf-8'))

    # We return the data back to the Step Function
    event["inferences"] = inferences
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }

"""
rejectLowConfidenceInferences
"""

import json

THRESHOLD = 0.93

def lambda_handler(event, context):
    # Get the inferences from the event
    inferences = event.get("inferences", [])  ## TODO: fill in
    
    # Check if any values in any inferences are above THRESHOLD
    meets_threshold = (max(inferences) > THRESHOLD)  ## TODO: fill in
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        return {
            'statusCode': 200,
            'body': event
        }
    else:
        raise Exception("THRESHOLD_CONFIDENCE_NOT_MET")
