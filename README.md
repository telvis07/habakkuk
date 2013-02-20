# Habakkuk
Habakkuk is an application for filtering tweets containing Christian bible references. The goal is to capture the book name, chapter number, verse number and tweet text for further analysis.

## Django
This project uses [django](https://www.djangoproject.com/) for project organization purposes. Perform the following to set up the virtual environment.

    $ virtualenv .
    $ . ./bin/activate
    $ pip install -r requirements.txt

##  Storm
This project uses a [storm](http://storm-project.net/) topology to analyze tweets from the [twitter sample stream](https://dev.twitter.com/docs/streaming-apis/streams/public).
The entry point is a storm spout that uses [twitter4j](http://twitter4j.org/en/index.html) to access the stream with a username and password. 
Tweets are then passed to a storm shell bolt implemented in Python that applies a regular expression 
for detecting Christian bible references. Finally, a bolt receives the tuple with a bible reference tag and stores it to 
elasticsearch.

For more information refence the [storm concepts wiki](https://github.com/nathanmarz/storm/wiki/Concepts). 
I also have a [habakkuk starter page](http://technicalelvis.com/blog/2012/06/21/habakkuk-starter/) that provides some background.

## Elasticsearch
This project uses [ElasticSearch](http://www.elasticsearch.org/) as backend storage. Please reference the site for details.

## Accumulo
I experimented with using [Apache Accumulo](http://accumulo.apache.org/). The code has been disabled but the Bolt is
still there is anyone wants to try it. It works fine but I found Elasticsearch worked better for this project.

# Sub-Directories
* java - [Storm Application](http://storm-project.net/)
* bible_verse_matching - Tools to build and test the bible reference regular expressions.
* elasticsearch - Index templates and tools to query elasticsearch
* accumulo - Table initialization scripts
* config - Configuration files for setting up storm with [supervisord](http://supervisord.org/)
