from django.test import TestCase
from api.models import ClusterData
from datetime import date, datetime
from django.test.client import Client
import json
import logging
logger = logging.getLogger(__name__)

# TODO: timezone
class QueryTest(TestCase):
    def setUp(self):
        pass
        
    def tearDown(self):
        ClusterData.objects.all().delete()
        
    def test_dendogram(self):
        cl = ClusterData()
        cl.date = date(2013,10,01)
        cl.range = 1
        cl.created_at = datetime.now()
        cl.ml_json = json.dumps(raw_cluster_data(), indent=2)
        cl.save()

        cl = ClusterData.objects.get(pk=1)
        logger.info("dendogram json: '%s'"%cl.d3_dendogram_json)
        got = json.loads(cl.d3_dendogram_json)
        expected = expected_cluster_dendogram()
        self.assertEquals(expected, got)

def raw_cluster_data():
    return  \
    [
     {
      "cluster": "VL-1{n=5924 c=[genesis:0.000, exodus:0.009, ...]}",
      "cluster_id": 1,
      "points": [
        {
          "vector_name": "user1",
          "weight": "1.0",
          "point": "user1 = [proverbs:1.000]"
        },
        {
          "vector_name": "user2",
          "weight": "1.0",
          "point": "user2 = [proverbs:1.000]"
        },
      ],
      "top_terms": [
        {
          "term": "proverbs",
          "weight": 0.19125590817015531
        },
        {
          "term": "romans",
          "weight": 0.16306549628629305
        }
      ],
      "hk_topics": [
        {
          "term": "TODO",
        },
        {
          "term": "TODO AGAIN",
        }
      ],

    },
    {
      "cluster": "VL-2{n=5924 c=[genesis:0.000, exodus:0.009, ...]}",
      "cluster_id": 2,
      "points": [
        {
          "vector_name": "user2",
          "weight": "1.0",
          "point": "user2 = [proverbs:1.000]"
        },
        {
          "vector_name": "user3",
          "weight": "1.0",
          "point": "user3 = [proverbs:1.000]"
        },
      ],
      "top_terms": [
        {
          "term": "romans",
          "weight": 0.19125590817015531
        },
        {
          "term": "proverbs",
          "weight": 0.16306549628629305
        }
      ],
      "hk_topics": [
        {
          "term": "TODO",
        },
        {
          "term": "TODO AGAIN",
        }
      ],

    }
    ]


    
def expected_cluster_dendogram():
    return \
        {
          "name": "2013-10-01, 1 day range", 
          "facets": {
                "romans": 2, 
                "proverbs": 2
          }, 
          "children": [
            {
              "name": "proverbs", 
              "size": 2,
              "children": [
                {
                  "name": "'proverbs' topics", 
                  "size": 1,
                  "children": [
                    {
                      "name": "TODO", 
                      "children": []
                    },
                    {
                      "name": "TODO AGAIN", 
                      "children": []
                    }
                  ], 
                }, 
                {
                  "name": "bibleverses (2)", 
                  "size": 2,
                  "children": [
                    {
                      "name": "proverbs", 
                      "children": []
                    }, 
                    {
                      "name": "romans", 
                      "children": []
                    }
                  ], 
                }
              ], 
            }, 
            {
              "name": "romans", 
              "size": 2,
              "children": [
                {
                  "name": "'romans' topics", 
                  "size": 1,
                  "children": [
                    {
                      "name": "TODO", 
                      "children": []
                    },
                    {
                      "name": "TODO AGAIN", 
                      "children": []
                    }
                  ], 
                }, 
                {
                  "name": "bibleverses (2)", 
                  "size": 2,
                  "children": [
                    {
                      "name": "romans", 
                      "children": []
                    }, 
                    {
                      "name": "proverbs", 
                      "children": []
                    }
                  ], 
                }
              ], 
            }
          ]
        }


