from django.test import TestCase
from web.models import ClusterData
from datetime import date, datetime
from django.test.client import Client
import json
import logging
from django.utils.timezone import now
logger = logging.getLogger(__name__)

# TODO: make test for empty cluster 
# {"top_terms":[],"cluster_id":1648,"cluster":"CL-1648{n=1 c=[] r=[]}","points":[]} 

class QueryTest(TestCase):
    def setUp(self):
        for dt in [date(2013,10,01), now().date()]:
            cl = ClusterData()
            cl.date = dt
            cl.range = 1
            cl.created_at = now()
            cl.ml_json = json.dumps(raw_cluster_data(), indent=2)
            cl.save()
        
    def tearDown(self):
        ClusterData.objects.all().delete()
        
    def test_dendogram(self):
        cl = ClusterData.objects.get(pk=1)
        logger.debug("dendogram json: '%s'"%cl.d3_dendogram_json)
        got = json.loads(cl.d3_dendogram_json)
        expected = expected_cluster_dendogram()
        self.assertEquals(expected, got)

    def test_view(self):
        client = Client()
        response = client.get("/")
        self.assertEquals(200, response.status_code)
        print response.context['facets']
        self.assertTrue(response.context['facets'])

    def test_with_date(self):
        client = Client()
        response = client.get("/api/query/%s"%date(2013,10,01).strftime("%Y%m%d"))
        self.assertEquals(200, response.status_code)
        try:
            res = json.loads(response.content)
            self.assertFalse(res.get('trace'),res.get('trace'))
        except:
            self.fail("Failed to parse response from /api/query/")

        self.assertEquals(2, res['num_clusters'])
        logger.debug("dendogram json: '%s'"%res['clusters'])
        expected = expected_cluster_dendogram()
        self.assertEquals(expected,res['clusters'])

        # test with range value in path
        response = client.get("/api/query/%s/1"%date(2013,10,01).strftime("%Y%m%d"))
        self.assertEquals(200, response.status_code)
        try:
            res = json.loads(response.content)
            self.assertFalse(res.get('trace'),res.get('trace'))
        except:
            self.fail("Failed to parse reponse from /api/query/")

        self.assertEquals(2, res['num_clusters'])


    def test_no_date(self):
        client = Client()
        response = client.get("/api/query/")
        self.assertEquals(200, response.status_code)
        try:
            res = json.loads(response.content)
            self.assertFalse(res.get('trace'),res.get('trace'))
        except:
            self.fail("Failed to parse reponse from /api/query/")

        # just verify it returned clusters
        self.assertEquals(2, res['num_clusters'])
        logger.debug("dendogram json: '%s'"%res['clusters'])

    def test_no_results(self):
        client = Client()
        response = client.get("/api/query/%s"%date(2013,10,02).strftime("%Y%m%d"))
        self.assertEquals(200, response.status_code)
        try:
            res = json.loads(response.content)
            self.assertFalse(res.get('trace'),res.get('trace'))
        except:
            self.fail("Failed to parse reponse from /api/query/")

        # just verify it returned clusters
        self.assertEquals(0, res['num_clusters'])
        logger.debug("dendogram json: '%s'"%res['clusters'])

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
          "facets": [
            {
              "term": "romans",
              "count": 2
            }, 
            {
              "term": "proverbs",
              "count": 2
            }
          ],
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


