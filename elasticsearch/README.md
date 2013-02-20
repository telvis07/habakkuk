This directory contains convenience scripts to perform an faceted search queries against ES.

## Example
To get the data for Valentines day 2013,  I execute the following

    $ python bible_facet.py -s 2013-02-14 -e 2013-02-15

Which produces the following output. It shows the raw query json for the 
[Elasticsearch Query DSL](http://www.elasticsearch.org/guide/reference/query-dsl/index.html). 
Below that it shows the top 10 bible references. Its basically just a faceted search on the 
bibleverse field.

    {
      "query": {
        "filtered": {
          "filter": {
            "range": {
              "created_at_date": {
                "to": "2013-02-15T00:00:00",
                "include_upper": false,
                "from": "2013-02-14T00:00:00"
              }
            }
          },
          "query": {
            "match_all": {}
          }
        }
      },
      "facets": {
        "bibleverse": {
          "terms": {
            "field": "bibleverse",
            "order": "count",
            "size": 10
          }
        }
      },
      "size": 0
    }
    Total bibleverse 1568
        john 3:16 85
        i_john 4:19 42
        i_corinthians 13:4 31
        i_corinthians 13:13 24
        john 14:23 19
        psalm 37:23 18
        john 15:13 18
        i_corinthians 13:7 18
        philippians 4:13 17
        romans 5:8 15


## Files
* bible_facet.py - script used for simple faceted search
* dump_data_for_date.py - I use this to dump data each day to prevent data loss - lucene indexes can be fickle. Basically,
I execute the following every day. 

    $  python dump_data_for_date.py -s `date +"%F" --date "yesterday"` -o /path/to/backup/habakkuk_data/
* habakkuk-template.json and set-template.sh are to set the index template for habakkuk data stored in ES. Just execute the following
to set it up.    

    $ sh set-template.sh habakkuk-template.json
