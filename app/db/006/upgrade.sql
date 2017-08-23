ALTER TABLE SubjectFile
  ADD COLUMN dicomTagsMetadata TEXT,
  ADD COLUMN imagingDate datetime,
  MODIFY sbjID int(10) unsigned,
  MODIFY evtID integer unsigned;

-- add the batch generated log type
INSERT INTO LogType
(logtType, logtDescription)
VALUES
('batch_generated','Event runs when a zip file is generated for a batch download'),
('token_generated','Event runs when an admin creates a token for a user to use token auth'),
('token_auth_attempted','Someone attempted to use a token to log in');

ALTER TABLE User
  ADD COLUMN tokenHash varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT '',
  ADD COLUMN tokenSalt varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT '';
