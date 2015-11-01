from flask import render_template
from flask import Response
from . import main
import json
from ..models import User


@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/search')
def search():
    return render_template('main/search.html')


@main.route('/search/<query>')
def search_query(query):
    users = User.query.all()
    data = dict()
    data["results"] = []
    for u in users:
        data["results"].append({
            "title": u.full_name,
            "url": "/optional/url/on/click"
        })
    json_data = json.dumps(data)
    return Response(response=json_data, status=200,
                    mimetype="application/json")
