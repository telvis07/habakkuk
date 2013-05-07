package technicalelvis.habakkuk;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Map;
import java.util.Properties;
import org.apache.log4j.Logger;



import technicalelvis.habakkuk.bolt.AccumuloLoader;
import technicalelvis.habakkuk.bolt.ElasticSearchBolt;
import technicalelvis.habakkuk.bolt.PrinterBolt;
import technicalelvis.habakkuk.spout.TestTweetSpout;
// import technicalelvis.bolt.ScriptureFilterBolt;
// import technicalelvis.bolt.PrinterBolt;
import technicalelvis.habakkuk.spout.TwitterSampleSpout;
import backtype.storm.Config;
import backtype.storm.LocalCluster;
import backtype.storm.StormSubmitter;
import backtype.storm.generated.AlreadyAliveException;
import backtype.storm.generated.InvalidTopologyException;
import backtype.storm.task.ShellBolt;
import backtype.storm.topology.IRichBolt;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.topology.TopologyBuilder;
// import backtype.storm.utils.Utils;
import backtype.storm.tuple.Fields;
import backtype.storm.utils.Utils;

public class MainTopology {
	static Logger LOG = Logger.getLogger(MainTopology.class);
	final static String MATCHBOLT = "biblematch";
	final static String TWITTERSPOUT = "twitter";
	final static String ESBOLT = "elastic";
	final static String ACCBOLT = "accumulo";
	final static String PRINTBOLT = "printer";
	
	public static class ScriptureFilterBolt extends ShellBolt implements IRichBolt{
	    
		public ScriptureFilterBolt() {
	        super("python", "ScriptureFilterBolt.py");
	    }
		
		public void declareOutputFields(OutputFieldsDeclarer declarer) {
	        declarer.declare(new Fields("result"));
	    }

	    public Map<String, Object> getComponentConfiguration() {
	        return null;
	    }
	}
	
	public static void main(String[] args) throws AlreadyAliveException, InvalidTopologyException, IOException {
        Properties props = new Properties();
        FileInputStream in = new FileInputStream(args[0]);
        props.load(in);
        in.close();
		
        TopologyBuilder builder = new TopologyBuilder(); 
        LOG.info(props.toString());
        
        // config
        boolean useTestSpout = Boolean.parseBoolean(props.getProperty("habakkuk.usetestspout"));
        boolean localMode = Boolean.parseBoolean(props.getProperty("habakkuk.localmode"));
        boolean hasStorageBolt = false;
        String topologyName = props.getProperty("habakkuk.topologyname");
        int numworkers = Integer.parseInt(props.getProperty("habakkuk.numWorkers"));
        int numTwitterSpouts = 1;
        int numBibleFilterBolts = Integer.parseInt(props.getProperty("habakkuk.numBibleFilterBolts"));
        int numAccumuloBolts = Integer.parseInt(props.getProperty("habakkuk.numAccumulotBolts","0"));
        int numESBolts = Integer.parseInt(props.getProperty("habakkuk.numESBolts","0"));
        
        if (useTestSpout){
        	builder.setSpout(TWITTERSPOUT, new TestTweetSpout(),numTwitterSpouts);
        } else{	
        	builder.setSpout(TWITTERSPOUT, new TwitterSampleSpout(props), numTwitterSpouts);            
        }
        builder.setBolt(MATCHBOLT, new ScriptureFilterBolt(), numBibleFilterBolts)
        		.shuffleGrouping(TWITTERSPOUT);
        
        // Accumulo storage
        if (numAccumuloBolts>0) {
            builder.setBolt(ACCBOLT, new AccumuloLoader(props), numAccumuloBolts)
                .shuffleGrouping(MATCHBOLT);
            hasStorageBolt = true;
        }
        
        // Elasticsearch storage
        if (numESBolts>0){
            builder.setBolt(ESBOLT, new ElasticSearchBolt(props), numESBolts)
        		  .shuffleGrouping(MATCHBOLT);
            hasStorageBolt = true;
        }
        
        // no storage bolt is enabled, so just print habakkuk messages 
        // to stdout
        if (!hasStorageBolt){
            LOG.info("Using printer bolt");
            builder.setBolt(PRINTBOLT, new PrinterBolt(), 1)
                .shuffleGrouping(MATCHBOLT);
        }
               
        if (localMode){
        	Config conf = new Config();
        	conf.setNumWorkers(numworkers);
        	LocalCluster cluster = new LocalCluster();
        	cluster.submitTopology(topologyName, conf, builder.createTopology());            
        	Utils.sleep(10000);
            cluster.shutdown();
        } else {
        	Config conf = new Config();
        	conf.setNumWorkers(numworkers);
        	conf.setMaxSpoutPending(5000);
        	StormSubmitter.submitTopology(topologyName, conf, builder.createTopology());
        } 
    }
}
