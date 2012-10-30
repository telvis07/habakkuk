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
        String topologyName = props.getProperty("habakkuk.topologyname");
        String twUsername = props.getProperty("twitter4j.username");
        String twPassword = props.getProperty("twitter4j.password");
        int numworkers = Integer.parseInt(props.getProperty("habakkuk.numWorkers"));
        int numTwitterSpouts = 1;
        int numBibleFilterBolts = Integer.parseInt(props.getProperty("habakkuk.numBibleFilterBolts"));
        // int numAccumuloBolts = Integer.parseInt(props.getProperty("habakkuk.numAccumulotBolts"));
        int numESBolts = Integer.parseInt(props.getProperty("habakkuk.numESBolts"));
        
        if (useTestSpout){
        	builder.setSpout("twitter", new TestTweetSpout(),numTwitterSpouts);
        } else{	
        	builder.setSpout("twitter", new TwitterSampleSpout(twUsername, twPassword), numTwitterSpouts);
        }
        builder.setBolt("biblematch", new ScriptureFilterBolt(), numBibleFilterBolts)
        		.shuffleGrouping("twitter");
        //builder.setBolt("accumulo", new AccumuloLoader(props), numAccumuloBolts)
        //        .shuffleGrouping("biblematch");
        builder.setBolt("elastic", new ElasticSearchBolt(props), numESBolts)
        		  .shuffleGrouping("biblematch");
               
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
