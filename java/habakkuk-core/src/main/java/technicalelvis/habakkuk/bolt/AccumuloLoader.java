package technicalelvis.habakkuk.bolt;

import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

import org.apache.accumulo.core.client.MutationsRejectedException;
import org.apache.accumulo.core.data.Value;
import org.apache.hadoop.io.Text;
import org.apache.log4j.Logger;
import org.codehaus.jackson.map.ObjectMapper;

import backtype.storm.task.OutputCollector;
import backtype.storm.task.TopologyContext;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.topology.base.BaseRichBolt;
import backtype.storm.tuple.Fields;
import backtype.storm.tuple.Tuple;
import technicalelvis.habakkuk.database.AccumuloDB;

public class AccumuloLoader extends BaseRichBolt{
	static Logger LOG = Logger.getLogger(AccumuloLoader.class);
	OutputCollector _collector;
	AccumuloDB acc = null;
	Properties props;
	ObjectMapper jxn;
	
	public AccumuloLoader (Properties props) 	{		
		this.props = props;
	}
		
	public void prepare(Map conf, TopologyContext context, OutputCollector collector) {
		_collector = collector;	
		acc = new AccumuloDB(props);
		jxn = new ObjectMapper();
	}
	
	@Override
	public void execute(Tuple tuple){
		try {
			@SuppressWarnings("unchecked")
			HashMap<String,String> res = (HashMap<String,String>)tuple.getValueByField("result");
			
			
			Text verse = new Text(res.get("book")+" "+res.get("verse"));
			Text tweetid = new Text(res.get("tweetid"));
			Text _date = new Text(res.get("created_at_str"));
			Value txt;
			txt = new Value(jxn.writeValueAsString(res).getBytes());
			LOG.debug(String.format("db bolt verse %s tweetid %s _date %s txt %s\n",
					verse.toString(),
					tweetid.toString(),
					_date.toString(),
					txt.toString()));
			acc.store(tweetid, verse, _date, txt);				
		} catch (Exception e) {
			LOG.error(e.getMessage(),e);
		} finally {
			_collector.ack(tuple);
		}
	}
	
	@Override
	public void declareOutputFields(OutputFieldsDeclarer declarer){
		declarer.declare(new Fields("result"));
	}
	
	@Override
	public void cleanup(){
		acc.close();
	}
}


