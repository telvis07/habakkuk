# Habakkuk
Habakkuk is an application for filtering tweets containing Christian bible references. The goal is to capture the book name, chapter number, verse number and tweet text for further analysis.

## Dependencies
This project requires postgresql

    sudo apt-get install postgresql-8.4 postgresql-client-8.4 postgresql-server-dev-8.4
    sudo apt-get install build-essential python-devel
    sudo add-apt-repository ppa:chris-lea/node.js
    sudo apt-get update
    sudo apt-get install nodejs
    sudo npm install karma

    coverage run --source='.' manage.py test web topic_analysis
    coverage report

## Web app
This is the frontend code for [http://bakkify.com](http://bakkify.com).

### Django
This project uses [django](https://www.djangoproject.com/). Perform the following to set up the virtual environment.

    $ virtualenv .
    $ . ./bin/activate
    $ pip install -r requirements.txt

### Angular
This project uses [angularJS](http://angularjs.org/) and [karma](https://github.com/vojtajina/karma/) for JS unit testing. To test...

    # install dependencies
    karma start

## Topic Analysis

The topic analysis is based on the [NMF topic extraction example](http://scikit-learn.org/stable/auto_examples/applications/topics_extraction_with_nmf.html). 
It performs kmeans clustering on velocity features for bibleverses. Then it applies the NMF analysis to extract 
topics from text for each cluster. Finally, it uses [hierarchical clustering](https://pypi.python.org/pypi/cluster/1.1.0b1)
to filter (nearly) duplicate topics and rank the topics.


## Real-time processing
This project uses a [storm](http://storm-project.net/) topology to analyze tweets from the [twitter sample stream](https://dev.twitter.com/docs/streaming-apis/streams/public).
The entry point is a storm spout that uses [twitter4j](http://twitter4j.org/en/index.html) to access the stream with a username and password. 
Tweets are then passed to a storm shell bolt implemented in Python that applies a regular expression 
for detecting Christian bible references. Finally, a bolt receives the tuple with a bible reference tag and stores it to 
elasticsearch.

For more information refence the [storm concepts wiki](https://github.com/nathanmarz/storm/wiki/Concepts). 
I also have a [habakkuk starter page](http://technicalelvis.com/blog/2012/06/21/habakkuk-starter/) that provides some background.

## Data Stores

### Elasticsearch
This project uses [ElasticSearch](http://www.elasticsearch.org/) as backend storage. Please reference the site for details.


### Accumulo
I experimented with using [Apache Accumulo](http://accumulo.apache.org/). The code has been disabled but the Bolt is
still there is anyone wants to try it. It works fine but I found Elasticsearch worked better for this project.

### Hadoop
Scripts in analysis/ depend on [Cloudera Hadoop CDH3](https://ccp.cloudera.com/display/CDHDOC/CDH3+Documentation).

# Sub-Directories
* java - [Storm Application](http://storm-project.net/)
* bible_verse_matching - Tools to build and test the bible reference regular expressions. Also dictionary files for pig and mahout.
* elasticsearch - Index templates and tools to query elasticsearch
* accumulo - Table initialization scripts
* config - Configuration files for setting up storm with [supervisord](http://supervisord.org/)
* analysis - pig scripts for data analysis
* web - web front-end
* topic_analysis - topic modeling using scikit-learn
