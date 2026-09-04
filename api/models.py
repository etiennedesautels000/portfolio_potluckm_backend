

from datetime import datetime
from api import db

### sqlalchemy class models, with to_dict and from_dict converters

class Potlucks(db.Model):
    __tablename__ = 'Potlucks'

    id = db.Column(db.Integer, primary_key=True)
    event_date = db.Column(db.Date, nullable=False)
    time_begin = db.Column(db.Time, nullable=False)
    time_end = db.Column(db.Time, nullable=True)
    title = db.Column(db.String, nullable=False)
    organizer = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)

    subgroups = db.relationship('Subgroups', backref='potluck', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'event_date': self.event_date.isoformat(),
            'time_begin': self.time_begin.isoformat(),
            'time_end': self.time_end.isoformat() if self.time_end else None,
            'title': self.title,
            'organizer': self.organizer,
            'location': self.location
        }

    def update(self, record):
        time_end_val = record.get('time_end')
        self.event_date = datetime.strptime(record['event_date'], '%Y-%m-%d').date()
        self.time_begin = datetime.strptime(record['time_begin'], '%H:%M').time()
        self.time_end = datetime.strptime(time_end_val, '%H:%M').time() if time_end_val else None
        self.title = record['title']
        self.organizer = record['organizer']
        self.location = record['location']

    @classmethod
    def from_dict(cls, record):
        time_end_val = record.get('time_end')
        return cls(
            event_date=datetime.strptime(record['event_date'], '%Y-%m-%d').date(),
            time_begin=datetime.strptime(record['time_begin'], '%H:%M').time(),
            time_end=datetime.strptime(time_end_val, '%H:%M').time() if time_end_val else None,
            title=record['title'],
            organizer=record['organizer'],
            location=record['location']
        )


class Subgroups(db.Model):
    __tablename__ = 'Subgroups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    potluck_id = db.Column(db.Integer, db.ForeignKey('Potlucks.id'), nullable=False)

    contributions = db.relationship('Contributions', backref='subgroup', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'potluck_id': self.potluck_id
        }

    def update(self, record):
        self.name = record['name']
        self.potluck_id = record['potluck_id']

    @classmethod
    def from_dict(cls, record):
        return cls(
            name=record['name'],
            potluck_id=record['potluck_id']
        )


class Contributions(db.Model):
    __tablename__ = 'Contributions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=True)
    notes = db.Column(db.String, nullable=True)
    subgroup_id = db.Column(db.Integer, db.ForeignKey('Subgroups.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'notes': self.notes,
            'subgroup_id': self.subgroup_id
        }

    def update(self, record):
        self.name = record['name']
        self.category = record.get('category')
        self.notes = record.get('notes')
        self.subgroup_id = record['subgroup_id']

    @classmethod
    def from_dict(cls, record):
        return cls(
            name=record['name'],
            category=record['category'],
            notes=record['notes'],
            subgroup_id=record['subgroup_id']
        )
