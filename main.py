import os
import requests
import json
import xml.etree.ElementTree as ET

login_url = 'https://transkribus.eu/TrpServer/rest/auth/login'
create_upload_url = 'https://transkribus.eu/TrpServer/rest/uploads'

# enter collection id you would like to add documents to and your transkribus account details
collection_id = "COLLECTION_ID"
username = "USER_EMAIL"
password = "USER_PWD"

def login_transkribus(username, password):
    response = requests.post(login_url, data={'user': username, 'pw': password})
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        session_id = root.find('sessionId').text
        return session_id
    else:
        raise Exception(f"Login failed: {response.status_code} - {response.text}")
    

def create_upload(session_id, collection_id, doc_name, pages):
    headers = {'Cookie': f"JSESSIONID={session_id}", 'Content-Type': 'application/json'}
    body = {
        "md": {
            "title": doc_name # name the document is going to be called in the collection
        },
        "pageList": {"pages": pages}
    }
    #print(json.dumps(body, indent=4))  # Debug print
    response = requests.post(f'{create_upload_url}?collId={collection_id}', headers=headers, data=json.dumps(body))
    if response.status_code == 200:
        #print("Response Status Code:", response.status_code) # Debug print
        #print("Response Content:", response.text) # Debug print
        root = ET.fromstring(response.text)
        upload_id = root.find('uploadId').text
        return upload_id
    else:
        raise Exception(f"Failed to create upload: {response.status_code}, {response.text}")


def upload_page(session_id, upload_id, page_data, image_path, xml_path=None):
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
    for dirpath, _, filenames in os.walk(base_dir):

        if dirpath == base_dir:
            continue

        doc_name = os.path.basename(dirpath)
        print(f"Processing directory {doc_name}...")

        pages = []
        #print(filenames)
      
        # assuming sortable filenames
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

            pages.sort(key=lambda x: x['pageNr'])
            #print(pages)
            for page in pages:
                image_path = os.path.join(dirpath, page['fileName'])
                xml_path = os.path.join(dirpath, "page", page['pageXmlName'])
                upload_page(session_id, upload_id, page, image_path, xml_path)


if __name__ == "__main__":

    base_dir = 'PATH/TO/DIRECTORY'
    process_directory(base_dir)
