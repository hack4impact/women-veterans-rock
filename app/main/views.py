from flask import render_template
from flask import Response
from . import main
import json
from ..models import User
from flask.ext.login import login_required


@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/users')
@login_required
def user_map():
    return render_template('main/map.html', users=User.query.all())


@main.route('/search/<query>')
@login_required
def search_query(query):
    looking_for = '%'+query+'%'
    users = User.query.filter((User.first_name.ilike(looking_for)) |
                              User.last_name.ilike(looking_for))\
        .order_by(User.first_name).all()
    data = dict()
    data['results'] = [{'title': u.full_name(),
                        'url': '/account/profile/' + str(u.id)} for u in users]
    json_data = json.dumps(data)
    return Response(response=json_data, status=200,
                    mimetype='application/json')


@main.route('/help')
def help():
    return render_template('main/help.html')
