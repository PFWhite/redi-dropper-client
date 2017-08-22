"""
ORM for RediDropper.LogType table
"""
from redidropper.database.crud_mixin import CRUDMixin
from redidropper.main import db

LOG_TYPE_ACCOUNT_CREATED = 'account_created'
LOG_TYPE_LOGIN = 'login'
LOG_TYPE_LOGOUT = 'logout'
LOG_TYPE_LOGIN_ERROR = 'login_error'
LOG_TYPE_FILE_UPLOADED = 'file_uploaded'
LOG_TYPE_FILE_DELETED = 'file_deleted'
LOG_TYPE_FILE_DOWNLOADED = 'file_downloaded'
LOG_TYPE_ACCOUNT_MODIFIED = 'account_modified'
LOG_TYPE_REDCAP_SUBJECTS_IMPORTED = 'redcap_subjects_impported'
LOG_TYPE_REDCAP_EVENTS_IMPORTED = 'redcap_events_imported'
LOG_TYPE_ACCOUNT_UPDATED = 'account_updated'
LOG_TYPE_BATCH_GENERATED = 'batch_generated'
LOG_TYPE_TOKEN_AUTH_ATTEMPTED = 'token_auth_attempted'
LOG_TYPE_TOKEN_GENERATED = 'token_generated'


class LogTypeEntity(db.Model, CRUDMixin):

    """ Stores types of logs """
    __tablename__ = 'LogType'

    id = db.Column('logtID', db.Integer, primary_key=True)
    type = db.Column('logtType', db.String(255), nullable=False)
    description = db.Column('logtDescription', db.Text, nullable=False)

    def __repr__(self):
        """ Return a friendly object representation """
        return ("<LogTypeEntity(id: {0.id}, "
                "logtType: {0.type}, "
                "logtDescription: {0.description})>"
                .format(self))
