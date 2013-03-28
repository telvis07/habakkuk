-- from http://comments.gmane.org/gmane.comp.apache.mahout.user/16037
-- sanity test for elephant-bird mahout integration. Generate 
-- vectors then dump with 'mahout seqdumper'
-- $ pig -x local mahout_seqfile.pig
-- $ mahout seqdumper -s file:///path/to/output/part-m-00000
--
-- seqdumper should show
-- Key class: class org.apache.hadoop.io.Text Value Class: class org.apache.mahout.math.VectorWritable
-- Key: aaa: Value: org.apache.mahout.math.VectorWritable@236e6a12
-- Key: bbb: Value: org.apache.mahout.math.VectorWritable@236e6a12
-- Key: ccc: Value: org.apache.mahout.math.VectorWritable@236e6a12
-- Key: ddd: Value: org.apache.mahout.math.VectorWritable@236e6a12
-- Count: 4

-- register jars
register '/usr/lib/pig/3rd-party/elephant-bird-2.2.3.jar';
register '/usr/lib/pig/contrib/piggybank/java/lib/json-simple-1.1.jar';
register '/usr/lib/pig/3rd-party/guava-11.0.1.jar';
register '/usr/lib/mahout/mahout-examples-0.5-cdh3u5-job.jar'; 

-- seqfile constants
%declare SEQFILE_LOADER 'com.twitter.elephantbird.pig.load.SequenceFileLoader';
%declare SEQFILE_STORAGE 'com.twitter.elephantbird.pig.store.SequenceFileStorage';
%declare INT_CONVERTER 'com.twitter.elephantbird.pig.util.IntWritableConverter';
%declare VECTOR_CONVERTER 'com.twitter.elephantbird.pig.mahout.VectorWritableConverter';
%declare TEXT_CONVERTER 'com.twitter.elephantbird.pig.util.TextConverter';

-- params
%default data 'vectorsPigTest.dat'
%default output 'output'

-- load the data
pair = LOAD '$data' AS (key:chararray, 
        val:tuple (cardinality: int, entries:bag {entry: tuple(index: int, value: double)}));
dump pair;
describe pair;

-- sanity check to make sure data was loaded correctly.
keys = foreach pair generate key;
dump keys;
describe keys;

-- execute prior statements before shell command
exec;
sh rm -rf '$output'

-- store sequence files
STORE pair INTO '$output' USING $SEQFILE_STORAGE (
  '-c $TEXT_CONVERTER', '-c $VECTOR_CONVERTER'
);
