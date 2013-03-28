-- Generate vectors with counts for every bible book tweeted by a user
-- pig -x local book_vectors.pig

-- deps
register '/usr/lib/pig/3rd-party/elephant-bird-2.2.3.jar';
register '/usr/lib/pig/contrib/piggybank/java/lib/json-simple-1.1.jar';
register '/usr/lib/pig/3rd-party/guava-11.0.1.jar';
register '/usr/lib/mahout/mahout-examples-0.5-cdh3u5-job.jar'; 
register '/usr/lib/pig/contrib/piggybank/java/piggybank.jar'

-- elephant-bird seqfile constants
%declare SEQFILE_LOADER 'com.twitter.elephantbird.pig.load.SequenceFileLoader';
%declare SEQFILE_STORAGE 'com.twitter.elephantbird.pig.store.SequenceFileStorage';
%declare INT_CONVERTER 'com.twitter.elephantbird.pig.util.IntWritableConverter';
%declare VECTOR_CONVERTER 'com.twitter.elephantbird.pig.mahout.VectorWritableConverter';
%declare TEXT_CONVERTER 'com.twitter.elephantbird.pig.util.TextConverter';

-- param defaults
%default book_dict 'join_data/book_id.csv';
%default data 'input/test_habakkuk_data.json'
%default output 'book_vectors'

-- load habakkuk json data, generate screenname and book reference
tweets = load '$data' using com.twitter.elephantbird.pig.load.JsonLoader();
filtered = foreach tweets generate (chararray)$0#'screenname' as screenname, (chararray)$0#'book' as book;

-- load book ids for join
bookids = load '$book_dict' as (book:chararray, docfreq:int, bookid:int);
filtered = join bookids by book, filtered by book;

-- group using tuple(screenname,book) as key
by_screen_book = group filtered by (screenname, bookids::bookid);

-- generate counts for each screenname, book
book_counts = foreach by_screen_book {
    generate group.screenname as screenname, group.bookids::bookid as bookid, COUNT(filtered) as count;
}

-- group by screenname: bag{(screenname, bookid, count)}
grpd = group book_counts by screenname;

-- nested projection to get: screenname: entries:bag{(bookid, count)}
-- uses ToTuple because SEQFILE_STORAGE expects bag to be in a tuple
vector_input = foreach grpd generate group, org.apache.pig.piggybank.evaluation.util.ToTuple(book_counts.(bookid, count));

-- store to sequence files
STORE vector_input INTO '$output' USING $SEQFILE_STORAGE (
  '-c $TEXT_CONVERTER', '-c $VECTOR_CONVERTER -- -cardinality 66'
);
