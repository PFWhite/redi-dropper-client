"""
Goal: Delegate requests to the `/api` path to the appropriate controller

@authors:
  Akash Agarwal           <agarwala989@gmail.com
  Andrei Sura             <sura.andrei@gmail.com>
  Ruchi Vivek Desai       <ruchivdesai@gmail.com>
  Sanath Pasumarthy       <sanath@ufl.edu>
  Taeber Rapczak          <taeber@ufl.edu>
"""

import os
import json
import zipfile
import random
import string
from datetime import datetime
import collections

from flask import request
from flask import send_file
from flask import session
from flask import make_response
from flask_login import login_required, current_user

from redidropper.main import app, db
from redidropper import emails
from redidropper import utils
from redidropper.models.log_entity import LogEntity
from redidropper.routes import file_manager

from redidropper.models.subject_entity import SubjectEntity
from redidropper.models.subject_file_entity import SubjectFileEntity
from redidropper.models.event_entity import EventEntity
from redidropper.models.user_entity import UserEntity
from redidropper.models.role_entity import RoleEntity

from redidropper.routes.users import perm_admin, perm_admin_or_technician, perm_deleter


@app.route('/api/list_subject_events', methods=['POST', 'GET'])
@login_required
def api_list_subject_events():
    """
    :rtype: Response
    :return the list of subjects in json format
    """
    # from sqlalchemy.sql import text
    from collections import namedtuple

    if 'POST' == request.method:
        subject_id = utils.get_safe_int(request.form.get('subject_id'))
    else:
        subject_id = utils.get_safe_int(request.args.get('subject_id'))

    query = """
SELECT
    evtID AS id
    , evtRedcapArm AS redcap_arm
    , evtRedcapEvent AS redcap_event
    , evtDayOffset AS day_offset
    , COUNT(sfID) AS total_files
    , GROUP_CONCAT(sfFileName) AS file_names
FROM
     Event
    JOIN SubjectFile USING(evtID)
WHERE
    sbjID = :subject_id
GROUP BY
    evtID
    """
    # print subject_id, query
    result = db.session.execute(query, {'subject_id': subject_id})
    Event = namedtuple('Event', result.keys())
    events = [Event(*r) for r in result.fetchall()]
    events_ser = [i._asdict() for i in events]
    return utils.jsonify_success({'subject_events': events_ser})


@app.route('/api/list_subject_event_files', methods=['POST', 'GET'])
@login_required
def api_list_subject_event_files():
    """
    :rtype: Response
    :return the list of subjects in json format
    """

    if 'POST' == request.method:
        subject_id = utils.get_safe_int(request.form.get('subject_id'))
        event_id = utils.get_safe_int(request.form.get('event_id'))
    else:
        subject_id = utils.get_safe_int(request.args.get('subject_id'))
        event_id = utils.get_safe_int(request.args.get('event_id'))

    files = SubjectFileEntity \
        .query.filter_by(subject_id=subject_id,
                         event_id=event_id).all()
    files_ser = [i.serialize() for i in files]
    return utils.jsonify_success({'subject_event_files': files_ser})


@app.route('/api/find_subject', methods=['POST', 'GET'])
@login_required
def find_subject():
    """
    Side effect: This function will synchronize the list of subjects in the
    local database with REDCap by sending a REDCap API call
    if the local database contains no entries.

    :rtype: Response
    :return the list of subjects in json format
    """
    invalid_id = -1

    if 'POST' == request.method:
        search_id = utils.get_safe_int(request.form['name'],
                                       invalid_id, invalid_id)
    else:
        search_id = utils.get_safe_int(request.args.get('name'),
                                       invalid_id,
                                       invalid_id)

    matching = []

    if search_id != invalid_id:
        # @TODO: optimize to return one column by default
        # http://stackoverflow.com/questions/7533146/how-do-i-select-additional-manual-values-along-with-an-sqlalchemy-query
        subject_list = SubjectEntity.query.filter(
            SubjectEntity.redcap_id.like("%{}%".format(search_id))
        ).all()
        matching = [subject.redcap_id for subject in subject_list]

        if len(matching) == 0:
            api_import_redcap_subjects()

    return utils.jsonify_success({'subjects': matching})


@app.route('/api/list_events', methods=['POST', 'GET'])
@login_required
def list_events():
    """
    Side effect: This function will synchronize the list of events in the
    local database with REDCap by sending a REDCap API call
    if the local database contains no entries.

    :rtype: Response
    :return the list of subjects in json format
    """
    events = EventEntity.query.all()
    events_ser = [i.serialize() for i in events]

    if len(events) == 0:
        api_import_redcap_events()

    return utils.jsonify_success({'events': events_ser})


@app.route('/api/upload', methods=['POST'])
@login_required
def api_upload():
    """ Receives files on the server side
    :rtype: Response
    :return the status of the upload action in json format

    @TODO: respond with an error if upload failed
    """
    return make_response(file_manager.save_uploaded_file(), 200)

@app.route('/api/delete_file', methods=['POST'])
@login_required
@perm_deleter.require(http_exception=403)
def api_delete_file():
    """ Deletes the passed file    """
    #get the file from the response
    subject_file_id = request.form.get('file_id')

    try:
        ret_value = file_manager.delete_file(subject_file_id)
        deleted_id = ret_value[0]
        deleted_path = ret_value[1]
        app.logger.debug("deleted file id: {}".format(subject_file_id))
        LogEntity.file_deleted(session['uuid'], deleted_path)
        response = utils.jsonify_success({"file_id": deleted_id})

    except:
        response = utils.jsonify_error({"exception": ret_value})

    return response

@app.route('/api/update_fileType', methods=['POST'])
@login_required
def api_update_fileType():
    """ Updates the file type    """
    #get the file from the response
    subject_file_id = request.form.get('file_id')
    subject_file_type = request.form.get('file_type')
    try:
        ret_value = file_manager.update_filetype(subject_file_id, subject_file_type)
        #app.logger.debug("updated file id: {}".format(subject_file_id))
        response = utils.jsonify_success({"file_id": ret_value[0], "file_type": ret_value[1]})

    except:
        response = utils.jsonify_error({"exception": ret_value})

    return response

@app.route("/api/download_file", methods=['POST'])
@login_required
def download_file():
    """ Download a file using the database id """

    if 'POST' == request.method:
        file_id = utils.get_safe_int(request.form['file_id'])
    else:
        file_id = utils.get_safe_int(request.args.get('file_id'))

    subject_file = SubjectFileEntity.get_by_id(file_id)
    file_path = subject_file.get_full_path(
        app.config['REDIDROPPER_UPLOAD_SAVED_DIR'])
    LogEntity.file_downloaded(session['uuid'], file_path)
    return send_file(file_path, as_attachment=True)

def get_all_files():
    """
    Returns all SubjectFiles with the redcap_event and subject redcap id attached
    """
    return db.session.query(SubjectFileEntity,
                            EventEntity.redcap_event,
                            SubjectEntity.redcap_id).join(EventEntity).join(SubjectEntity)

def __get_matching_batch(subjects=[ 'ALL' ], events=[ 'ALL' ], startDate=None,
                         endDate=None, takenStartDate=None, takenEndDate=None,
                         imageTypes=[ 'ALL' ]):
    """
    This is used with batch downloading to filter out the files that
    dont match what is passed
    """
    all_files = get_all_files()
    if not 'ALL' in subjects:
        all_files = all_files.filter(SubjectEntity.redcap_id.in_(subjects))
    if not 'ALL' in events:
        all_files = all_files.filter(EventEntity.redcap_event.in_(events))
    if startDate:
        all_files = all_files.filter(SubjectFileEntity.uploaded_at >= startDate)
    if endDate:
        all_files = all_files.filter(SubjectFileEntity.uploaded_at <= startDate)
    if not 'ALL' in imageTypes:
        all_files = all_files.filter(SubjectFileEntity.file_type.in_(imageTypes))
    return all_files

def clean_old_files(root, test_string='download'):
    # two days, 24 hours, 60 min, 60 sec
    too_old = 2 * 24 * 60 * 60
    for root, dirs, files in os.walk(root):
        for path in files:
            if test_string in path:
                if os.stat(os.path.join(root, path)).st_mtime > too_old:
                    os.remove(os.path.join(root, path))
                    LogEntity.file_deleted(session['uuid'], os.path.join(root, path))


@app.route('/api/batch_download', methods=['GET', 'HEAD'])
@login_required
def api_batch_download():
    """
    Uses the url args to find matching files. Then downloads a
    zipfile containing those files.
    Also will generate a metadata file for the end user that has
    information about the file

    The GET route will download the file where as the HEAD will return
    just the metadata of the files that would be downloaded with GET

    NOTE: Calling this route deletes old stuff from the tmp
    directory
    TODO: configurable tmp directory
    """
    clean_old_files('/tmp')

    query = request.args.get('q')
    params = json.loads(query)

    try:
        all_files, events, subjects = zip(*__get_matching_batch(**params))
    except ValueError as ex:
        return utils.jsonify_error(params, 404)

    # metadata file generation
    now = str(datetime.now()).replace(' ', '_')
    paths = [subfile.get_full_path(app.config['REDIDROPPER_UPLOAD_SAVED_DIR']) for subfile in all_files]
    meta_path = '/tmp/download_metadata-' + now + '.json'
    paths.append(meta_path)
    metadata = {
        'url_parameters': params,
        'files': [f.serialize() for f in all_files]
    }
    if request.method == 'HEAD':
        return utils.jsonify_success(metadata)

    with open(meta_path, 'w') as mfile:
        json.dump(metadata, mfile, indent=4, sort_keys=True)

    # zip files into tmp
    zip_path = '/tmp/batch_download-' + str(now) + '.zip'
    with zipfile.ZipFile(zip_path, 'w') as myzip:
        for path in paths:
            myzip.write(path, os.path.basename(path))

    # log steps
    LogEntity.batch_generated(session['uuid'], zip_path)

    # send zip
    filename = os.path.split(zip_path)[1]
    res = send_file(zip_path, as_attachment=True)
    return res

@app.route("/api/all_files_info", methods=['GET'])
@login_required
def all_files_info():
    """ Get the list of all uploaded files and their path """
    all_files = get_all_files()
    return_list = [__build_files_info_json(subject_file,event,subject) for subject_file,event,subject in all_files]
    return utils.jsonify_success({'list_of_files' : return_list})

def __build_files_info_json(subject_file,event,subject):
    path = subject_file.get_full_path(app.config['REDIDROPPER_UPLOAD_SAVED_DIR'])
    file_json = subject_file.serialize()
    file_json['path'] = path
    file_json['redcap_id'] = subject
    file_json['redcap_event'] = event
    return file_json

def __extract_user_information(request):
    return {
        "email": request.form.get('email'),
        "first": request.form.get('first'),
        "last": request.form.get('last'),
        "minitial": request.form.get('minitial'),
        "roles": request.form.getlist('roles[]'),
        "is_edit": request.form.get('isEdit'),
        "usr_id": request.form.get('usrId'),
    }

def __get_date_information():
    return {
        "added_at": datetime.today(),
        "access_expires_at": utils.get_expiration_date(180),
    }

def __assign_roles(roles_required, user):
    """
    Delete all roles for the user if not in the
    provided `roles_required` list and assing new roles.
    """
    all_roles = RoleEntity.query.all()
    user_roles = [role for role in all_roles if role.name in roles_required]
    user = UserEntity.update(user, roles=user_roles)
    return user

@app.route('/api/gen_token', methods=['POST'])
@login_required
@perm_admin.require(http_exception=403)
def generate_token():
    user_id = request.form.get('user_id')
    user = UserEntity.get_by_id(user_id)
    if user:
        token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(32))
        creds = UserEntity.generate_credentials(user.email, token)
        user.token_hash = creds['password_hash']
        user.token_salt = creds['salt']
        user.update()
        LogEntity.token_generated(session['uuid'],
                                  '{} created a token for {}'.format(current_user, user.email))
        return utils.jsonify_success(token)
    else:
        return utils.jsonify_error('No user found', 404)


@app.route('/api/save_user', methods=['POST'])
@login_required
@perm_admin.require(http_exception=403)
def api_save_user():
    """ Save a new user to the database
    TODO: Add support for reading a password field
    """
    request_data = __extract_user_information(request)
    credentials = UserEntity.generate_credentials(request_data["email"])
    date_data = __get_date_information()

    if UserEntity.is_existing(request_data["email"]):
        return utils.jsonify_error(
            {'message': 'Sorry. This email is already taken.'})

    user = UserEntity.create(email=request_data["email"],
                             first=request_data["first"],
                             last=request_data["last"],
                             minitial=request_data["minitial"],
                             added_at=date_data["added_at"],
                             modified_at=date_data["added_at"],
                             access_expires_at=date_data["access_expires_at"],
                             password_hash="{}:{}"
                             .format(credentials["salt"],
                                     credentials["password_hash"]))

    __assign_roles(request_data["roles"], user)

    app.logger.debug("saved user: {}".format(user))
    LogEntity.account_created(session['uuid'], user)
    # NOTE the verification call here users the secret key instead of the salt.
    return utils.jsonify_success({
        'user': user.serialize(),
        'verify_token': user.get_email_verification_token(app.config['SECRET_KEY'], app.config['SECRET_KEY'])
    })

@app.route('/api/edit_user', methods=['POST'])
@login_required
@perm_admin.require(http_exception=403)
def api_edit_user():
    """ Edit an existing user in the database
    TODO: Add support for reading a password field
    """
    request_data = __extract_user_information(request)
    credentials = UserEntity.generate_credentials(request_data["email"])
    date_data = __get_date_information()

    user = UserEntity.get_by_id(id=request_data["usr_id"])
    user.update(email=request_data["email"],
                first=request_data["first"],
                last=request_data["last"],
                minitial=request_data["minitial"],
                added_at=date_data["added_at"],
                modified_at=date_data["added_at"],
                access_expires_at=date_data["access_expires_at"],
                password_hash="{}:{}".format(credentials["salt"],
                                             credentials["password_hash"]))

    __assign_roles(request_data["roles"], user)

    app.logger.debug("updated user: {}".format(user))
    LogEntity.account_updated(session['uuid'], user)
    return utils.jsonify_success({'user': user.serialize()})

@app.route('/api/list_users', methods=['POST', 'GET'])
@login_required
def api_list_users():
    """
    Retrieve the users cached in the local database
    :rtype: Response
    :return
    """
    if 'POST' == request.method:
        per_page = utils.get_safe_int(request.form.get('per_page'))
        page_num = utils.get_safe_int(request.form.get('page_num'))
    else:
        per_page = utils.get_safe_int(request.args.get('per_page'))
        page_num = utils.get_safe_int(request.args.get('page_num'))

    pagination = UserEntity.query.order_by(
        db.desc(UserEntity.id)).paginate(page_num, per_page, False)
    items = [i.serialize() for i in pagination.items]
    return utils.jsonify_success(
        {"total_pages": pagination.pages, "list_of_users": items})


@app.route('/api/list_logs', methods=['GET', 'POST'])
@login_required
def api_list_logs():
    """
    Render the specified page of event logs
    @TODO: show user-specific logs for non-admins?

    :rtype: string
    :return the json list of logs
    """
    if 'POST' == request.method:
        per_page = utils.get_safe_int(request.form.get('per_page'))
        page_num = utils.get_safe_int(request.form.get('page_num'))
    else:
        per_page = utils.get_safe_int(request.args.get('per_page'))
        page_num = utils.get_safe_int(request.args.get('page_num'))

    logs, total_pages = LogEntity.get_logs(per_page, page_num)

    return utils.jsonify_success(
        dict(list_of_events=logs, total_pages=total_pages))


@app.route('/api/list_local_subjects', methods=['GET', 'POST'])
@login_required
def api_list_local_subjects():
    """
    Render the table of subjects and their file counts

    @see http://pythonhosted.org/Flask-SQLAlchemy/api.html
        #flask.ext.sqlalchemy.BaseQuery.paginate
    paginate(page, per_page=20, error_out=True)

    :rtype: Response
    :return json
    """
    if 'POST' == request.method:
        per_page = utils.get_safe_int(request.form.get('per_page'))
        page_num = utils.get_safe_int(request.form.get('page_num'))
    else:
        per_page = utils.get_safe_int(request.args.get('per_page'))
        page_num = utils.get_safe_int(request.args.get('page_num'))

    pagination = SubjectEntity.query.paginate(page_num, per_page, False)
    items = [i.serialize() for i in pagination.items]
    return utils.jsonify_success(
        dict(total_pages=pagination.pages, list_of_subjects=items))


@app.route('/api/activate_account', methods=['POST'])
@login_required
@perm_admin.require()
def api_activate_account():
    """
    Activate an user.
    @TODO: should change expiration date too?

    :rtype: Response
    :return the success or failed in json format
    """
    user_id = utils.get_safe_int(request.form.get('user_id'))
    user = UserEntity.get_by_id(user_id)
    user = UserEntity.update(user, active=True)
    LogEntity.account_modified(session['uuid'],
                               "User activated: {}".format(user))
    return utils.jsonify_success({"message": "User activated."})


@app.route('/api/deactivate_account', methods=['POST'])
@login_required
@perm_admin.require()
def api_deactivate_account():
    """
    De-activate an user.
    @TODO: should change expiration date too?

    :rtype: Response
    :return the success or failed in json format
    """
    user_id = utils.get_safe_int(request.form.get('user_id'))
    user = UserEntity.get_by_id(user_id)
    user = UserEntity.update(user, active=False)
    LogEntity.account_modified(session['uuid'],
                               "User deactivated: {}".format(user))
    return utils.jsonify_success({"message": "User deactivated."})


@app.route('/api/send_verification_email', methods=['POST'])
@login_required
@perm_admin.require()
def api_send_verification_email():
    """
    @TODO: Send Verification Email to user_id

    :rtype: Response
    :return the success or failed in json format
    """
    user_id = utils.get_safe_int(request.form.get('user_id'))
    user = UserEntity.get_by_id(user_id)

    try:
        emails.send_verification_email(user)
        return utils.jsonify_success(
            {"message": "Verification email was sent."})
    except Exception as exc:
        details = "Connection config: {}/{}:{}".format(
            app.config['MAIL_USERNAME'],
            app.config['MAIL_SERVER'],
            app.config['MAIL_PORT'])
        app.logger.debug(details)
        return utils.jsonify_error(
            {"message": "Unable to send email due: {} {}".format(exc, details)})


@app.route('/api/verify_email', methods=['GET', 'POST'])
def api_verify_email():
    """
    @TODO: add counter/log to track failed attempts

    :rtype: Response
    :return the success or failed in json format
    """
    if 'POST' == request.method:
        token = utils.clean_str(request.form.get('tok'))
    else:
        token = utils.clean_str(request.args.get('tok'))

    if not token:
        return utils.jsonify_error({'message': 'No token specified.'})

    try:
        email = utils.get_email_from_token(token,
                                           app.config["SECRET_KEY"],
                                           app.config["SECRET_KEY"])
    except Exception as exc:
        # @TODO: add dedicated log type
        app.logger.error("api_verify_email: {}".format(exc.message))
        return utils.jsonify_error({'message': exc.message})

    app.logger.debug("Decoded email from token: {}".format(email))
    user = UserEntity.query.filter_by(email=email).first()

    if user is None:
        app.logger.error("Attempt to verify email with incorrect token: {}"
                         .format(token))
        return utils.jsonify_error({'message': 'Sorry.'})

    user = UserEntity.update(user, email_confirmed_at=datetime.today())
    app.logger.debug("Verified token {} for user {}".format(token, user.email))

    # @TODO: add dedicated log type
    LogEntity.account_modified(session['uuid'],
                               "Verified token {} for user {}".format(
                                   token, user.email))
    return utils.jsonify_success(
        {"message": "Email was verified for {}.".format(email)})


@app.route('/api/expire_account', methods=['POST'])
@login_required
@perm_admin.require()
def api_expire_account():
    """
    Change the `User.usrAccessExpiresAt` to today's date and 00:00:00 time
    effectively blocking the user access.

    :rtype: Response
    :return the success or failed in json format
    """
    user_id = utils.get_safe_int(request.form.get('user_id'))
    user = UserEntity.get_by_id(user_id)
    today = datetime.today()
    today_start = datetime(today.year, today.month, today.day)
    user = UserEntity.update(user, access_expires_at=today_start)
    # @TODO: add dedicated log type
    LogEntity.account_modified(session['uuid'],
                               "User access was expired. {}".format(user.email))
    return utils.jsonify_success({"message": "User access was expired."})


@app.route('/api/extend_account', methods=['POST'])
@login_required
@perm_admin.require()
def api_extend_account():
    """
    Change the `User.usrAccessExpiresAt` to today's date + 180 days

    :rtype: Response
    :return the success or failed in json format
    """
    user_id = request.form.get('user_id')
    today_plus_180 = utils.get_expiration_date(180)
    user = UserEntity.get_by_id(user_id)
    user = UserEntity.update(user, access_expires_at=today_plus_180)
    # @TODO: add dedicated log type
    LogEntity.account_modified(session['uuid'],
                               "Updated expiration date to {}. {}".format(
                                   today_plus_180, user.email))
    return utils.jsonify_success(
        {"message": "Updated expiration date to {}".format(today_plus_180)})


@app.route('/api/import_redcap_subjects', methods=['POST'])
@login_required
@perm_admin_or_technician.require()
def api_import_redcap_subjects():
    """
    Refresh the list of subjects
    """
    local_subjects = SubjectEntity.query.all()
    url = app.config['REDCAP_API_URL']
    redcap_subjects = utils.retrieve_redcap_subjects(
        url=url,
        token=app.config['REDCAP_API_TOKEN'],
        fields=app.config['REDCAP_DEMOGRAPHICS_SUBJECT_ID'],
        max_time=app.config['REDCAP_CURL_API_MAX_TIME'])
    new_subjects = find_new_subjects(local_subjects, redcap_subjects)

    added_date = datetime.today()
    inserted_subjects = []

    for id, redcap_subject in new_subjects.iteritems():
        subject = SubjectEntity.create(
            redcap_id=id,
            added_at=added_date,
            last_checked_at=added_date,
            was_deleted=False)
        inserted_subjects.append(subject)

    details = [i for i in new_subjects]
    LogEntity.redcap_subjects_imported(session['uuid'],
                                       "Total: {} \n {}"
                                       .format(len(details), details))

    return utils.jsonify_success({
        'local_subjects': [i.redcap_id for i in local_subjects],
        'redcap_subjects': redcap_subjects,
        'inserted_subjects': [i.redcap_id for i in inserted_subjects],
        'api_url': url
    })


def find_new_subjects(local_subjects, redcap_subjects):
    """
    :param local_subjects: the list of SubjectEntity in the local database
    :param redcap_subjects: the list of subjects in the remote database
    :rtype {}
    :return the dictionary of subjects that do not exist in the local database
    """
    local_lut = collections.OrderedDict()

    for subj in local_subjects:
        # populate the lookup table for faster comparison
        local_lut[subj.redcap_id] = subj

    subject_id_field = app.config['REDCAP_DEMOGRAPHICS_SUBJECT_ID']
    new_subjects = {}

    for subj in redcap_subjects:
        id = str(subj[subject_id_field])
        if id not in local_lut:
            # app.logger.debug("id {} not in local list of ids".format(id))
            new_subjects[id] = subj

    return new_subjects


def find_new_events(local_events, redcap_events):
    """
    :param local_events: the EventEntity objects in the local database
    :param redcap_subjects: the events in the remote database
    :rtype {}
    :return the dictionary of events  that do not exist in the local database
    """

    local_lut = collections.OrderedDict()

    for evt in local_events:
        # local_lut.append(evt.get_unique_event_name())
        local_lut[evt.get_unique_event_name()] = evt

    new_events = collections.OrderedDict()

    for evt in redcap_events:
        id = evt['unique_event_name']
        if id not in local_lut:
            new_events[id] = evt

    return new_events


@app.route('/api/import_redcap_events', methods=['POST'])
@login_required
@perm_admin_or_technician.require()
def api_import_redcap_events():
    """
    Refresh the list of events
    """
    url = app.config['REDCAP_API_URL']
    local_events = EventEntity.query.all()
    redcap_events = utils.retrieve_redcap_events(
        url=url,
        token=app.config['REDCAP_API_TOKEN'],
        max_time=app.config['REDCAP_CURL_API_MAX_TIME'])
    new_events = find_new_events(local_events, redcap_events)

    added_date = datetime.today()
    inserted_events = []

    for id, redcap_event in new_events.iteritems():
        evt = EventEntity.create(
            redcap_arm='arm_{}'.format(redcap_event['arm_num']),
            redcap_event=redcap_event['event_name'],
            day_offset=redcap_event['day_offset'],
            added_at=added_date
        )
        inserted_events.append(evt)

    details = [i for i in new_events]
    LogEntity.redcap_events_imported(session['uuid'],
                                     "Total: {} \n {}"
                                     .format(len(details), details))

    return utils.jsonify_success({
        'local_events': [i.get_unique_event_name() for i in local_events],
        'redcap_events': redcap_events,
        'inserted_events': [i.get_unique_event_name() for i in inserted_events],
        'api_url': url})
