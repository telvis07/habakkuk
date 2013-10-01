This directory contains scripts to analyze habakkuk tweets using hadoop and mahout

## Dependencies
- [hadoop](http://hadoop.apache.org/)
- [pig](http://pig.apache.org/docs/r0.7.0/piglatin_ref2.html)
- [elephant-bird](https://github.com/kevinweil/elephant-bird)
- [mahout](http://mahout.apache.org/)

## Kmeans Clustering by bible book
This section describes steps to perform kmeans clustering based on book feature vectors. 
Each entry in the vector corresponds to a bible book (e.g. 1 is genesis, 2 is exodus, etc).

### Execution Steps
Copy input data to hdfs

    hadoop fs -mkdir input
    hadoop fs -copyFromLocal input/test_habakkuk_data.json input
    hadoop fs -mkdir join_data
    hadoop fs -copyFromLocal join_data/book_id.csv join_data/

Remove output from prior run

    hadoop fs -rmr book_vectors

Run pig job to generate book vectors. There will be a vector for each twitter screen name in 
the data.

    pig -p data=input -p output=book_vectors book_vectors.pig 

Use `mahout seqdumper` to view output vectors

    mahout seqdumper -s book_vectors/part-r-00000

I wrote a simple hadoop app to convert vectors created by elephant-bird to namedVectors. namedVectors will show the 
actual twitter screenname in the `clusterdump` command performed in later steps.

    $ hadoop fs -mkdir book_vectors-nv
    or...
    $ hadoop fs -rm book_vectors-nv/*
    $ cd habakkuk/java/elephant-bird-vector-converter/
    $ mvn package
    $ hadoop jar target/elephant-bird-vector-converter-0.1-SNAPSHOT-job.jar \
      technicalelvis.elephantBirdVectorConverter.App book_vectors/ book_vectors-nv/

Output should be something like: 

    13/03/26 04:40:54 INFO elephantBirdVectorConverter.App: inputdir='book_vectors/', outputdir='book_vectors-nv/'
    13/03/26 04:40:54 INFO elephantBirdVectorConverter.App: Wrote '10' namedvectors to 'book_vectors-nv/part-m-00000'

Run mahout kmeans on book vectors. Kmeans will generate 2 clusters (-k 2) and choose the initial clusters at random
and place them in kmeans-initial-clusters. The maximum number of iterations is 10 (-x). The cosine distance measure is used (-dm).
The clustering output will be stored in clusters (-o). Use a convergence threshold (-cd) of 0.1, instead of using the
default value of 0.5, because cosine distances lie between 0 and 1.

    mahout kmeans -i book_vectors-nv \
       -c kmeans-initial-clusters -k 2 -o clusters \
       -x 10 -ow -cl -dm org.apache.mahout.common.distance.CosineDistanceMeasure \
       -cd 0.1

Check out the clusters directory. clusters/clusters-* contains clusters from each kmeans round. 
The highest round contains the final clusters with the book weightings.  clusters/clusteredPoints lists the original vectors and their assigned clusters.

    $ hadoop fs -ls clusters

    Found 3 items
    /clusters/clusteredPoints
    /clusters/clusters-1
    /clusters/clusters-2

Use clusterdump to show top bible books per cluster using the book dictionary in 
join_data/ on your local filesystem. Output is stored in clusterdump.log

    $ mahout clusterdump -d join_data/book.dictionary -dt text -s clusters/clusters-1 -p clusters/clusteredPoints -n 10 -o clusterdump.log
    $ cat clusterdump.log
    CL-0{n=9 c=[matthew:0.333, luke:0.444, john:0.222, galatians:0.111, philippians:0.111] r=[matthew:0.667, luke:0.497, john:0.416, galatians:0.314, philippians:0.314]}
        Top Terms: 
            luke                                    =>  0.4444444444444444
            matthew                                 =>  0.3333333333333333
            john                                    =>  0.2222222222222222
            galatians                               =>  0.1111111111111111
            philippians                             =>  0.1111111111111111
        Weight:  Point:
        1.0: Zigs26 = [luke:1.000]
        1.0: da_nellie = [john:1.000]
        1.0: austinn_21 = [luke:1.000]
        1.0: YUMADison22 = [luke:1.000]
        1.0: chap_stique = [galatians:1.000]
        1.0: ApesWhitelaw = [matthew:2.000, john:1.000]
        1.0: alexxrenee22 = [luke:1.000]
        1.0: AbigailObregon3 = [philippians:1.000]
        1.0: thezealofisrael = [matthew:1.000]
    VL-7{n=1 c=[ephesians:1.000] r=Affirm_Success =]}
        Top Terms: 
            ephesians                               =>                 1.0
        Weight:  Point:
        1.0: Affirm_Success = [ephesians:1.000]

The results show 2 clusters. 1 cluster has 9 tweeters with the top books as luke, matthew, john, galations and phillippians. 
The second cluster has 1 tweeter with ephesians as a top book. Obviously, YMMV with different convergence thresholds, data and distance metrics.

## References
* [Programming Pig by Alan Gates](http://my.safaribooksonline.com/book/-/9781449317881)
* [Mahout in Action by Sean Owen](http://manning.com/owen/)
