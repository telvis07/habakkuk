from fabric.api import local, settings, env, lcd
from datetime import date, datetime, timedelta
import os
from fabric.contrib import django
import json
django.project('habakkuk')
from web.models import ClusterData
from web.cluster_topics import find_topics
import logging
logger = logging.getLogger(__name__)

def config():
    # TODO: add fabricrc
    vars = {
        'hk.data':env.get('hk.data','/opt/habakkuk_data/'),
        'hk.input':env.get('hk.input','input'),
        'hk.book_vectors':env.get('hk.book_vectors','book_vectors'),
        'hk.named_vectors':env.get('hk.named_vectors','book_vectors-nv'),
        'hk.pig_script':env.get('hk.pig_script', 'book_vectors.pig'),
        'hk.mahout.num_clusters':env.get('hk.mahout.num_clusters','10'),
        'hk.mahout.num_iterations':env.get('hk.mahout.num_iterations','5'),
        'hk.mahout.output':env.get('hk.mahout.output','clusters'),
        'hk.mahout.metric':env.get('hk.mahout.metric','org.apache.mahout.common.distance.CosineDistanceMeasure'),
        'hk.mahout.converge':env.get('hk.mahout.converge','0.1'),
        'hk.mahout.dump.terms':env.get('hk.mahout.dump.terms','10'),
        'hk.mahout.dump.json':env.get('hk.mahout.dump.json','/tmp/clusterdump.json'),
        'hk.mahout.dump.text':env.get('hk.mahout.dump.text','/tmp/clusterdump.txt'),
    }
    return vars


def make_dirs():
    vars = config()
    # input dir
    with settings(warn_only=True):
        ret = local('hadoop fs -test -d %(hk.input)s'%vars)

    if ret.succeeded:
        local('hadoop fs -rmr %(hk.input)s'%vars)

    local('hadoop fs -mkdir %(hk.input)s'%vars)

    with settings(warn_only=True):
        local('hadoop fs -rmr %(hk.book_vectors)s'%vars)
        local('hadoop fs -rmr %(hk.named_vectors)s'%vars)
    local('hadoop fs -mkdir %(hk.named_vectors)s'%vars)

def prepare_data(date_str, range):
    vars = config()
    days = int(range)
    make_dirs()

    dt = datetime.strptime(date_str, '%Y-%m-%d').date()
    et = dt + timedelta(days=-range)
    while dt>et:
        _date = dt.strftime('%Y-%m-%d')
        fn = os.path.join(vars['hk.data'], 'habakkuk-%s.json.gz'%_date)
        local('hadoop fs -copyFromLocal %s input'%fn)
        dt-=timedelta(days=1)

    local("hadoop fs -ls %(hk.input)s"%vars)

def run_pig_job():
    vars = config()
    with lcd('analysis'):
        local('pig -p data=%(hk.input)s -p output=%(hk.book_vectors)s %(hk.pig_script)s'%vars)

def named_vectors():
    vars = config()
    local("hadoop jar " \
          "./java/elephant-bird-vector-converter/target/elephant-bird-vector-converter-0.1-SNAPSHOT-job.jar " \
          "technicalelvis.elephantBirdVectorConverter.App %(hk.book_vectors)s/ %(hk.named_vectors)s/"%vars)

def run_mahout_job():
    vars = config()
    local('hadoop fs -rmr %(hk.mahout.output)s'%vars)
    local("mahout kmeans -i %(hk.named_vectors)s -c kmeans-initial-clusters "\
          "-k %(hk.mahout.num_clusters)s -o %(hk.mahout.output)s "\
          "-x %(hk.mahout.num_iterations)s -ow -cl -dm %(hk.mahout.metric)s "\
          "-cd %(hk.mahout.converge)s "%vars)

def clusterdump_json():
    vars = config()
    # mahout patched with https://issues.apache.org/jira/browse/MAHOUT-1343
    with lcd('analysis'):
        local("/var/hadoop/mahout-patched-0.8/bin/mahout clusterdump -d ./join_data/book.dictionary "\
              "-dt text -i clusters/clusters-*-final -p clusters/clusteredPoints "\
              "-n %(hk.mahout.dump.terms)s -o %(hk.mahout.dump.json)s -of JSON"%vars)

def clusterdump_text():
    vars = config()
    # mahout patched with https://issues.apache.org/jira/browse/MAHOUT-1343
    local("/var/hadoop/mahout-patched-0.8/bin/mahout clusterdump -d ./join_data/book.dictionary "\
          "-dt text -i clusters/clusters-*-final -p clusters/clusteredPoints "\
          "-n %(hk.mahout.dump.terms)s -o %(hk.mahout.dump.text)s -of TEXT"%vars)

def run_clustering(date_str=None, range='1'):
    vars = config()
    if not date_str:
        dt = date.today() - timedelta(days=1)
        date_str = dt.strftime('%Y-%m-%d')
    else:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
    range=int(range)

    prepare_data(date_str, range)
    run_pig_job()
    named_vectors()
    run_mahout_job()
    clusterdump_json()
    save_cluster_data(date_str, range, vars['hk.mahout.dump.json'])

def save_cluster_data(date_str, range, fn):
    dt = datetime.strptime(date_str, "%Y-%m-%d").date()
    range = int(range)

    if ClusterData.objects.filter(date=date_str, range=range):
        cl = ClusterData.objects.filter(date=date_str, range=range)[0]
        print "updating existing cluster data"
    else:
        cl = ClusterData()

    cl.date = dt
    cl.range = range
    cl.created_at = datetime.now()
    clusters = []
    for line in file(fn):
        data = json.loads(line)
        data['hk_topics'] = find_topics(data)
        clusters.append(data)
    cl.ml_json = json.dumps(clusters, indent=2)
    cl.save()

def print_clusters():
    print("Found %d clusters"%len(ClusterData.objects.all()))
    for cl in ClusterData.objects.all():
        print cl
