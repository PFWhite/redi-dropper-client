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
        'AccessionNumber': '',
        'EthnicGroup': '',
        'InstitutionName': '',
        'PatientAddress': '',
        'PatientAge': '',
        'PatientBirthDate': "19990909",
        'PatientName': 'Anonymous',
        'PatientSex': '',
        'PatientWeight': '',
        'PhysiciansOfRecord': '',
        'ProtocolName': '',
        'ReferringPhysicianName': '',
        'RequestingPhysician': '',
        'RescaleIntercept': None,
        'RescaleSlope': None,
        'RescaleType': None,
        'SOPInstanceUID': '',
        'SeriesDescription': '',
        'StationName': '',
        'StudyDescription': '',
        'StudyID': '',
        'StudyInstanceUID': '',
        'SeriesInstanceUID': ''
    }

def _deidentify(image):
    changes = get_changes_for_deidentification()
    for key, value in changes.items():
        obfuscate = True
        image.modify_item(key, value, obfuscate=obfuscate)
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
