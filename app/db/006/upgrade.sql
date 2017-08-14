ALTER TABLE SubjectFile
  ADD COLUMN dicomTagsMetadata TEXT,
  ADD COLUMN imagingDate datetime,
  MODIFY sbjID int(10) unsigned,
  MODIFY evtID integer unsigned;

-- add the batch generated log type
INSERT INTO LogType
(logtType, logtDescription)
VALUES
('batch_generated','Event runs when a zip file is generated for a batch download');
