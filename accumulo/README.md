# Habakkuk Text Table
- Stores bible verse match, date and matched tweet text
- The schema is column family: column qualifier - "YYYYMMDD:book verse"

Demo:
<pre>
> createtable habakkuk_text
> insert 1 20120101 "John 3:16" "{_id=1, tweet='tweet 1}"
> insert 2 20120101 "John 3:16" "{_id=2, tweet='tweet 2}"
> insert 3 20120101 "John 3:16" "{_id=3, tweet='tweet 3}"
> insert 4 20120101 "Mark 1:2"  "{_id=4, tweet='tweet 4}"
> insert 5 20120102 "Mark 1:2"  "{_id=5, tweet='tweet 4}"
> scan
    1 20120101:John 3:16 []    {_id=1, tweet='tweet 1}
    2 20120101:John 3:16 []    {_id=2, tweet='tweet 2}
    3 20120101:John 3:16 []    {_id=3, tweet='tweet 3}
    4 20120101:Mark 1:2 []    {_id=4, tweet='tweet 4}
    5 20120102:Mark 1:2 []    {_id=5, tweet='tweet 4}
> scan -c 20120101
    1 20120101:John 3:16 []    {_id=1, tweet='tweet 1}
    2 20120101:John 3:16 []    {_id=2, tweet='tweet 2}
    3 20120101:John 3:16 []    {_id=3, tweet='tweet 3}
    4 20120101:Mark 1:2 []    {_id=4, tweet='tweet 4}
> scan -c "20120101:John 3:16"
    1 20120101:John 3:16 []    {_id=1, tweet='tweet 1}
    2 20120101:John 3:16 []    {_id=2, tweet='tweet 2}
    3 20120101:John 3:16 []    {_id=3, tweet='tweet 3}
</pre>

# Habakkuk Verse Count Table
- Stores bible verse with daily counts
- The schema is column family: column qualifier - "YYYYMMDD:book verse"

To create the table:
<pre>
> createtable --no-default-iterators habakkuk_verse_count
> setiter -t habakkuk_verse_count -p 10 -scan -minc -majc -class org.apache.accumulo.core.iterators.user.SummingCombiner


    SummingCombiner interprets Values as Longs and adds them together.  A variety of encodings (variable length, fixed length, or string) are available
    ----------> set SummingCombiner parameter all, set to true to apply Combiner to every column, otherwise leave blank. if true, columns option will be ignored.: true
    ----------> set SummingCombiner parameter columns, <col fam>[:<col qual>]{,<col fam>[:<col qual>]} escape non-alphanum chars using %<hex>.:
    ----------> set SummingCombiner parameter lossy, if true, failed decodes are ignored. Otherwise combiner will error on failed decodes (default false): <TRUE|FALSE>:
    ----------> set SummingCombiner parameter type, <VARLEN|FIXEDLEN|STRING|fullClassName>: STRING

> insert "John 3:16" 20120101 "" 1
> insert "John 3:16" 20120101 "" 1
> insert "John 3:16" 20120101 "" 1
> insert "Mark 1:2" 20120101  "" 1
> insert "Mark 1:2" 20120102  "" 1
> scan
    John 3:16 20120101: []    3
    Mark 1:2 20120101: []    1
    Mark 1:2 20120102: []    1
</pre>

