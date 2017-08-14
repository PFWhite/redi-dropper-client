ALTER TABLE SubjectFile
  DROP COLUMN tagsJSON,
  MODIFY sbjID int(10) unsigned NOT NULL,
  MODIFY evtID integer unsigned NOT NULL;

DELETE FROM LogType
WHERE logtType='batch_generated';
