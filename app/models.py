from . import db

__all__ = ['Field', 'Player', 'Record']


class Field(db.Model):
    __tablename__ = 'fields'
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.Integer, nullable=False)
    fox_count = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(40))
    records = db.relationship(
        'Record',
        backref='field',
        foreign_keys='Record.field_id',
        order_by='asc(Record.shot_count),asc(Record.seconds)',
        lazy='dynamic')


class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)


class Record(db.Model):
    __tablename__ = 'records'
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), primary_key=True)
    field_id = db.Column(db.Integer, db.ForeignKey('fields.id'), primary_key=True)
    shot_count = db.Column(db.Integer, nullable=False, primary_key=True)
    seconds = db.Column(db.Float(precision=6, decimal_return_scale=3), primary_key=True)
    player = db.relationship(
        'Player',
        backref='record',
        primaryjoin='Record.player_id==Player.id')
