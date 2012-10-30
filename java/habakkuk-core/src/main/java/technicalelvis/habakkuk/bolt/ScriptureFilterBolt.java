package technicalelvis.habakkuk.bolt;
import backtype.storm.task.ShellBolt;
import backtype.storm.topology.IRichBolt;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.tuple.Fields;
import java.util.Map;


public class ScriptureFilterBolt extends ShellBolt implements IRichBolt{
    
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;

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

