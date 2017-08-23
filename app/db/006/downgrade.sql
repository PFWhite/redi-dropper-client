ALTER TABLE SubjectFile
  DROP COLUMN tagsJSON,
  MODIFY sbjID int(10) unsigned NOT NULL,
  MODIFY evtID integer unsigned NOT NULL;

DELETE FROM LogType
WHERE logtType='batch_generated' OR logtType='token_auth_authenticated';

ALTER TABLE User
  DROP COLUMN tokenHash,
  DROP COLUMN tokenSalt;
