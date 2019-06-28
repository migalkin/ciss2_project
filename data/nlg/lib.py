import re
import csv
import yaml
import json
import requests
from urllib.parse import urlparse
from filterClasses import filterClasses


class Config:
    """
    load configuration files
    """

    def __init__(self, path_to_config='../config.yml'):
        self.cfg = self.load_config(path_to_config=path_to_config)

    @staticmethod
    def load_config(path_to_config):
        try:
            with open(path_to_config, 'r') as config:
                return yaml.load(config)
        except IOError as e:
            raise e


class Utils:
    """
    tools used in common
    """

    def __init__(self):
        pass

    @staticmethod
    def clean_str(reply):
        if isinstance(reply, tuple):
            return reply
        """
        Tokenization/string cleaning for all datasets except for SST.
        """

        reply = re.sub(r"\. \. \.", "\.", reply)
        reply = re.sub(r"[^A-Za-z0-9(),!?\'\`\.]", " ", reply)
        # string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
        reply = re.sub(r"\'s", " \'s", reply)
        reply = re.sub(r"\'ve", " \'ve", reply)
        reply = re.sub(r"n\'t", " n\'t", reply)
        reply = re.sub(r"\'re", " \'re", reply)
        reply = re.sub(r"\'d", " \'d", reply)
        reply = re.sub(r"\'ll", " \'ll", reply)
        reply = re.sub(r",", " , ", reply)
        reply = re.sub(r"!", " ! ", reply)
        reply = re.sub(r"\(", " ( ", reply)
        reply = re.sub(r"\)", " ) ", reply)
        reply = re.sub(r"\?", " ? ", reply)
        reply = re.sub(r"\s{2,}", " ", reply)
        return reply.strip().lower()

    @staticmethod
    def parse_templates(csv_path):
        csv_dict = {}
        with open(csv_path, 'r') as csv_file:
            for item in csv.DictReader(csv_file):
                if item['Templates'] != '':
                    csv_dict[item['Relations']] = {}
                    replaced_x = re.sub(r"\b%s\b" % 'x', 'X', item['Templates'])
                    replaced_y = re.sub(r"\b%s\b" % 'y', 'Y', replaced_x)
                    csv_dict[item['Relations']]["single"] = replaced_y
                    replaced_x = re.sub(r"\b%s\b" % 'x', 'X', item['Plural Templates'])
                    replaced_y = re.sub(r"\b%s\b" % 'y', 'Y', replaced_x)
                    csv_dict[item['Relations']]["plural"] = replaced_y
        return csv_dict

    @staticmethod
    def get_white_relations(csv_path):
        white_relations = []
        with open(csv_path, 'rt') as csv_file:
            for item in csv.DictReader(csv_file):
                white_relations.append((item['Relations'], item['Labels']))
        return white_relations


class NLG:

    def __init__(self):
        pass

    @staticmethod
    def triple_2_nl(triple, api):
        """
        use triple 2 nl
        :param triple:
        :param api:
        :return:
        """
        subject, predicate, objects = triple[0], triple[1], triple[2]
        url = api + '?s=' + subject + '&p=' + predicate + '&o=' + objects
        print(url)
        result = requests.get(url)
        return result

    @staticmethod
    def simple_nl(triple):
        """
        use simple nl
        :param triple:
        :return:
        """
        subject = urlparse(triple[0])[2].rpartition('/')[-1]
        predicate = urlparse(triple[1])[2].rpartition('/')[-1]
        objects = []
        for obj in triple[2].split(','):
            objects.append(urlparse(obj)[2].rpartition('/')[-1])
        data = {
            "sentence":
                {
                    "subject": subject,
                    "verb": predicate,
                    "object": {
                        "type": "coordinated_phrase",
                        "coordinates": objects
                    }
                }
        }
        result = requests.post('http://localhost:8300/generateSentence', json=data)
        return result

    @staticmethod
    def get_label(entity, nlg_cfg, version, lang):
        query = "select DISTINCT ?o where {<"+entity+"> rdfs:label ?o. " \
                                                     "BIND(datatype(?o) as ?dt) " \
                                                     "FILTER(IF(isliteral(?o) && !bound(?dt), langMatches(lang(?o),'"+lang+"'), true))}"
        path = ""
        if version == "2016":
            path = nlg_cfg['endpoint']
        elif version == "2018":
            path = nlg_cfg['dbp2018_endpoint']
        label = requests.get(url=path,
                             params={'query': query},
                             headers={'Accept': "application/json"})
        json_label = json.loads(label.content)
        if len(json_label['results']['bindings']) > 0:
            return json_label['results']['bindings'][0]['o']['value']
        else:
            return urlparse(entity)[2].rpartition('/')[-1]

    @staticmethod
    def templates(csv_path, triple, nlg_cfg, version, lang):
        """
        use template verbalization
        :param csv_path:
        :param triple:
        :param nlg_cfg
        :param version
        :return:
        """
        relation_template_dict = Utils.parse_templates(csv_path=csv_path)
        if triple[1] in relation_template_dict.keys():  # if relation is there
            subject = triple[0]
            if 'http' in subject:
                subject = NLG.get_label(subject, nlg_cfg=nlg_cfg, version=version, lang=lang)
            objects = []
            for obj in triple[2].split(','):
                if 'http' in obj:
                    objects.append(NLG.get_label(obj, nlg_cfg=nlg_cfg, version=version, lang=lang))
                else:
                    objects.append(obj)
            if len(objects) <= 1:
                template = relation_template_dict[triple[1]]["single"]
                replaced_x = re.sub(r"\b%s\b" % 'X', subject, template)
                replaced_y = NLG.replace_objects(replaced_x, template, objects)
                return replaced_y
            else:
                template = relation_template_dict[triple[1]]["plural"]
                replaced_x = re.sub(r"\b%s\b" % 'X', subject, template)
                replaced_y = NLG.replace_objects(replaced_x, template, objects)
                return replaced_y
        return None

    @staticmethod
    def has_subclass(entity, cfg):
        """
        check whether entity has subclass
        :param entity:
        :param cfg: sparql endpoint
        :return:
        """
        query = "select (COUNT(DISTINCT ?s) AS ?count) where {?s rdfs:subClassOf <"+entity+">. }"
        result = requests.get(url=cfg['endpoint'],
                             params={'query': query},
                             headers={'Accept': "application/json"})
        print(result.content)
        subclass_count = json.loads(result.content)
        if int(subclass_count['results']['bindings'][0]['count']['value']) == 0:
            return False
        else:
            return True

    @staticmethod
    def replace_objects(replaced_subject, template, objects):
        # key_words = {'Y has': 'have', 'Y is': 'are', 'Y was': 'were'}
        # key_exist, value = NLG.key_in_string(key_words, template)
        # if len(objects) > 1 and key_exist:
        #     return re.sub(r"\b%s\b" % value, ', '.join(objects) + ' ' + key_words[value], replaced_subject)
        # else:
        #     return re.sub(r"\b%s\b" % 'Y', ', '.join(objects), replaced_subject)
        if len(objects) > 1:
            return re.sub(r"\b%s\b" % 'Y', ', '.join(objects[:-1]) + ' and ' + objects[-1], replaced_subject)
        else:
            return re.sub(r"\b%s\b" % 'Y', ', '.join(objects), replaced_subject)

    @staticmethod
    def key_in_string(dictionary, template):
        for key in dictionary.keys():
            if key in template:
                return True, key
        return False, None

    @staticmethod
    def get_white_relations(entity, white_relations, nlg_cfg):
        entity_white_relations = []
        query = "select distinct ?p  where {<" + entity + "> ?p ?o. " \
                                                          "BIND(datatype(?o) as ?dt) " \
                                                          "FILTER(IF(isliteral(?o) && !bound(?dt), " \
                                                          "langMatches(lang(?o),'en'), true))}"
        relations = requests.get(url=nlg_cfg['endpoint'],
                             params={'query': query},
                             headers={'Accept': "application/json"})
        json_relations = json.loads(relations.content)
        for binding in json_relations['results']['bindings']:
            if binding['p']['value'] in white_relations:
                entity_white_relations.append(binding['p']['value'])
        return entity_white_relations

    @staticmethod
    def get_objects(entity, relation, nlg_cfg):
        print("NewRelation: {}".format(relation))
        objects_list = []
        query_object = "select ?o where {<" + entity + "> <" + relation + "> ?o. " \
                       "BIND(datatype(?o) as ?dt) " \
                       "FILTER(IF(isliteral(?o) && !bound(?dt), " \
                       "langMatches(lang(?o),'en'), true))}"
        objects = requests.get(url=nlg_cfg['endpoint'],
                             params={'query': query_object},
                             headers={'Accept': "application/json"})
        json_objects = json.loads(objects.content)
        for obj in json_objects['results']['bindings']:
            print(obj['o']['value'])
            objects_list.append(obj['o']['value'])
        print('Number of objects: ' + str(len(objects_list)))
        if relation == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
            print('Relation: {}'.format(relation))
            new_objects_list = []
            for objj in objects_list:
                if "http" in objj:
                    if 'http://dbpedia.org/ontology' in objj: # or ('class' in objj and NLG.has_subclass(objj, cfg=nlg_cfg) is False)
                        new_objects_list.append(objj)
            print(new_objects_list)
            objects_list = filterClasses(new_objects_list, 1)
            # objects_list = new_objects_list
        if len(objects_list) > 0:
            return ','.join(objects_list)
        return None

    @staticmethod
    def nl_from_triple(triple, api, template_csv, nlg_cfg):
        """
        triple to nl, use template verbalization first
        :param triple:
        :param api:
        :param template_csv:
        :return:
        """

        # print (triple)
        if len(triple) != 3:
            raise ValueError
        template_res = NLG.templates(csv_path=template_csv, triple=triple, nlg_cfg=nlg_cfg)
        if template_res is None or template_res == '.':  # template should cover all the cases
            #result = NLG.triple_2_nl(triple=triple, api=api)
            #json_label = json.loads(result.content)
            #return json_label['nl']
            raise ValueError
        else:
            return template_res

    @staticmethod
    def get_triple_nl(entities, white_relations, nlg_cfg):
        entity_relations_objects = []
        for entity in entities:
            s_white_relations = NLG.get_white_relations(entity,
                                                        white_relations=white_relations,
                                                        nlg_cfg=nlg_cfg)
            for relation in s_white_relations:
                objs = NLG.get_objects(entity=entity,
                                       relation=relation,
                                       nlg_cfg=nlg_cfg)
                if objs is not None:
                    nl = NLG.nl_from_triple(triple=(entity, relation, objs),
                                            api=nlg_cfg['api'],
                                            template_csv=nlg_cfg['template'],
                                            nlg_cfg=nlg_cfg)
                    entity_relations_objects.append((nl, entity + ';' + relation + ';' + objs))
        return entity_relations_objects
