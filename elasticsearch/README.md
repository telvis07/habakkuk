This directory contains convenience scripts to perform an faceted search queries against ES.

## setup clusters index

  vim topics-template.json 
  curl -XDELETE yoyoma:9201/topics-all
  curl -XPUT 'http://192.168.117.4:9201/_template/template_topics/' -d @topics-template.json 
  curl -XPUT http://192.168.117.4:9201/topics-all


## Dir Setup

````
    6  sudo mkdir -p /data0/elasticsearch-1
    7  cd /data0/elasticsearch-1/
    8  mkdir -p config data logs run work
    9  cd /opt/
    11  yum install wget
   12  wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.0.1.tar.gz
   13  tar xf elasticsearch-1.0.1.tar.gz
   14  ln -s /opt/elasticsearch-1.0.1 /opt/elasticsearch
   15  useradd -r -s /bin/bash -d /opt/elasticsearch elasticsearch
   [root@es-1 ~]# chown -R elasticsearch:elasticsearch /data0/elasticsearch-1/
[root@es-1 ~]# chown -R elasticsearch:elasticsearch /opt/elasticsearch
[root@es-1 ~]# chown -R elasticsearch:elasticsearch /opt/elasticsearch-1.0.1
````



````
     1017  sudo mkdir -p /data0/elasticsearch-1
 1018  cd data0/elasticsearch-1/
 1019  cd
 1020  cd /opt/
 1021  sudo tar xf ~/Downloads/elasticsearch-1.0.0.RC2.tar.gz
 1022  sudo ln -s /opt/elasticsearch-1.0.0.RC2/ elasticsearch
 1023  cd elasticsearch
 1024  ls
 1025  sudo mkdir -p config data logs run work
 1026  ls
 1027  cd ../
 1028  rm -rf elasticsearch-1.0.0.RC2/
 1029  sudo rm -rf elasticsearch-1.0.0.RC2/
 1030  sudo tar xf ~/Downloads/elasticsearch-1.0.0.RC2.tar.gz
 1031  ls
 1032  cd elasticsearch
 1033  ls
 1034  cd /data0/
 1035  cd elasticsearch-1/
 1036  sudo mkdir -p config data logs run work
 1037  ls
 1038  cd config/
 1039  vim elasticsearch.yml
 1040  sudo vim elasticsearch.yml
 1041  sudo cp /opt/elasticsearch/config/logging.yml .
 1042  cd
 1043  cd /etc/supervisord.conf.d/
 1044  ls
 1045  vim elasticsearch-1.conf
 1046  which java
 1047  sudo vim elasticsearch-1.conf
 1048  sudo useradd -r elasticsearch
 1049  cd
 1050  cd /data0/
 1051  ls
 1052  grep elasticsearch /etc/group
 1053  sudo chown -R elasticsearch:elasticsearch elasticsearch-1/
 1054  sudo chown -R elasticsearch:elasticsearch /opt/elasticsearch-1.0.0.RC2/
 1055  sudo chown -R elasticsearch:elasticsearch /opt/elasticsearch
 1056  usermod -h
 1057  sudo usermod -h
 1058  sudo usermod -d /opt/elasticsearch elasticsearch
 1059  cat /etc/supervisord.conf.d/elasticsearch-1.conf
 wget http://download.elasticsearch.org/kibana/kibana/kibana-latest.zip
 mkdir /opt/kibana
 sudo chown -R elasticsearch:elasticsearch /opt/kibana/


 ````

## Plugins

    # FYI: Use './bin/plugin -remove' to remove old plugins
    ./bin/plugin -install mobz/elasticsearch-head
    ./bin/plugin -install elasticsearch/marvel/latest

## To Bulk Load

    python bulk_load.py -H yoyoma:9201 -i /tmp/habakkuk_data/habakkuk-2014-04-09.json.gz
    # or
    python bulk_load.py -H yoyoma:9201 -i /tmp/habakkuk_data/

## Example
To get the data for Valentines day 2013,  I execute the following

    $ python bible_facet.py -s 2013-02-14 -e 2013-02-15

It shows the raw query json for the 
[Elasticsearch Query DSL](http://www.elasticsearch.org/guide/reference/query-dsl/index.html). 
Below that it shows the top 10 bible references. Its basically just a faceted search on the 
bibleverse field.

    {
      "query": {
        "filtered": {
          "filter": {
            "range": {
              "created_at_date": {
                "to": "2013-02-15T00:00:00",
                "include_upper": false,
                "from": "2013-02-14T00:00:00"
              }
            }
          },
          "query": {
            "match_all": {}
          }
        }
      },
      "facets": {
        "bibleverse": {
          "terms": {
            "field": "bibleverse",
            "order": "count",
            "size": 10
          }
        }
      },
      "size": 0
    }
    Total bibleverse 1568
        john 3:16 85
        i_john 4:19 42
        i_corinthians 13:4 31
        i_corinthians 13:13 24
        john 14:23 19
        psalm 37:23 18
        john 15:13 18
        i_corinthians 13:7 18
        philippians 4:13 17
        romans 5:8 15


## Files
* bible_facet.py - script used for simple faceted search
* dump_data_for_date.py - I use this to dump data each day to prevent data loss - lucene indexes can be fickle. Basically,
I execute the following every day. 

    $  python dump_data_for_date.py -s `date +"%F" --date "yesterday"` -o /path/to/backup/habakkuk_data/
* habakkuk-template.json and set-template.sh are to set the index template for habakkuk data stored in ES. Just execute the following
to set it up.    

    $ sh set-template.sh habakkuk-template.json
