if [ -z "$1" ];then
    echo "need a json file"
else
    curl -XPUT 'http://localhost:9201/_template/template_habakkuk/' -d @$1
fi
