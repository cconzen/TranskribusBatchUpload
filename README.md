# Transkribus Document Uploader

This Python script automates the process of uploading multiple documents with image and xml files to a Transkribus collection using Transkribus' REST API. It is tailored to mass uploading the results of running the  [Loghi](https://github.com/knaw-huc/loghi) pipeline.

## Requirements

- Python 3.11
- `requests` library

You can install `requests` using pip:

```
pip install requests
```

## Setup

Clone this repository:
```
git clone https://github.com/cconzen/TranskribusBatchUpload.git
```
Navigate to the project directory:
```
cd TranskribusBatchUpload
```
Edit `main.py` to include your Transkribus account details and the ID of the destination collection:
```
collection_id = "YOUR_COLLECTION_ID"
username = "YOUR_EMAIL"
password = "YOUR_PASSWORD"
```
Set the base directory for processing documents:
```
base_dir = 'PATH/TO/DIRECTORY'
```

## Usage
Run the script by executing the following command:

```
python main.py
```

The script will:

- Log in to your Transkribus account.
- Process the specified directory and its subdirectories to find image files and their corresponding XML files.
- Create a new job for each directory, uploading it as a document in your Transkribus collection.

## Directory Structure
The directory you process should follow this structure:

```
base_dir/
│
└───document_name/
    │
    ├───page001.jpg
    ├───page002.jpg
    ├───page/
        ├── page001.xml
        └── page002.xml
```

- _document_name_: The name of the directory will be used as the document name in Transkribus.
- _image1.jpg, image2.jpg_: Image files representing pages of the document.
- _image1.xml, image2.xml_: pageXML files.

### Notes
- Ensure that your images are in .jpg format and your XML files are named correctly.
- The XML files should be located inside a page subdirectory under the same directory as the images.
- The pages are sorted based on their names. Make sure they follow a naming convention which makes them sortable, or adjust the code to pay mind to the naming conventions of your files.

## License
This project is licensed under the MIT License.
