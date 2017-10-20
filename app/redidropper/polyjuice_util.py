import json

from polyjuice.dicom_image import DicomImage

def get_changes_for_deidentification():
    """
    The dictionary returned here was specified as the recommended
    way to deidentify dicom files

    Any change in here that is not an empty string was made to reflect
    the changes that were made in the dicom file after the manual process
    """
    return {
        'SOPInstanceUID': '',
        'AccessionNumber': '',
        'InstitutionName': '',
        'ReferringPhysicianName': '',
        'StationName': '',
        'StudyDescription': '',
        'SeriesDescription': '',
        'RequestingPhysician': '',
        'PhysiciansOfRecord': '',
        'PatientName': 'Anonymous',
        'PatientBirthDate': "19990909",
        'PatientSex': '',
        'PatientAge': '',
        'PatientWeight': '',
        'EthnicGroup': '',
        'PatientAddress': '',
        'ProtocolName': '',
        'StudyInstanceUID': '',
        'SeriesInstanceUID': '',
        'StudyID': '',
        'RescaleIntercept': None,
        'RescaleSlope': None,
        'RescaleType': None,
    }

def is_delete_value(value):
    return value == None

def _deidentify(image):
    changes = get_changes_for_deidentification()
    for key, value in changes.items():
        delete = is_delete_value(value)
        image.modify_item(key, value, delete)
    return image

def get_file_type(metadata_string):
    """
    Modality is the name of the dicom header that specifies the type
    MR is magnetic resonance
    CT is computed tomography
    a full list can be found at https://www.dicomlibrary.com/dicom/modality/
    """
    data = json.loads(metadata_string)
    return data['Modality']

def clean_image(subject_file, directory):
    """
    This function edits the file and updates the database entry
    """
    image_path = subject_file.get_full_path(directory)
    image_file = open(image_path)
    image = DicomImage(image_file)
    image_file.close()
    image = _deidentify(image)
    metadata = image.serialize_metadata()
    subject_file.file_metadata = metadata
    subject_file.file_type = get_file_type(metadata)
    image.save_image(image_path)
    subject_file.save()
