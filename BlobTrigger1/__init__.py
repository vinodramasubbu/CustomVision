import json
import logging

import azure.functions as func
import os

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
import requests

from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, generate_account_sas, ResourceTypes, AccountSasPermissions

AZURE_ACC_NAME = 'computervisionblobinstg'
AZURE_PRIMARY_KEY = 'xxxxxx'
AZURE_CONTAINER = 'imagefiles'


# Add your Computer Vision subscription key and endpoint to your environment variables.
subscription_key = 'e8ff37d6d524429ba65f465d4af9fd58'
#endpoint = 'https://azcompvisn2.cognitiveservices.azure.com' + "/vision/v2.1/analyze"
endpoint = 'https://azcompvisn2.cognitiveservices.azure.com' + '/vision/v3.2/describe'


# Request headers.
headers = {
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': subscription_key,
}

# Request parameters. All of them are optional.
params = {
    'visualFeatures': 'Categories,Description,Color',
    'language': 'en',
}

#def main(myblob: func.InputStream, outputDocument: func.Out[func.Document]) -> func.HttpResponse:
def main(myblob: func.InputStream, outputDocument: func.Out[func.Document]):
#def main(myblob: func.InputStream, outputDocument: func.DocumentList) -> func.Document:
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")
    text1=os.path.basename(myblob.name)
    #name1=(os.path.splitext(text1)[0]) +'.csv'
    logging.info(text1)

    AZURE_BLOB=text1

    sas_token = generate_account_sas(
        account_name=AZURE_ACC_NAME,
        account_key=AZURE_PRIMARY_KEY,
        resource_types=ResourceTypes(object=True),
        permission=AccountSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)
    )

    sas_url={'url': 'https://'+AZURE_ACC_NAME+'.blob.core.windows.net/'+AZURE_CONTAINER+'/'+AZURE_BLOB+'?'+sas_token}
    logging.info('https://'+AZURE_ACC_NAME+'.blob.core.windows.net/'+AZURE_CONTAINER+'/'+AZURE_BLOB+'?'+sas_token)

    response = requests.post(endpoint, headers=headers, params=params, json=sas_url)
    response.raise_for_status()
    #logging.info(json.dumps(response.json()))
    #logging.info(json.loads(response.json()))
    describe = response.json()
    logging.info(describe['description']['captions'][0]['text']) 
    logging.info(describe['description']['captions'][0]['confidence']) 
    logging.info(describe['requestId']) 
    image_desc = dict({'description': describe['description']['captions'][0]['text'], 'confidence': describe['description']['captions'][0]['confidence'] , 'requestid': describe['requestId'], 'imagename': text1 })
    logging.info(image_desc)

    #outputDocument.set(func.Document.from_json(json.dumps(image_desc)))
    outputDocument.set(func.Document.from_json(json.dumps(image_desc)))
    #return str(describe)

    #return json.dumps(image_desc)