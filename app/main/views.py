import random
from datetime import datetime
from flask import render_template
from flask import abort
from flask import jsonify
from flask import request
from flask import session
from . import main
from .. import db
from .. models import *


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/field/<int:field_id>', methods=['GET'])
def field(field_id):
    """Initilization of the game"""
    if not request.is_xhr:
        abort(403)

    if field_id == 0:
        field_id = session.get('current_field_id', 2)

    session['current_field_id'] = field_id
    state = {
        'status': 0,
        'field_size': 0,
        'fox_count': 0,
        'foxes': [],
        'start_time': 0,
        'end_time': 0,
        'shot_count': 0,
        'last_shot_result': '',
        'hits': 0,
        'is_in_top_10': False,
    }
    field = Field.query.get(field_id)
    state['field_size'] = field.size
    state['fox_count'] = field.fox_count

    installed_foxes = 0
    foxes = []
    random.seed()
    while installed_foxes < field.fox_count:
        x = random.randrange(field.size)
        y = random.randrange(field.size)
        fox = {
            'x': x,
            'y': y,
        }
        if fox in foxes:
            continue
        foxes.append(fox)
        installed_foxes += 1

    state['foxes'] = foxes
    session['state'] = state

    result = state.copy()
    del result['foxes'] # We don't want to spoil foxes' positions

    return jsonify(result)


@main.route('/current_field_id/<int:id>', methods=['GET'])
def set_current_field_id(id):
    """Save selected field id in session"""
    if not request.is_xhr:
        abort(403)
    session['current_field_id'] = id
    return jsonify(id)


@main.route('/fields', methods=['GET'])
def get_fields():
    """Returns all existing field sizes and its names"""
    if not request.is_xhr:
        abort(403)
    fields = Field.query.all()
    result = {field.id:field.name for field in fields}
    return jsonify(result)


@main.route('/shot/<int:x>/<int:y>', methods=['GET'])
def shot(x, y):
    """Make a shot"""
    if not request.is_xhr:
        abort(403)
    if 'state' not in session:
        abort(500)

    state = session['state']

    if state['status'] == 2:
        abort(403)

    if state['shot_count'] == 0:
        # This is a first shot - let's the game begin!
        state['start_time'] = datetime.now()
        state['status'] = 1

    foxes = state['foxes']
    value = 0
    for fox in foxes:
        if fox['x'] == x and fox['y'] == y:
            value = 'hit'
            state['hits'] += 1
            break

        # Counting the number of foxes in the cell
        cond1 = (x == fox['x']) or (y == fox['y'])
        cond2 = abs(x - fox['x']) == abs(y - fox['y'])
        if cond1 or cond2:
            value += 1

    state['last_shot_result'] = value
    state['shot_count'] += 1

    # Check if we've founded last fox
    if state['hits'] == state['fox_count']:
        # Game over
        state['status'] = 2
        state['time'] = (datetime.now() - state['start_time']).total_seconds()

        # Check if the player got in top
        field = Field.query.filter_by(size=state['field_size'], fox_count=state['fox_count']).one()
        records = field.records.limit(10).all()

        is_in_top_10 = False
        if not records or len(records) < 10:
            is_in_top_10 = True
        else:
            for record in records:
                cond1 = int(state['shot_count']) < record.shot_count
                cond2 = int(state['shot_count']) == record.shot_count and float(state['time']) < record.seconds
                if cond1 or cond2:
                    is_in_top_10 = True
                    break

        if is_in_top_10:
            # Does the player already have a name?
            player_name = session.get('player', '')
            player = None
            if player_name == '':
                # Generate a name for the player
                player = Player(name='FoxHunter')
                db.session.add(player)
                db.session.commit()
                player.name = player.name + str(player.id)
                db.session.commit()
                player_name = player.name
                session['player'] = player_name
            else:
                player = Player.query.filter_by(name=player_name).one()

            record = Record(
                player_id=player.id,
                field_id=field.id,
                shot_count=state['shot_count'],
                seconds=state['time']
            )
            db.session.add(record)
            db.session.commit()
            state['is_in_top_10'] = True

    session['state'] = state

    result = state.copy()
    del result['foxes'] # We don't want to spoil foxes' positions

    return jsonify(result)


@main.route('/records/<int:field_id>')
def get_records(field_id):
    """Return TOP 10 records for selected field"""
    if not request.is_xhr:
        abort(403)

    if field_id == 0:
        field_id = session.get('current_field_id', 2)

    field = Field.query.get(field_id)
    records = field.records.limit(10)
    top_10 = []
    for record in records:
        is_you = False
        current_player = session.get('player', '')
        if current_player == record.player.name:
            is_you = True
        top_10.append(
            {
                'size': field.name,
                'player': record.player.name,
                'shot_count': record.shot_count,
                'seconds': record.seconds,
                'isYou': is_you,
            }
        )

    if not top_10:
        top_10 = [{'size': field.name},]

    return jsonify(top_10)
