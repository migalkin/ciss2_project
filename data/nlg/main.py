from flask import Flask, request, jsonify
from lib import NLG, Config, Utils
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.debug = True
APP_PATH = app.root_path + '/'

# initialize configurations, charges prices, models
CFG = Config(APP_PATH+'/resources/dev.yml').cfg['nlg']

WHITE_RELATIONS = Utils.get_white_relations(APP_PATH+CFG['white_relations'])
WHITE_RELATIONS = [item[0] for item in WHITE_RELATIONS]


@app.route('/nlg', methods=['GET'])
def nlg():
    """
    predict delivery time of input transaction
    :return: json delivery time and corresponding error range
    """
    version, s, p, o, lang = request.args['version'], request.args['s'], request.args['p'], request.args['o'], request.args['lang']
    triple = (s, p, o)
    if version == "2016":
        template_res = NLG.templates(csv_path=APP_PATH + CFG['template'], triple=triple, nlg_cfg=CFG, version=version)
    elif version == "2018":
        if lang == "en":
            template_res = NLG.templates(csv_path=APP_PATH + CFG['dbp2018_verbalisations'], triple=triple, nlg_cfg=CFG, version=version, lang=lang)
        else:
            template_res = NLG.templates(csv_path=APP_PATH + CFG['dbp2018_verbalisations_de'], triple=triple, nlg_cfg=CFG,
                                         version=version, lang=lang)
    if template_res is None:
        return jsonify({'nl': ""})
    else:
        return jsonify({'nl': template_res})


@app.route('/relations', methods=['GET'])
def relations():
    """
    return white list of relations for input entities
    :return:
    """
    entity = request.args['entity']
    white_relations = NLG.get_white_relations(entity, WHITE_RELATIONS, nlg_cfg=CFG)
    return jsonify({'white_relations': white_relations})


if __name__ == '__main__':
    """
    configure the ip and port where the application should run on
    """
    app.run(host='0.0.0.0', port=5050)
