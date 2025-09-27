from googleapiclient.discovery import build
from google.oauth2 import service_account
import streamlit as st

import json

with open("gcp_service_account.json") as f:
    creds_info_from_json = json.load(f)

st.write(creds_info_from_json)


def link_to_file(username):
    """Generates a shareable link to a Google Drive file for a specific user.

    This function searches for a file named 'Overall_{username}.pdf' in Google Drive and returns its shareable link.

    Args:
        username (str): The username associated with the file.

    Returns:
        str: The shareable link to the Google Drive file.
    """
    creds_info = creds_info_from_json

    credentials = service_account.Credentials.from_service_account_info(
        creds_info,
        scopes=['https://www.googleapis.com/auth/drive']
    )

    service = build('drive', 'v3', credentials=credentials)

    file_name = f'Overall_{username}.pdf'
    page_token = None
    while True:
        response = service.files().list(q=f"name='{file_name}'",
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name)',
                                        pageToken=page_token).execute()
        for file in response.get('files', []):
            shareable_link = f"https://drive.google.com/file/d/{file.get('id')}/view?usp=sharing"

        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return shareable_link

def link_to_extra_file(var_name):
    """Generates a shareable link to an extra file in Google Drive for a given variable name.

    This function searches for a file with a modified name based on the provided variable name and returns its shareable link.

    Args:
        var_name (str): The variable name used to construct the file name.

    Returns:
        str: The shareable link to the extra file in Google Drive.
    """
    creds_info = creds_info_from_json

    credentials = service_account.Credentials.from_service_account_info(
        creds_info,
        scopes=['https://www.googleapis.com/auth/drive']
    )

    service = build('drive', 'v3', credentials=credentials)

    file_name = var_name.replace('I_', 'I_F_').replace('pdf', 'zip')
    page_token = None
    while True:
        response = service.files().list(q=f"name='{file_name}'",
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name)',
                                        pageToken=page_token).execute()
        for file in response.get('files', []):
            shareable_link = f"https://drive.google.com/file/d/{file.get('id')}/view?usp=sharing"

        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return shareable_link

def link_to_var(var_name):
    """
    Generates a shareable link to a Google Drive file with the given variable name.

    Args:
        username (str): The username associated with the Google Drive account.
        var_name (str): The name of the variable to generate the link for.

    Returns:
        str: The shareable link to the Google Drive file.
    """

    creds_info = creds_info_from_json
    credentials = service_account.Credentials.from_service_account_info(
        creds_info,
        scopes=['https://www.googleapis.com/auth/drive']
    )

    service = build('drive', 'v3', credentials=credentials)

    file_name = f'{var_name}.pdf'
    page_token = None
    while True:
        response = service.files().list(q=f"name='{file_name}'",
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name)',
                                        pageToken=page_token).execute()
        for file in response.get('files', []):
            shareable_link = f"https://drive.google.com/file/d/{file.get('id')}/view?usp=sharing"

        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return shareable_link


def list_files(username, doc_type='Variant', subject='M_'):
    """
    Lists files from Google Drive that match the given username and subject.

    Args:
        username (str): The username to search for in the file names.
        subject (str): The subject to search for in the file names.

    Returns:
        list: A list of file names that match the given username and subject.
    """
    WHAT_TO_FIND = {
        'Variant': f'name contains "{subject}" and name contains "{username}" and name contains ".pdf"',
        'Homework': f'name contains "Overall" and name contains "{username}" and name contains ".pdf"',
        'Files': f'name contains "I_F_" and name contains "{username}" and name contains ".zip"' 
    }

    creds_info = creds_info_from_json

    credentials = service_account.Credentials.from_service_account_info(
        creds_info,
        scopes=['https://www.googleapis.com/auth/drive']
    )

    service = build('drive', 'v3', credentials=credentials)

    results = service.files().list(pageSize=100, fields="nextPageToken, files(name)", q=WHAT_TO_FIND[doc_type]).execute()

    items = results.get('files', [])

    return [elem['name'] for elem in items]
