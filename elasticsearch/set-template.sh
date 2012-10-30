if [ -z "$1" ];then
    echo "need a json file"
else
    curl -XPUT 'http://localhost:9200/_template/template_habakkuk/' -d @$1
fi
