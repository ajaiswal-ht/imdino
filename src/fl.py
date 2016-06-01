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
        #print json.dumps(runner)
        #score = int(runner.get('distanceRan')*.025)
        #highestScore = runner.get('highestScore')
        #speed = runner.get("currentSpeed")
        #speed = speed/13
        #obs = horizon['obstacles']
        #no_of_obstacles = len(obs)
        #nearest_size = None
        #nearest_distance = None
        #second_size = None
        #second_distance = None
        #if no_of_obstacles > 0:
        #    nearest = obs[0]
        #    nearest_size = nearest['width']/60.0
        #    nearest_distance = nearest['xPos']/50.0
        #if no_of_obstacles>1:
        #    second = obs[1]
        #    second_size = second['width']/60.0
        #    second_distance = nearest['xPos']/50.0
        #d = {
        #        'sc':score,'o':over, 's':speed, 'n':no_of_obstacles, 'fs':nearest_size,'ss':second_size,'sd':second_distance,'fd':nearest_distance
        #        }
        print runner
        r.set('p',runner)
    return str('got')

if __name__ == '__main__':
    app.run(debug=True)

