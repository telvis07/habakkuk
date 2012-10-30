package technicalelvis.habakkuk.database;

import java.util.HashSet;
import java.util.Properties;

import org.apache.accumulo.core.client.AccumuloException;
import org.apache.accumulo.core.client.AccumuloSecurityException;
import org.apache.accumulo.core.client.BatchWriter;
import org.apache.accumulo.core.client.Connector;
import org.apache.accumulo.core.client.MultiTableBatchWriter;
import org.apache.accumulo.core.client.MutationsRejectedException;
import org.apache.accumulo.core.client.TableNotFoundException;
import org.apache.accumulo.core.client.ZooKeeperInstance;
import org.apache.accumulo.core.data.KeyExtent;
import org.apache.accumulo.core.data.Mutation;
import org.apache.accumulo.core.data.Value;
import org.apache.hadoop.io.Text;
import org.apache.log4j.Logger;

public class AccumuloDB {
	static Logger LOG = Logger.getLogger(AccumuloDB.class);
	String instanceName;
	String zooServers;
	String user;
	String password;
	boolean testing=false;
	
	ZooKeeperInstance inst;
	Connector conn;
	MultiTableBatchWriter mtbw;
	BatchWriter bw_txt;
	BatchWriter bw_cnt;
	final String TEXT_TBL =  "habakkuk_text";
	final String CNT_TBL  = "habakkuk_verse_count";
	
	public AccumuloDB (Properties props) {
		instanceName = props.getProperty("accumulo.instance");
		zooServers = props.getProperty("accumulo.zookeeper");
		user = props.getProperty("accumulo.user");
		password = props.getProperty("accumulo.password");
		testing = Boolean.parseBoolean(props.getProperty("habakkuk.usetestspout","true"));
		LOG.info(String.format("instance %s,  zooservers %s",instanceName, zooServers));
		init();
	}
	
	boolean init(){
		inst = new ZooKeeperInstance(instanceName, zooServers);
		boolean ret = false;
		try {
			conn = inst.getConnector(user,password.getBytes());
			mtbw = conn.createMultiTableBatchWriter(200000l, 300, 4);
			bw_txt = mtbw.getBatchWriter(TEXT_TBL);
			bw_cnt = mtbw.getBatchWriter(CNT_TBL);
			ret=true;
			LOG.info("init succeeded");
		} catch (AccumuloException e) {
			conn = null;			
		} catch (AccumuloSecurityException e) {
			LOG.error(e.getMessage());
			conn = null;
		} catch (TableNotFoundException e) {
			LOG.error(e.getMessage());
			conn = null;
		}	
		return ret;
	}
	
	public void clear()
	{
	}
	
	public void store(Text tweetId, Text verse, Text date, Value tweet) throws MutationsRejectedException{
		if (conn == null){
			if (! init()){
				return;
			}
		}
		if (testing){
			LOG.info(String.format("db (testing): verse %s tweetid %s _date %s txt %s",
					verse.toString(),
					tweetId.toString(),
					date.toString(),
					tweet.toString()));
			return;
		} else {
			LOG.info(String.format("db: verse %s tweetid %s _date %s txt %s",
					verse.toString(),
					tweetId.toString(),
					date.toString(),
					tweet.toString()));
		}
		
		Mutation mutation = new Mutation(tweetId);
		mutation.put(date, verse, tweet);
		bw_txt.addMutation(mutation);
		
		Mutation mutation2 = new Mutation(verse);
	    mutation2.put(date, new Text(""), new Value("1".getBytes()));
	    bw_cnt.addMutation(mutation2);
	}
	
	public void close() {
		try {
		      mtbw.close();
		} catch (MutationsRejectedException e) {
		      if (e.getAuthorizationFailures().size() > 0) {
		        HashSet<String> tables = new HashSet<String>();
		        for (KeyExtent ke : e.getAuthorizationFailures()) {
		          tables.add(ke.getTableId().toString());
		        }
		        LOG.error("ERROR : Not authorized to write to tables : " + tables);
		      }
		      
		      if (e.getConstraintViolationSummaries().size() > 0) {
		        LOG.error("ERROR : Constraint violations occurred : " + e.getConstraintViolationSummaries());
		      }
		}
	}
}
