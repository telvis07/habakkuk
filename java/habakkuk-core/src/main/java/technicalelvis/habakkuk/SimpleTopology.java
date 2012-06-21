package technicalelvis.habakkuk;

import java.util.Map;

// import technicalelvis.bolt.ScriptureFilterBolt;
// import technicalelvis.bolt.PrinterBolt;
import technicalelvis.habakkuk.spout.TwitterSampleSpout;
import backtype.storm.Config;
import backtype.storm.LocalCluster;
import backtype.storm.task.ShellBolt;
import backtype.storm.topology.IRichBolt;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.topology.TopologyBuilder;
// import backtype.storm.utils.Utils;
import backtype.storm.tuple.Fields;

public class SimpleTopology {
	public static class ScriptureFilterBolt extends ShellBolt implements IRichBolt{
	    
		public ScriptureFilterBolt() {
	        super("python", "ScriptureFilterBolt.py");
	    }
		
		public void declareOutputFields(OutputFieldsDeclarer declarer) {
	        declarer.declare(new Fields("book"));
	    }

	    public Map<String, Object> getComponentConfiguration() {
	        return null;
	    }
	}
	
	public static void main(String[] args) {
        String username = args[0];
        String pwd = args[1];
        TopologyBuilder builder = new TopologyBuilder();
        
        builder.setSpout("twitter", new TwitterSampleSpout(username, pwd), 1);
        builder.setBolt("filter", new ScriptureFilterBolt(), 1)
        		.shuffleGrouping("twitter");
        //builder.setBolt("print", new PrinterBolt(), 1)
        //        .shuffleGrouping("filter");
                
        
        Config conf = new Config();
        LocalCluster cluster = new LocalCluster();
        
        cluster.submitTopology("test", conf, builder.createTopology());
        
        // Utils.sleep(10000);
        // cluster.shutdown();
    }
}
