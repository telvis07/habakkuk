# Bible Reference Regex

regex_generatory.py is an app to auto-generate find_all_scriptures.py - which is used by the storm application to match scriptures.    

To re-build the regex after modifying the regex_generator.py  
  
    $ cd habakkuk    
    $ virtualenv .     
    $ pip install -r requirements.txt
    $ ./manage.py regex --build      
    $ mv find_all_scriptures.py java/habakkuk-core/multilang/resources/find_all_scriptures.py    


To test changes against known matches    

    $ ./manage.py regex --test    
