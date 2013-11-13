-- Generate vectors with counts for every bible verse tweeted by a user
-- pig -x local verse_vectors.pig

-- deps
register '/var/hadoop/elephant-bird/elephant-bird-core-4.1-SNAPSHOT.jar';
register '/var/hadoop/elephant-bird/elephant-bird-pig-4.1-SNAPSHOT.jar';
register '/var/hadoop/elephant-bird/elephant-bird-mahout-4.1-SNAPSHOT.jar';
register '/var/hadoop/elephant-bird/elephant-bird-hadoop-compat-4.1-SNAPSHOT.jar';
register '/var/hadoop/mahout-distribution-0.7/lib/json-simple-1.1.jar';
register '/var/hadoop/mahout-distribution-0.7/lib/guava-r09.jar';
register '/var/hadoop/mahout/mahout-examples-0.7-job.jar'; 
register '/var/hadoop/pig/contrib/piggybank/java/piggybank.jar';

-- elephant-bird seqfile constants
%declare SEQFILE_LOADER 'com.twitter.elephantbird.pig.load.SequenceFileLoader';
%declare SEQFILE_STORAGE 'com.twitter.elephantbird.pig.store.SequenceFileStorage';
%declare INT_CONVERTER 'com.twitter.elephantbird.pig.util.IntWritableConverter';
%declare VECTOR_CONVERTER 'com.twitter.elephantbird.pig.mahout.VectorWritableConverter';
%declare TEXT_CONVERTER 'com.twitter.elephantbird.pig.util.TextConverter';

-- param defaults
%default verse_dict 'join_data/verse_id.csv';
%default data 'input/test_habakkuk_data.json'
%default output 'verse_vectors'

-- load habakkuk json data, generate screenname and verse reference
tweets = load '$data' using com.twitter.elephantbird.pig.load.JsonLoader();
filtered = foreach tweets generate (chararray)$0#'screenname' as screenname, (chararray)$0#'bibleverse' as verse;

-- load verse ids for join, (hopefully this join will get rid of false regex matches too)
verseids = load '$verse_dict' as (verse:chararray, docfreq:int, verseid:int);
filtered = join verseids by verse, filtered by verse;

-- group using tuple(screenname,verse) as key
by_screen_verse = group filtered by (screenname, verseids::verseid);

-- generate counts for each screenname, verse
verse_counts = foreach by_screen_verse {
    generate group.screenname as screenname, group.verseids::verseid as verseid, COUNT(filtered) as count;
}

-- group by screenname: bag{(screenname, verseid, count)}
grpd = group verse_counts by screenname;

-- nested projection to get: screenname: entries:bag{(verseid, count)}
-- uses ToTuple because SEQFILE_STORAGE expects bag to be in a tuple
vector_input = foreach grpd generate group, org.apache.pig.piggybank.evaluation.util.ToTuple(verse_counts.(verseid, count));

-- store to sequence files
STORE vector_input INTO '$output' USING $SEQFILE_STORAGE (
  '-c $TEXT_CONVERTER', '-c $VECTOR_CONVERTER -- -cardinality 31102'
);
