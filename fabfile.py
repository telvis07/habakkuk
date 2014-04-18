from fabric.api import local, settings, env, lcd, cd
import requests
import re
import jsonlib2 as json

def sync_es(target='es-1'):
    with cd('./elasticsearch'):
        local('/home/telvis/bin/stream2es es --source http://localhost:9201/habakkuk-all --target "http://%s:9201/habakkuk-all/"'%target)


def install_es_plugins():
    with cd('/opt/elasticsearch'):
        run("./bin/plugin -install mobz/elasticsearch-head")


def new_index(host="yoyoma", port='9201', alias="habakkuk-all"):
    """
    create a new index by incrementing the revnum and move the alias
    """
    update_template(host, port)


    # get aliases. find the current revnum
    r = requests.get("http://{ESHOST}:{ESPORT}/*/_alias/habakkuk-all".format(ESHOST=host, ESPORT=port))
    data = r.json()
    assert data
    assert len(data) == 1

    # create the next index name
    current_index = data.keys()[0]
    ma = re.match('habakkuk-revnum-(?P<revnum>\d+)', current_index)
    assert ma
    next = int(ma.groups("revnum")[0])+1
    next_index = "habakkuk-revnum-{next}".format(next=next)

    # create next index
    r = requests.put("http://{ESHOST}:{ESPORT}/{INDEX}".format(ESHOST=host, ESPORT=port, INDEX=next_index))
    print "PUT {next_index} return {response}".format(next_index=next_index, response=r.json())

    # move the alias
    alias_cmd = {
        "actions" : [
            { "remove" : { "index" : current_index, "alias" : alias } },
            { "add" : { "index" : next_index, "alias" : alias } }
        ]
    }

    r = requests.post("http://{ESHOST}:{ESPORT}/_aliases".format(ESHOST=host, ESPORT=port), data=json.dumps(alias_cmd))
    print "PUT _alias returned {response}".format(next_index=next_index, response=r.json())


def update_template(host="yoyoma", port='9201'):
    template = 'elasticsearch/habakkuk-template.json'
    r = requests.get("http://{ESHOST}:{ESPORT}/_template/template_habakkuk/".format(ESHOST=host, ESPORT=port), data=open(template).read())
    print "PUT _template returned {code} {response}".format(response=r.json(), code=r.status_code)


def stop_storm():
    local("storm kill habakkuk")

def start_storm():
    with cd('./java/habakkuk-core'):
        local("storm jar target/habakkuk-core-0.0.1-SNAPSHOT-jar-with-dependencies.jar "\
              "technicalelvis.habakkuk.MainTopology habakkuk.properties")
    
