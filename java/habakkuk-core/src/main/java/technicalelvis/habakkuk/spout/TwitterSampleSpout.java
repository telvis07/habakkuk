package technicalelvis.habakkuk.spout;

import java.text.SimpleDateFormat;
import java.util.Map;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.HashMap;

import org.apache.log4j.Logger;

import twitter4j.Status;
import twitter4j.StatusDeletionNotice;
import twitter4j.StatusListener;
import twitter4j.TwitterStream;
import twitter4j.TwitterStreamFactory;
import twitter4j.json.DataObjectFactory;
import twitter4j.conf.ConfigurationBuilder;
import backtype.storm.Config;
import backtype.storm.spout.SpoutOutputCollector;
import backtype.storm.task.TopologyContext;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.topology.base.BaseRichSpout;
import backtype.storm.tuple.Fields;
import backtype.storm.tuple.Values;
import backtype.storm.utils.Utils;

// TODO: twitter4j with API keys
public class TwitterSampleSpout extends BaseRichSpout {
	static Logger LOG = Logger.getLogger(TwitterSampleSpout.class);
    SpoutOutputCollector _collector;
    LinkedBlockingQueue<Status> queue = null;
    TwitterStream _twitterStream;
    String _username;
    String _pwd;
    
    
    public TwitterSampleSpout(String username, String pwd) {
        _username = username;
        _pwd = pwd; 
    }
    
    @Override
    public void open(Map conf, TopologyContext context, SpoutOutputCollector collector) {
        queue = new LinkedBlockingQueue<Status>(1000);
        _collector = collector;
        StatusListener listener = new StatusListener() {

            @Override
            public void onStatus(Status status) {
                queue.offer(status);
            }

            @Override
            public void onDeletionNotice(StatusDeletionNotice sdn) {
            }

            @Override
            public void onTrackLimitationNotice(int i) {
            }

            @Override
            public void onScrubGeo(long l, long l1) {
            }

            @Override
            public void onException(Exception e) {
            }
            
        };
        
        ConfigurationBuilder cb = new ConfigurationBuilder();
        cb.setUser(_username)
        .setPassword(_pwd)
        .setJSONStoreEnabled(true);
        TwitterStreamFactory fact = new TwitterStreamFactory(cb.build());
        _twitterStream = fact.getInstance();
        _twitterStream.addListener(listener);
        _twitterStream.sample();    
    }

    @Override
    public void nextTuple() {
        Status ret = queue.poll();
        if(ret==null) {
            Utils.sleep(50);
        } else {
        	String rawJSON = DataObjectFactory.getRawJSON(ret);
        	if (rawJSON != null){
        		LOG.info(String.format("raw json: '%s'",rawJSON));
        	}
        	Map<String, String> data = new HashMap<String, String>();
        	data.put("username", ret.getUser().getName());
        	data.put("screenname", ret.getUser().getScreenName());
        	data.put("text", ret.getText());
        	data.put("tweetid",Long.toString(ret.getId()));    	    
    	    data.put("created_at", ret.getCreatedAt().toString());
    	    
    	    SimpleDateFormat _format = new SimpleDateFormat("yyyy-MM-dd");
    	    StringBuilder _datestr = new StringBuilder(_format.format(ret.getCreatedAt()));
    	    data.put("created_at_date", _datestr.toString());
    	    data.put("created_at", Long.toString(ret.getCreatedAt().getTime()));
        	_collector.emit(new Values(data));        	
        }
    }

    @Override
    public void close() {
        _twitterStream.shutdown();
    }

    @Override
    public Map<String, Object> getComponentConfiguration() {
        Config ret = new Config();
        ret.setMaxTaskParallelism(1);
        return ret;
    }    

    @Override
    public void ack(Object id) {
    }

    @Override
    public void fail(Object id) {
    }

    @Override
    public void declareOutputFields(OutputFieldsDeclarer declarer) {
        declarer.declare(new Fields("tweet"));
    }
    
}
