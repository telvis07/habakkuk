## Bible Reference Regex
**NOTE**: There are manual edits to bible_verse_matching/find_all_scripture.py. Don't overwrite without
adding the changes to the autogen script.

regex_generator.py is an app to auto-generate find_all_scriptures.py - which is used by the storm application to match scriptures.    

To re-build the regex after modifying the regex_generator.py  
  
    $ cd habakkuk    
    $ virtualenv .     
    $ pip install -r requirements.txt
    $ ./manage.py regex --build      
    $ mv find_all_scriptures.py java/habakkuk-core/multilang/resources/find_all_scriptures.py    


To test changes against known matches    

    $ ./manage.py regex --test    


## Bible book and verse ID
normalize_bible_verses.py generates a unique ID for each 'book' or 'book chapter:verse'. data/ 
includes a xml copy of the King James Version (KJV) Bible used as input to the script.
The output can be used for pig scripts to JOIN on stored habakkuk to data on the book or bibleverse.
The resulting IDs are use as offsets in feature vectors.

For book

    $ python normalize_bible_verses.py -f data/kjv.xml

For bibleverse

    $ python normalize_bible_verses.py -f data/kjv.xml --verse

