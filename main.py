import os
import requests
import json
import xml.etree.ElementTree as ET

login_url = 'https://transkribus.eu/TrpServer/rest/auth/login'
create_upload_url = 'https://transkribus.eu/TrpServer/rest/uploads'

# change these
collection_id = "COLLECTION_ID"
username = "USER_EMAIL"
password = "USER_PWD"


def login_transkribus(username, password):
    """
    Logs in to the Transkribus API using the provided credentials.

    Args:
        username (str): Your Transkribus account username (email).
        password (str): Your Transkribus account password.

    Returns:
        str: The session ID upon successful login.

    Raises:
        Exception: If the login fails, an exception is raised with the error details.
    """
    response = requests.post(login_url, data={'user': username, 'pw': password})
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        session_id = root.find('sessionId').text
        return session_id
    else:
        raise Exception(f"Login failed: {response.status_code} - {response.text}")


def create_upload(session_id, collection_id, doc_name, pages):
    """
    Creates a new upload in the specified Transkribus collection.

    Args:
        session_id (str): The session ID from the login.
        collection_id (str): The ID of the collection to upload the document to.
        doc_name (str): The name of the document.
        pages (list): A list of pages (image files and metadata) to be uploaded.

    Returns:
        str: The ID of the created upload.

    Raises:
        Exception: If the upload creation fails, an exception is raised with the error details.
    """
    headers = {'Cookie': f"JSESSIONID={session_id}", 'Content-Type': 'application/json'}
    body = {
        "md": {
            "title": doc_name
        },
        "pageList": {"pages": pages}
    }

    response = requests.post(f'{create_upload_url}?collId={collection_id}', headers=headers, data=json.dumps(body))
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        upload_id = root.find('uploadId').text
        return upload_id
    else:
        raise Exception(f"Failed to create upload: {response.status_code}, {response.text}")


def upload_page(session_id, upload_id, page_data, image_path, xml_path=None):
    """
    Uploads a single page (image and optional XML metadata) to the created upload.

    Args:
        session_id (str): The session ID from the login.
        upload_id (str): The ID of the created upload.
        page_data (dict): Metadata about the page being uploaded, including the filename and page number.
        image_path (str): The path to the image file.
        xml_path (str, optional): The path to the XML file, if available.

    Raises:
        Exception: If the upload fails, an error message is printed.
    """
    headers = {'Cookie': f"JSESSIONID={session_id}"}
    files = {'img': (page_data['fileName'], open(image_path, 'rb'), 'application/octet-stream')}
    
    if xml_path and os.path.exists(xml_path):
        files['xml'] = (page_data['pageXmlName'], open(xml_path, 'rb'), 'application/octet-stream')
    else:
        print(f"XML file not found: {xml_path}")
        return

    response = requests.put(f'https://transkribus.eu/TrpServer/rest/uploads/{upload_id}', headers=headers, files=files)

    if response.status_code == 200:
        print(f"Page {page_data['pageNr']} uploaded successfully.")
    else:
        print(f"Failed to upload page {page_data['pageNr']}: {response.status_code}, {response.text}")


def process_directory(base_dir):
    """
    Processes a directory of documents and uploads their pages to Transkribus.

    Args:
        base_dir (str): The base directory containing documents to be uploaded.

    Directory Structure:
        base_dir/
        └── document_name/
            ├── image1.jpg
            ├── image2.jpg
            └── page/
                ├── image1.xml
                └── image2.xml
    """
    for dirpath, _, filenames in os.walk(base_dir):
        if dirpath == base_dir:
            continue

        doc_name = os.path.basename(dirpath)
        print(f"Processing directory {doc_name}...")

        pages = []

        # Sort filenames to ensure proper page order
        sorted_filenames = sorted((filename for filename in filenames if not filename.endswith('.done')))

        for filename in sorted_filenames:
            if filename.lower().endswith('.jpg'):
                base_filename = os.path.splitext(filename)[0]

                # Define paths for image and XML files
                image_path = os.path.join(dirpath, filename)
                xml_path = os.path.join(dirpath, "page", f"{base_filename}.xml")

                page_data = {
                    "fileName": filename,
                    "pageNr": len(pages) + 1,
                    "pageXmlName": f"{base_filename}.xml"
                }
                pages.append(page_data)

        if pages:
            session_id = login_transkribus(username, password)
            upload_id = create_upload(session_id, collection_id, doc_name, pages)

            for page in pages:
                image_path = os.path.join(dirpath, page['fileName'])
                xml_path = os.path.join(dirpath, "page", page['pageXmlName'])
                upload_page(session_id, upload_id, page, image_path, xml_path)


if __name__ == "__main__":
    base_dir = 'PATH/TO/DIRECTORY'
    process_directory(base_dir)
