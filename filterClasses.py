import requests
import operator
import json


def filterClasses(listClasses, topk):
    endpoint = "http://dbpedia.org/sparql"
    queryTemplate = "SELECT COUNT(distinct ?class) as ?num WHERE {{ <{0!s}> rdfs:subClassOf* ?class }} "

    matching = {}

    for cl in listClasses:
        query = queryTemplate.format(cl)
        answer = requests.get(url=endpoint,
                             params={'query': query},
                             headers={'Accept': "application/json"})

        if answer:
            json_answer = json.loads(answer.content)
            num = json_answer["results"]["bindings"][0]["num"]["value"]
            matching[cl] = num
        else:
            matching[cl] = 0

    sorted_matching = sorted(matching.items(), key=operator.itemgetter(1))
    val_set = set([int(item[1]) for item in sorted_matching])
    top_values = sorted(val_set)[-topk:]


    output = [item for item in sorted_matching if int(item[1]) in top_values]
    output_names = [k for k, v in output]

    return output_names


if __name__ == '__main__':
    filterClasses(["dbo:Building", "dbo:Place", "dbo:Place", "dbo:ArchitecturalStructure"], 1)
