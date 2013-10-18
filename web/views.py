# from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime, timedelta, date
from django.utils.timezone import now
import jsonlib2 as json
import traceback
import logging
import sys
from web.models import ClusterData

DEFAULT_RANGE=1
# init logging
logger = logging.getLogger(__name__)
query_logger = logging.getLogger('query_logger')

def home(request, template='clustering.html'):
    context = {}
    context['facets'] = json.dumps([
            {'value':'john 3:16', 'count':'10', 'selected': False},
            {'value':'genesis 2:24', 'count':'8', 'selected': False},
         ])
    context['clusters'] = json.dumps([])

    return render(request, template, context)

def query(request, datestr=None, range=None):
    response = {}
    try:
        if datestr:
            logger.debug("got a datestr "+datestr)
            dt = datetime.strptime(datestr, "%Y%m%d")
        else:
            logger.debug("using today")
            dt = now().date()

        if not range:
            range=DEFAULT_RANGE
        else:
            range=int(range)
            
        logger.info("Looking for clusters dt=%s, range=%d"%(dt, range))
        ret = ClusterData.objects.filter(date=dt, range=range)
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
