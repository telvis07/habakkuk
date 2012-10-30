package technicalelvis.habakkuk.spout;

import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.text.SimpleDateFormat;
import org.apache.log4j.Logger;

import backtype.storm.spout.SpoutOutputCollector;
import backtype.storm.task.TopologyContext;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.topology.base.BaseRichSpout;
import backtype.storm.tuple.Fields;
import backtype.storm.tuple.Values;
import backtype.storm.utils.Utils;

public class TestTweetSpout extends BaseRichSpout {
	static Logger LOG = Logger.getLogger(TestTweetSpout.class);
	SpoutOutputCollector _collector;
	int tweetid=0;
	
	@Override
	public void open(Map conf, TopologyContext context,
			SpoutOutputCollector collector) {
		_collector = collector;
	}

	@Override
	public void nextTuple() {
		Utils.sleep(1000);
		LOG.info("TestTweetSpout emitting test message");
	    HashMap<String,String> res = new HashMap<String,String>();
	    Date _date = new Date();
	    SimpleDateFormat _format = new SimpleDateFormat("yyyy-MM-dd");
	    StringBuilder _datestr = new StringBuilder(_format.format(_date));
	    
	    
	    res.put("tweetid",Integer.toString(tweetid+=1));
	    res.put("text", "I like John 3:16");
	    res.put("created_at", Long.toString(_date.getTime()));
	    res.put("created_at_date", _datestr.toString());
	    LOG.info("emit");
	    _collector.emit(new Values(res));
	}

	@Override
	public void declareOutputFields(OutputFieldsDeclarer declarer) {
		declarer.declare(new Fields("result"));		
	}
}
