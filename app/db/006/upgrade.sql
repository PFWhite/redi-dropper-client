ALTER TABLE SubjectFile
  ADD COLUMN dicomTagsMetadata TEXT,
  ADD COLUMN imagingDate datetime,
  MODIFY sbjID int(10) unsigned,
  MODIFY evtID integer unsigned;
