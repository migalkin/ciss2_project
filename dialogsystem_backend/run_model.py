import spacy
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.neighbors import NearestNeighbors
import numpy as np
import pickle as pkl
import json
import requests
import urllib
import faiss
import scipy

nlp = spacy.load('en')
s_index = json.load(open("data/core_index.json","r"))
sub_embeddings = np.genfromtxt(fname="data/out.tsv", delimiter="\t", skip_header=0)[:,1:]
pred_embeddings = np.genfromtxt(fname="data/filtered_props.tsv", delimiter="\t", skip_header=0)[:,1:]

#nbrs = NearestNeighbors(10)
#nbrs.fit(sub_embeddings)
index = faiss.IndexFlatIP(200)
print(index.is_trained)
index.add(np.ascontiguousarray(sub_embeddings.astype('float32')))

entityuri2id = json.load(open("e2id.json","r"))
predicateuri2id = json.load(open("p2id.json","r"))
id2entity = json.load(open("id2e.json","r"))
id2predicate = json.load(open("id2p.json","r"))

input_sentence = "Who is the father of Barack Obama?"


def run_ner(sentence):
    doc = nlp(sentence)
    ents_extrd = []
    for ent in doc.ents:
        print(ent.label_)
        if ent.label_ in ["PERSON", "ORG", "NORP", "FAC", "GPE", "LOC", "PRODUCT", "EVENT", "WORK_OF_ART"]:
            ents_extrd.append(ent.text)
    return ents_extrd


def subject_lookup(entity):
    return s_index[entity][0]


def find_relation(sentence):
    return "http://www.wikidata.org/entity/P25"


def get_embeddings(e, r):
    entity_ind = entityuri2id["<" + e + ">"]
    relation_index = predicateuri2id["<" + r + ">"]

    return sub_embeddings[entity_ind], pred_embeddings[relation_index]


def find_objects(emb, number):
    emb = emb.reshape(1, -1)
    # indices = nbrs.kneighbors(emb, return_distance=True
    d, indices = index.search(emb.astype('float32'), 30)
    # print(indices)
    print(d)
    uri = [id2entity[str(e)] for e in indices[0]]
    return [get_label(u) for u in uri]


def get_label(uri):
    query = """
    SELECT ?l WHERE {{
       {0!s} rdfs:label ?l FILTER (lang(?l)='en')
    }}
    """.format(uri)
    address = "http://query.wikidata.org/sparql"
    params = urllib.parse.urlencode({"query": query, "format": "json"})
    r = requests.get(address, params=params, headers={'User-Agent': 'CISS2 agent'})
    try:
        results = json.loads(r.text)
        return results["results"]["bindings"][0]["l"]["value"]
    except Exception:
        raise Exception("Smth is wrong with the endpoint")


def nlg(s, p, o):
    return "{0!s} {1!s} {2!s}".format(s, p, o)


def dm(sentence):
    # run coref
    # entity_uri, relation_uri = run_coref(sentence)
    # if/else

    # run NER
    entity = run_ner(sentence)[0]
    print(u"Identified entity: {0!s}".format(entity))

    # index lookup
    entity_uri = subject_lookup(entity)
    print(u"Identified entity URI: {0!s}".format(entity_uri))

    # relation linking
    relation_uri = find_relation(sentence)
    print(u"Identified relation URI: {0!s}".format(relation_uri))

    # get s + p embeddings
    e, r = get_embeddings(entity_uri, relation_uri)
    us = sub_embeddings[entityuri2id["<http://www.wikidata.org/entity/Q766106>"]]

    # object emb
    # print(e)
    # print(r)
    object_embedding = e + r
    os = sub_embeddings + r
    scores = e.reshape((1, 200)) @ os.transpose()
    print([id2entity[str(r)] for r in np.argsort(scores.flatten())[-25:]])
    ranks = np.argsort(np.argsort(scores.flatten()))
    # print(ranks[entityuri2id["<http://www.wikidata.org/entity/Q766106>"]])
    #     print(object_embedding @ us.transpose())

    # kNN in embedding space
    # closest_objects = find_objects(object_embedding, 20)
    # print(u"Closest object: {}".format(closest_objects))

    # get labels of p, o
    p_label = get_label("<" + relation_uri + ">")
    # o_label = get_label("<+o+">")

    # verbalize
    answer = nlg(entity, p_label, closest_objects)

    return answer