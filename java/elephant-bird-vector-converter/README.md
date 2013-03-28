Simple hadoop app to read sparse vectors written by elephant-bird and generate named vectors.

Command is: 
    
    $ hadoop fs -mkdir book_vectors-nv
    or...
    $ hadoop fs -rm book_vectors-nv/*
    $ mvn package
    $ hadoop jar target/elephant-bird-vector-converter-0.1-SNAPSHOT-job.jar \
     technicalelvis.elephantBirdVectorConverter.App \
     book_vectors/ book_vectors-nv/


Output should be something like: 

    13/03/26 04:40:54 INFO elephantBirdVectorConverter.App: inputdir='book_vectors/', outputdir='book_vectors-nv/'
    13/03/26 04:40:54 INFO elephantBirdVectorConverter.App: Wrote '10' namedvectors to 'book_vectors-nv/part-m-00000'


Then run `mahout kmeans` on book_vectors-nv and `clusterdump` will show the twitter screennames in each cluster.
See habakkuk/analysis/README.md for clustering details.
