import json
import md5
from types import SimpleNamespace

class ImageFile(object):
    def __init__(self, file_path, dropper_database_connection, redcap_api, **kwargs):
        self.conn = dropper_database_connection
        self.api = redcap_api
        self.data = SimpleNamespace(**kwargs)
        self.json = json.dumps(kwargs)
        self._get_subject_header_records()

        with open(file_path, 'rb') as image:
            m = md5.new(image.read())
            self.md5 = m.digest()


    def _get_subject_header_records(self):
        res = self.api.export_records(fields=['ptid',
                                              'visitmo',
                                              'visitday',
                                              'visityr',
                                              'visitnum',
                                              'redcap_event_name'],
                                      records=[self.data.ptid])
        self.record_data = SimpleNamspace(json.loads(res.content))
        return self.record_data

    def _get_event_name_dates(self):
        dates = ['-'.join([i.visityr, i.visitmo, i.visitday]) for i in self.record_data]
        names = [i.redcap_event_name for i in self.record_data]
        return zip(names, dates)

    def get_event_name(self):
        target = self.data.StudyDate
        for name, date in self._get_event_name_dates().reverse():
            if date < target:
                return name
            else:
                pass
        exit('no event found')

    def load_into_dropper_db(self):
        self.conn.query("""
        SELECT sbjID from Subject where sbjRedcapID = '{}';
        """.format(self.data.ptid))
        sbjID = self.conn.store_result()
        self.conn.query("""
        SELECT evtID from Event where evtRedcapEvent = '{}';
        """.format(self.data.redcap_event_name))
        evtID = self.conn.store_result()
        self.conn.query(self._build_update(sbjID, evtID))

    def _build_update(self, subject_id, event_id):
        return """
        UPDATE SubjectFile
        SET tagsJSON = {json},
        WHERE sbjID = {subject_id} and evtID = {event_id} and sfFileChecksum = {checksum};
        """.format(**{
            'json': self.json,
            'subject_id': subject_id,
            'event_id': event_id,
            'checksum': self.md5
        })
