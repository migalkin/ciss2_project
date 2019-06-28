# coding=utf-8

from flask import Flask, render_template
from flask_cors import CORS


from src.lib import Config

# Required for video (VR) demo

from werkzeug.routing import Rule

#import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')

app = Flask(__name__)
CORS(app)
APP_PATH = app.root_path + '/'

# Config file, containing webserver and website configurations
CFG = Config(APP_PATH+'resources/conf.yml').cfg

# Configuration for the webserver
APP_CFG = CFG['app']

# Configuration for the frontend
DM_CFG = CFG['dm']
DM_CFG = Config.load_env_conf(DM_CFG)


@app.route('/')
def root():
    return render_template('home.html', app_config=DM_CFG)


if __name__ == '__main__':
    print(APP_CFG['cert'])
    print(APP_CFG['key'])
    app.run(debug=True, port=APP_CFG['port'], host=APP_CFG['host']) #, ssl_context='adhoc'
