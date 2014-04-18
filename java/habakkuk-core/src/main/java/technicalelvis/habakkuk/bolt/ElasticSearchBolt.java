package technicalelvis.habakkuk.bolt;

import java.util.Map;
import java.util.Properties;

import org.apache.log4j.Logger;

import backtype.storm.task.OutputCollector;
import backtype.storm.task.TopologyContext;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.topology.base.BaseRichBolt;
import backtype.storm.tuple.Tuple;

import org.elasticsearch.action.index.IndexResponse;
import org.elasticsearch.client.Client;
import org.elasticsearch.node.*;
import static org.elasticsearch.node.NodeBuilder.*;
import org.elasticsearch.client.transport.TransportClient;
import org.elasticsearch.common.settings.ImmutableSettings;
import org.elasticsearch.common.settings.Settings;
import org.elasticsearch.common.transport.InetSocketTransportAddress;

public class ElasticSearchBolt extends BaseRichBolt{
	static Logger LOG = Logger.getLogger(ElasticSearchBolt.class);
	OutputCollector _collector;
	Properties props;
	Client client;
	Node node;
	String host;
	String cluster;
	int port;
	String idxname;
	boolean testing;
	String doc_type="habakkuk";

	public ElasticSearchBolt(Properties props){
		this.props = props;
		host = props.getProperty("elasticsearch.host");
		port = Integer.parseInt(props.getProperty("elasticsearch.port"));
		cluster = props.getProperty("elasticsearch.cluster");
		idxname = props.getProperty("elasticsearch.indexname");
		testing = Boolean.parseBoolean(props.getProperty("habakkuk.usetestspout","true"));

	}

	@Override
	public void prepare(Map stormConf, TopologyContext context,
			OutputCollector collector) {
		_collector = collector;
		LOG.info("clustername "+cluster);
		LOG.info("host "+host);
		LOG.info("port "+port);
		Settings settings = ImmutableSettings.settingsBuilder()
                .put("cluster.name", cluster)
                .build();
		client = new TransportClient(settings).
				addTransportAddress(new InetSocketTransportAddress(host,port));
	}

	@Override
	public void execute(Tuple tuple) {
		try {
			@SuppressWarnings("unchecked")
			// See - http://www.elasticsearch.org/guide/en/elasticsearch/client/java-api/current/index_.html#index_
			Map<String,Object> data = (Map<String,Object>)tuple.getValueByField("result");
			LOG.info(String.format("ES:%s",data));
			String idx;
			if (testing){
				idx = idxname+"-"+"test";
			}else{
				idx = idxname;
			}

		   IndexResponse response = client.prepareIndex(idx, doc_type)
		    		.setSource(data)
		    		.execute().actionGet();
		} catch (Exception e) {
			LOG.error(e.getMessage(),e);
		} finally {
			_collector.ack(tuple);
		}

	}
	@Override
	public void cleanup(){
		client.close();
	}


	@Override
	public void declareOutputFields(OutputFieldsDeclarer declarer) {
		// none
	}
}
