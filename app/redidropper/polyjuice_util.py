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
    changes = get_changes_for_deidentificaton()
    for key, value in changes.items():
        delete = is_delete_value(key, value)
        image.modify_item(key, value, delete)
    return image

def clean_image(subject_file, file_prefix):
    """
    This function edits the file and updates the database entry
    """
    image_path = subject_file.get_full_path(file_prefx)
    image = DicomImage(image_path)
    image = _deidentify(image)
    # event = get_event_name(image)
    metadata = image.serialize_metadata()
    subject_file.file_metadata = metadata
    image.save_image(image_path)
    subject_file.save()
