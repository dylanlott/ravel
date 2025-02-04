from datetime import datetime
from api import db
import uuid


''' 
    generate_uuid returns a new, unique hexadecimal uuid string
'''
def generate_uuid():
    r = uuid.uuid4()
    return r.hex
    

'''
    This file contains the database relational schema
    Hierarchy can be followed top down
    Tree:
        Track (1->n) TrackOuts
        TrackOuts (1->1) Equalizer
                         Compression
                         Deesser
'''


class Track(db.Model):
    '''
        Database Generated Fields
    '''
    id = db.Column(db.Integer, primary_key=True)
    trackouts = db.relationship('TrackOut', backref=db.backref('trackouts', passive_deletes=True), lazy='dynamic')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    uuid = db.Column(db.String, default=generate_uuid)

    '''
        Configurable Fields
    '''
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(1000))
    artist = db.Column(db.String(200))
    info = db.Column(db.Text)
    compression = db.Column(db.Boolean)
    reverb = db.Column(db.Boolean)
    eq = db.Column(db.Boolean)
    deess = db.Column(db.Boolean)

    def to_dict(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "name": self.name,
            "user_id": self.user_id,
            "artist": self.artist,
            "info": self.info,
            "created_at": self.created_at,
            "compression": self.compression,
            "reverb": self.reverb,
            "eq": self.eq,
            "deess": self.deess
        }


class TrackOut(db.Model):
    '''
        Database Generated Fields
    '''
    id = db.Column(db.Integer, primary_key=True)
    track_id = db.Column(db.Integer, db.ForeignKey('track.uuid', ondelete='CASCADE'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    uuid = db.Column(db.String, default=generate_uuid)

    '''
        Configurable Fields
    '''
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(1000))
    type = db.Column(db.String(50))
    settings = db.Column(db.String(1000))
    eq = db.relationship("Equalizer", backref=db.backref("eq", passive_deletes=True), lazy='subquery', uselist=False)
    de = db.relationship("Deesser", backref=db.backref("de", passive_deletes=True), lazy='subquery', uselist=False)
    co = db.relationship("Compressor", backref=db.backref("co", passive_deletes=True), lazy='subquery', uselist=False)
    re = db.relationship("Reverb", backref=db.backref("re", passive_deletes=True), lazy='subquery', uselist=False)

    '''
    Wav File Representation
    '''
    path = db.Column(db.String(1000))
    file_hash = db.Column(db.LargeBinary, unique=True)

    def to_dict(self):
        trackout = {
            "id": self.id,
            "uuid": self.uuid,
            "user_id": self.user_id,
            "track_id": self.track_id,
            "created_at": self.created_at,
            "name": self.name,
            "type": self.type,
            "path": self.path,
            "settings": self.settings
        }

        return trackout


'''
    FX Models 

    These are models tracked for individual FX that are applied to tracks. 
    They're created to record calculated TrackOut parameters and values.
    They are currently only used for internal processing.
'''
class Equalizer(db.Model):
    '''
        Database Generated Fields
    '''
    id = db.Column(db.Integer, primary_key=True)
    trackout_id = db.Column(db.Integer, db.ForeignKey("track_out.uuid", ondelete='CASCADE'))

    '''
        Configurable Fields
    '''
    freq = db.Column(db.String)
    filter_type = db.Column(db.String)
    gain = db.Column(db.Float)
    path = db.Column(db.String(1000))

    def to_dict(self):
        return {
            "id": self.id,
            "trackout_id": self.trackout_id,
            "freq": self.freq,
            "filter_type": self.filter_type,
            "gain": self.gain
        }


class Deesser(db.Model):
    '''
        Database Generated Fields
    '''
    id = db.Column(db.Integer, primary_key=True)
    trackout_id = db.Column(db.Integer, db.ForeignKey("track_out.uuid", ondelete='CASCADE'))

    '''
        Configurable Fields
    '''
    sharpness_avg = db.Column(db.Float)
    path = db.Column(db.String(1000))

    def to_dict(self):
        return {
            "id": self.id,
            "trackout_id": self.trackout_id,
            "sharpness_avg": self.sharpness_avg
        }


class Reverb(db.Model):
    '''
        Database Generated Fields
    '''
    id = db.Column(db.Integer, primary_key=True)
    trackout_id = db.Column(db.Integer, db.ForeignKey("track_out.uuid", ondelete='CASCADE'))

    '''
        Configurable Fields
    '''
    path = db.Column(db.String(1000))

    def to_dict(self):
        return {
            "id": self.id,
            "trackout_id": self.trackout_id,
        }


class Compressor(db.Model):
    '''
        Database Generated Fields
    '''
    id = db.Column(db.Integer, primary_key=True)
    trackout_id = db.Column(db.Integer, db.ForeignKey("track_out.uuid", ondelete='CASCADE'))

    '''
        Configurable Fields
    '''
    ratio = db.Column(db.Float)
    threshold = db.Column(db.Float)
    knee_width = db.Column(db.Float)
    attack = db.Column(db.Float)
    release = db.Column(db.Float)
    path = db.Column(db.String(1000))

    def to_dict(self):
        return {
            "id": self.id,
            "trackout_id": self.trackout_id,
            "ratio": self.ratio,
            "threshold": self.threshold,
            "knee_width": self.knee_width,
            "attack": self.attack,
            "release": self.release
        }
