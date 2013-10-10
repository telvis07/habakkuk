from django.conf import settings
from django.http import HttpResponse
from datetime import datetime, timedelta, date
import jsonlib2 as json
import traceback
import logging
import sys

# init logging
logger = logging.getLogger(__name__)
query_logger = logging.getLogger('query_logger')

def query(request, datestr=None):
    response = {}
    try:
        if datestr:
            logger.debug("got a datestr "+datestr)
            dt = datetime.strptime(datestr, "%Y%m%d")
        else:
            logger.debug("using today")
            dt = datetime.today()
            dt = datetime(year=dt.year, month=dt.month, day=dt.day)
        facets = None
        clusters = None
        response = {
            'facets':facets,
            'clusters':clusters
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
