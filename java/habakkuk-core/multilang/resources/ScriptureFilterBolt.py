import storm
from find_all_scriptures import find_all_scriptures, filtergroupdict
import jsonlib2 as json

class ScriptureParserBolt(storm.BasicBolt):
    def process(self,tup):
        #storm.log("%s"%tup.values[0])
        #status = json.loads(tup.values[0])
        #if status.get('text'):
        #    storm.log("from ScriptureParserBolt: %s"%status['txt'])
        #storm.emit([txt])
        #txt = json.loads(tup.values[0])['text']
        #print "in ScriptureParserBolt: %s"%txt
        #words = txt.split(" ")
        #for word in words:
        #    storm.emit([word])
        txt = tup.values[0]['text']
        matches = find_all_scriptures(txt)
        for ma in matches:
            storm.log("%s"%tup.values[0])
            ret = filtergroupdict(ma)
            matext = ma.string[ma.start():ma.end()].replace('\r\n',' ') #actual matched string
            storm.log("Match %s %s {STRING: '%s'}"%(ret['book'],ret['verse'], matext))
            #storm.emit([ret["book"],ret["verse"])
            #storm.emit([ret["book"]])

ScriptureParserBolt().run()
