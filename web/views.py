from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
import jsonlib2 as json
import logging
from web.search import get_scriptures_by_date, get_topics

DEFAULT_RANGE=7
# init logging
logger = logging.getLogger(__name__)
query_logger = logging.getLogger('query_logger')


def about(request, template="about.html"):
    return render(request, template, {})


def topics(request, topic_name=None, template="topics.html"):
    context = {
        "topic_results": get_topics(topic_name=topic_name)
    }

    if topic_name:
        logger.info("topic_name: {}".format(topic_name))

    return render(request, template, context)

@require_POST
def topics_api(request, topic_name=None):
    try:
        params = json.loads(request.body)
    except:
        params = {}

    size = params.get('size', 10)
    offset = params.get("offset", 0)

    context = {
        "size" : size,
        "offset" : offset,
        "topic_results": get_topics(size=size,
                                    offset=offset,
                                    topic_name=topic_name)
    }

    return JsonResponse(context)


def biblestudy(request, template="biblestudy.html", live_hack=False):
    context = {}
    params = request.GET
    start = params.get('s', None)
    end = params.get('e', None)
    _date = params.get('date', None)
    size = params.get('size', 10)
    search_text = params.get('search', None)
    _format = params.get("format", None)
    recommend = params.get('r', None)

    logger.info("[biblestudy] - %s"%request.get_full_path())

    if _format == 'json':
        return_json = True
    else:
        return_json = False


    if live_hack:
        context["search_results"] = _get_scriptures_by_date()
    elif recommend:
        context["search_results"] = fake_recommendations()
    else:
        context["search_results"] = get_scriptures_by_date(st=start,
                                                           et=end,
                                                           size=size,
                                                           _date=_date,
                                                           search_text=search_text)

    context["habakkuk_message"] = get_habakkuk_message()
    context["search_text"] = search_text
    context["date_str"] = "all time"
    context["recommend"] = recommend

    if return_json:
        return JsonResponse(context)
    else:
        return render(request, template, context)

def get_habakkuk_message():
    return "Hello World!"

def _get_scriptures_by_date():
    return [{"bibleverse":"John 3:16",
      "text":"For God so loved the world that he gave his one and only Son,"
      "that whoever believes in him shall not perish but have eternal life."},
      {"bibleverse":"1 John 4:19",
      "text":"We love because he first loved us."},
      {"bibleverse":"1 Corinthians 13:4",
      "text":"Love is patient, love is kind. It does not envy, it does not boast, it is not proud."},
      {"bibleverse":"1 Corinthians 13:13",
      "text":"And now these three remain: faith, hope and love. But the greatest of these is love."},
      {"bibleverse":"Psalm 37:23",
      "text":"The steps of a good man are ordered by the Lord: and he delighteth in his way."},
    ]

def fake_recommendations():
    return [{"text": "If the Son therefore shall make you free, ye shall be free indeed.", "translation": "KJV",
             "bibleverse_human": "john 8:36", "bibleverse": "john 8:36"},
            {"text": "And ye shall know the truth, and the truth shall make you free.", "translation": "KJV",
             "bibleverse_human": "john 8:32", "bibleverse": "john 8:32"}, {
            "text": "Stand fast therefore in the liberty wherewith Christ hath made us free, and be not entangled again with the yoke of bondage.",
            "translation": "KJV", "bibleverse_human": "galatians 5:1", "bibleverse": "galatians 5:1"}, {
            "text": "Let your conversation be without covetousness; and be content with such things as ye have: for he hath said, I will never leave thee, nor forsake thee.",
            "translation": "KJV", "bibleverse_human": "hebrews 13:5", "bibleverse": "hebrews 13:5"}, {
            "text": "There is neither Jew nor Greek, there is neither bond nor free, there is neither male nor female: for ye are all one in Christ Jesus.",
            "translation": "KJV", "bibleverse_human": "galatians 3:28", "bibleverse": "galatians 3:28"}, {
            "text": "For the law of the Spirit of life in Christ Jesus hath made me free from the law of sin and death.",
            "translation": "KJV", "bibleverse_human": "romans 8:2", "bibleverse": "romans 8:2"}, {
            "text": "For the wages of sin is death; but the gift of God is eternal life through Jesus Christ our Lord.",
            "translation": "KJV", "bibleverse_human": "romans 6:23", "bibleverse": "romans 6:23"}]

