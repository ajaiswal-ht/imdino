from flask import Flask, request
from flask.ext.cors import CORS
import json
import redis
r = redis.StrictRedis(host='127.0.0.1', port=6379, db=3)
app = Flask(__name__)
app.config.from_object(__name__)
CORS(app)
@app.route('/')
def get_dino():
    runner = request.args.get('r','{}')
    if runner:
        r.set('p',runner)
    return str('got')

if __name__ == '__main__':
    app.run(debug=False)

