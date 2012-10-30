import storm
from find_all_scriptures import find_all_scriptures, filtergroupdict
import jsonlib2 as json

class ScriptureParserBolt(storm.BasicBolt):
    def process(self,tup):
        res = tup.values[0]
        # storm.log("python (in) =%s"%tup.values[0])
        txt = res['text'].lower()
        tweetid = res["tweetid"]
        matches = find_all_scriptures(txt)
        for ma in matches:
            ret = filtergroupdict(ma)
            matext = ma.string[ma.start():ma.end()].replace('\r\n',' ') #actual matched string
            res['book'] = ret['book']
            res['bibleverse'] = " ".join((ret['book'],ret['verse']))
            # storm.log("python (out) =%s"%res)
            storm.emit([res])

ScriptureParserBolt().run()
