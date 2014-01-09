from django.test import TestCase
from django.conf import settings
from web.models import ClusterData
from web.views import DEFAULT_RANGE
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
        ClusterData.objects.all().delete()
        for dt in [date(2013,10,01), now().date()]:
            cl = ClusterData()
            cl.date = dt
            cl.range = DEFAULT_RANGE
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

    def test_clusters_view(self):
        """ test the clusters view """
        client = Client()
        response = client.get("/clusters/")
        self.assertEquals(200, response.status_code)
        logger.debug("Facets: %s"%response.context['facets'])
        logger.debug("Clusters: %s"%response.context['clusters'])
        self.assertTrue(response.context['facets'])
        self.assertTrue(response.context['clusters'])

    def test_bible_study_view(self):
        """ test the bible study view """
        client = Client()
        response = client.get("/biblestudy/")
        self.assertEquals(200, response.status_code)

    def test_default_redirect(self):
        """ should redirect to clusters """
        client = Client()
        response = client.get("/")
        self.assertEquals(301, response.status_code)

        # verify I still get data after the redirect
        response = client.get("/", follow=True)
        self.assertEquals([('http://testserver/biblestudy/', 301)], response.redirect_chain)
        self.assertEquals(200, response.status_code)

    def test_data_with_date(self):
        client = Client()
        response = client.get("/api/clusters/%s"%date(2013,10,01).strftime("%Y%m%d"))
        self.assertEquals(200, response.status_code)
        try:
            res = json.loads(response.content)
            self.assertFalse(res.get('trace'),res.get('trace'))
        except:
            self.fail("Failed to parse response from /api/clusters/")

        self.assertEquals(2, res['num_clusters'])
        logger.debug("dendogram json: '%s'"%res['clusters'])
        expected = expected_cluster_dendogram()
        self.assertEquals(expected,res['clusters'])

        # test with range value in path
        response = client.get("/api/clusters/%s/%s"%(date(2013,10,01).strftime("%Y%m%d"),DEFAULT_RANGE))
        self.assertEquals(200, response.status_code)
        try:
            res = json.loads(response.content)
            self.assertFalse(res.get('trace'),res.get('trace'))
        except:
            self.fail("Failed to parse reponse from /api/clusters/")

        self.assertEquals(2, res['num_clusters'])

    def test_data_no_date(self):
        client = Client()
        response = client.get("/api/clusters/")
        self.assertEquals(200, response.status_code)
        try:
            res = json.loads(response.content)
            self.assertFalse(res.get('trace'),res.get('trace'))
        except:
            self.fail("Failed to parse reponse from /api/clusters/")

        # just verify it returned clusters
        self.assertEquals(2, res['num_clusters'])
        logger.debug("dendogram json: '%s'"%res['clusters'])

    def test_data_no_results(self):
        client = Client()
        response = client.get("/api/clusters/%s"%date(2013,10,02).strftime("%Y%m%d"))
        self.assertEquals(200, response.status_code)
        try:
            res = json.loads(response.content)
            self.assertFalse(res.get('trace'),res.get('trace'))
        except:
            self.fail("Failed to parse reponse from /api/clusters/")

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
      "date": "2013-10-01",
      "range": 7,
      "facets": [
        {
          "count": 2,
          "term": "romans"
        },
        {
          "count": 2,
          "term": "proverbs"
        }
      ],
      "name": "",
      "children": [
        {
          "bibleverse": "proverbs",
          "children": [
            {
              "children": [],
              "name": "proverbs",
              "bibleverse": "proverbs"
            },
            {
              "children": [],
              "name": "romans",
              "bibleverse": "romans"
            }
          ],
          "name": "proverbs",
          "size": 2
        },
        {
          "bibleverse": "romans",
          "children": [
            {
              "children": [],
              "name": "romans",
              "bibleverse": "romans"
            },
            {
              "children": [],
              "name": "proverbs",
              "bibleverse": "proverbs"
            }
          ],
          "name": "romans",
          "size": 2
        }
      ]
    }


