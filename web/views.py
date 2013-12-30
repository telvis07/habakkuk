# from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Max
import jsonlib2 as json
import traceback
import logging
import sys
from web.models import ClusterData, make_d3_data

DEFAULT_RANGE=7
# init logging
logger = logging.getLogger(__name__)
query_logger = logging.getLogger('query_logger')

def biblestudy(request, template="biblestudy.html"):
    context = {}
    return render(request, template, context)

def clusters(request, template='clustering.html'):
    context = {}
    ret = _get_newest_or_for_date(None, None)

    if ret:
        ret = ret[0]
        cluster = make_d3_data(ret)
        print cluster
        context['clusters'] = cluster
        context['facets'] = cluster.get('facets', [])
    else:
        context['clusters'] = []
        context['facets'] = []

    return render(request, template, context)

def clusters_data(request, datestr=None, range=None):
    response = {}
    try:
        ret = _get_newest_or_for_date(datestr, range)
        if ret:
            ret = ret[0]
            response = {
                'clusters':json.loads(ret.d3_dendogram_json),
                'num_clusters':ret.num_clusters,
            }
        else:
            response = {
                'clusters':'{}',
                'num_clusters':0,
            }
    except Exception, ex:
        msg = " ".join(traceback.format_exception(*sys.exc_info()))
        response = {
            'exception':ex,
            'trace':msg,
        }
        logger.error("query error|%s|%s|%s|%s"%(ex, request.user.id, request.body, msg))

    query_logger.info("query|%s|%s"%(request.user.id, request.path))
    return HttpResponse(json.dumps(response), content_type="application/json")

def _get_newest_or_for_date(datestr=None, range=None):
    if datestr:
        logger.debug("got a datestr "+datestr)
        dt = datetime.strptime(datestr, "%Y%m%d")
    else:
        logger.debug("using today")
        # dt = now().date()
        dt = ClusterData.objects.all().aggregate(Max('date'))['date__max']

    if not range:
        range=DEFAULT_RANGE
    else:
        range=int(range)

    logger.info("Looking for clusters dt=%s, range=%d"%(dt, range))
    return ClusterData.objects.filter(date=dt, range=range)
