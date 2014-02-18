ESHOST=localhost
ESPORT=9201
INDEX=habakkuk-revnum-2

if [ -z "$1" ];then
    echo "need a json file"
else
    curl -XPUT "http://$ESHOST:$ESPORT/_template/template_habakkuk/" -d @$1
fi


curl -XPUT "http://$ESHOST:$ESPORT/$INDEX"
curl -XPUT "http://$ESHOST:$ESPORT/$INDEX/_alias/habakkuk-all"
