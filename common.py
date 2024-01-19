import sys
sys.path.append('.')
sys.path.append('..')
from constants import *

import os
import re
import requests
from datetime import datetime, time, timedelta
import uuid
import json
import openai
from tenacity import retry, wait_random_exponential, stop_after_attempt
from azure.storage.blob import BlobClient, ContentSettings, ContainerClient

# Helper function to upload file to blobl storage
def upload_file_to_azure(path_local, path_remote, mime_type, datalake_account_container, datalake_connection_string, remove_local_file_when_done = True):
        # Upload the file to the data lake in the Azure Storage Account
        blob = BlobClient.from_connection_string(conn_str=datalake_connection_string, container_name=datalake_account_container, blob_name=path_remote)
        image_content_setting = ContentSettings(content_type=mime_type)

        # Upload the file to the data lake
        with open(path_local,"rb") as data:
            blob.upload_blob(data,overwrite=True,content_settings=image_content_setting)

        if remove_local_file_when_done:
            # Delete the temporary file
            os.remove(path_local)

# Helper function to upload json to azure blob storage
def upload_json_to_azure(serializable_object, path_remote, datalake_account_container, datalake_connection_string):
    unique_identifier = uuid.uuid4().hex # randon string to uniquely identify the temporary file
    file_name = f'{unique_identifier}.json'

    # Create temporary file with the mentions data
    with open(file_name, 'w') as f:
        json.dump(serializable_object, f)
    
    upload_file_to_azure(file_name, path_remote, 'application/json', datalake_account_container, datalake_connection_string)

# Helper function to list files in azure blob storage
def list_files_in_azure_container(datalake_account_container, datalake_connection_string, folder_path = ''):
    container_client = ContainerClient.from_connection_string(conn_str=datalake_connection_string, container_name=datalake_account_container)
    blob_list = container_client.list_blobs(name_starts_with=folder_path)

    # Add url to blob object and turn iterator into list
    file_list = []
    for blob in blob_list:
        blob.url = f'https://{DATALAKE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{datalake_account_container}/{blob.name}'
        file_list.append(blob)

    return file_list

# Helper function to move file in azure blob storage from one folder to another
def move_file_in_azure_container(datalake_account_container, datalake_connection_string, source_path, destination_path):
    container_client = ContainerClient.from_connection_string(conn_str=datalake_connection_string, container_name=datalake_account_container)
    # retrieve original blobl and its properties
    original_blob = container_client.get_blob_client(source_path)
    original_blob_properties = original_blob.get_blob_properties()
    original_blob_url = f'https://{DATALAKE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{datalake_account_container}/{original_blob_properties.name}'

    # create new blob and upload the original blob to it
    new_blob = BlobClient.from_connection_string(conn_str=datalake_connection_string, container_name=datalake_account_container, blob_name=destination_path)
    new_blob.upload_blob_from_url(original_blob_url)

    # delete original blob
    original_blob.delete_blob()


# Helper function to store log file to azure blob storage
def log_error(traceback, source_file):
    current_datetime = datetime.now().isoformat()
    log_dict = {}
    log_dict['datetime'] = current_datetime
    log_dict['traceback'] = traceback
    log_dict['file'] = source_file
    unique_log_identifier = uuid.uuid4().hex # randon string to uniquely identify the log file
    log_file_name = os.path.basename(source_file).split('.')[0] + f'_{unique_log_identifier}.json'
    upload_json_to_azure(log_dict, log_file_name, DATALAKE_LOGS_ACCOUNT_CONTAINER, DATALAKE_CONNECTION_STRING)

# Helper function to translate text
def translate(source_language, target_language, text):
    params = {
        'api-version': '3.0',
        'from': source_language,
        'to': [target_language]
    }

    trace_id = str(uuid.uuid4())
    headers = {
        'Ocp-Apim-Subscription-Key': AZURE_TRANSLATION_KEY,
        'Ocp-Apim-Subscription-Region': AZURE_TRANSLATION_LOCATION,
        'Content-type': 'application/json',
        'X-ClientTraceId': trace_id
    }

    body = [{
        'text': text
    }]

    request = requests.post(AZURE_TRANSLATION_ENDPOINT, params=params, headers=headers, json=body)
    response = request.json()

    translation_results = json.dumps(response, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': '))
    
    # If the response contains an error, return False
    if 'error' in response:
        return False

    # If the response contains a translation, return it
    if len(response) > 0 and 'translations' in response[0]:
        for translation in response[0]['translations']:
            return translation['text']
    else:
        return False

# Helper function to make prompts request against the OpenAI API with a retry mechanism
@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, functions=None, function_call=None, model=OPENAI_DEFAULT_GPT_MODEL, api_key=OPENAI_API_KEY):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key,
    }
    json_data = {"model": model, "messages": messages}
    if functions is not None:
        json_data.update({"functions": functions})
    if function_call is not None:
        json_data.update({"function_call": function_call})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        print(f"Response: {response.text}")
        raise

def clear_llm_response(response):
    # Remove any trailing spaces or newlines, also make all the text lowercase
    fixed_response = response.strip().lower()
    # Remove any non-alphanumeric characters like punctiation
    fixed_response = re.sub(r'[^a-zA-Z0-9_ ]', '', fixed_response)
    return fixed_response

def request_openai_moderation(text, api_key=OPENAI_API_KEY):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key,
    }
    json_data = {"input": "Sample text goes here"}
    response = requests.post(
        "https://api.openai.com/v1/moderations",
        headers=headers,
        json=json_data,
        timeout=30
    )
    response.raise_for_status()
    return response.json()

def check_for_content_violating_policies(text, api_key=OPENAI_API_KEY):
    response = request_openai_moderation(text, api_key)
    if 'results' in response:
        for result in response['results']:
            if 'flagged' in result and result['flagged']:
                return True
    return False