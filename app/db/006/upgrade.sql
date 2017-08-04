
ALTER TABLE SubjectFile
  ADD COLUMN tagsJSON TEXT,
  MODIFY sbjID int(10) unsigned,
  MODIFY evtID integer unsigned;
