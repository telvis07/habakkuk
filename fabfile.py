from fabric.api import local, lcd
import requests
import re
import jsonlib2 as json
import smtplib,os
import sys
from email.mime.text import MIMEText


def sync_es(_date, target='es-1', pwd='.', host="yoyoma", port='9201'):
    """
    push local data to "production"
    """
    with lcd(os.path.join(pwd, 'elasticsearch')):
        _python = sys.executable
        local("{python} dump_data_for_date.py habakkuk -H {host}:{port} -s {DATE} -o /tmp/".format(python=_python,
                                                                                                   DATE=_date,
                                                                                                   host=host,
                                                                                                   port=port))
        fn = os.path.join('/tmp/', "habakkuk-{DATE}.json.gz".format(DATE=_date))
        local("{python} bulk_load.py -H {HOST}:9201 --index=habakkuk-all -i {fn}".format(python=_python,
                                                                                         HOST=target,
                                                                                         fn=fn))


def sync_topics(target='es-1', pwd='.', host="yoyoma", port='9201'):
    dump_topics(pwd=pwd, host=host, port='9201', destdir='/tmp/', rsync=False)
    new_topic_index(host=target, port=port)
    load_topics(pwd=pwd, host=target, port='9201', destdir='/tmp')


def new_topic_index(basename='topics', host="yoyoma", port='9201'):
    new_index(basename=basename, host=host, port=port)


def new_index(basename, host="yoyoma", port='9201'):
    """
    create a new index by incrementing the revnum and move the alias
    """
    alias = basename+"-all"
    update_template(basename=basename,
                    host=host,
                    port=port)

    # get aliases. find the current revnum
    r = requests.get("http://{ESHOST}:{ESPORT}/*/_alias/{alias}".format(ESHOST=host,
                                                                        ESPORT=port,
                                                                        alias=alias))
    data = r.json()
    if not data:
        next = 1
    else:
        assert len(data) == 1
        # create the next index name
        current_index = data.keys()[0]
        ma = re.match(basename+'-revnum-(?P<revnum>\d+)', current_index)
        assert ma
        next = int(ma.groups("revnum")[0])+1

    next_index = basename+"-revnum-{next}".format(next=next)

    # create next index
    r = requests.put("http://{ESHOST}:{ESPORT}/{INDEX}".format(ESHOST=host, ESPORT=port, INDEX=next_index))
    print "PUT {next_index} return {response}".format(next_index=next_index, response=r.json())

    if next == 1:
        # new index, new alias
        alias_cmd = {
            "actions" : [
                { "add" : { "index" : next_index, "alias" : alias } }
            ]
        }
    else:
        # move the alias
        alias_cmd = {
            "actions" : [
                { "remove" : { "index" : current_index, "alias" : alias } },
                { "add" : { "index" : next_index, "alias" : alias } }
            ]
        }


    r = requests.post("http://{ESHOST}:{ESPORT}/_aliases".format(ESHOST=host, ESPORT=port), data=json.dumps(alias_cmd))
    print "PUT _alias returned {response}".format(next_index=next_index, response=r.json())


def update_template(basename, host="yoyoma", port='9201'):
    template = 'elasticsearch/{}-template.json'.format(basename)
    r = requests.put("http://{ESHOST}:{ESPORT}/_template/template_{basename}/".format(ESHOST=host,
                                                                                      ESPORT=port,
                                                                                      basename=basename),
                                                                                      data=open(template).read())
    print "PUT _template returned {code} {response}".format(response=r.json(), code=r.status_code)


def dump_data(_date, pwd='.', host="yoyoma", port='9201', destdir="/opt/habakkuk_data/", rsync=True):
    with lcd(os.path.join(pwd, 'elasticsearch')):
        _python = sys.executable

        local("{python} dump_data_for_date.py habakkuk -s {DATE} -H {host}:{port} -o {outdir} ".format(python=_python,
                                                                                                       host=host,
                                                                                                       port=port,
                                                                                                       outdir=destdir,
                                                                                                       DATE=_date))
        if rsync:
            local("rsync -avz /opt/habakkuk_data bootsy:/mnt/goflex/habakkuk")


def dump_topics(pwd='.', host="yoyoma", port='9201', destdir='/opt/habakkuk_data/', rsync=False):
    with lcd(os.path.join(pwd, 'elasticsearch')):
        _python = sys.executable
        local("{python} dump_data_for_date.py topics --estype=topic_clusters -H {host}:{port} -o {destdir}".format(python=_python,
                                                                                                     host=host,
                                                                                                     port=port,
                                                                                                     destdir=destdir))
        local("{python} dump_data_for_date.py topics --estype=ranked_phrases -H {host}:{port} -o {destdir}".format(python=_python,
                                                                                                     host=host,
                                                                                                     port=port,
                                                                                                     destdir=destdir))
        if rsync:
            local("rsync -avz {} bootsy:/mnt/goflex/habakkuk".format(destdir))


def load_topics(pwd='.', host="yoyoma", port='9201', destdir='/opt/habakkuk_data/'):
    with lcd(os.path.join(pwd, 'elasticsearch')):
        _python = sys.executable

        # get aliases. find the current revnum
        r = requests.get("http://{ESHOST}:{ESPORT}/*/_alias/topics-all".format(ESHOST=host,
                                                                               ESPORT=port))
        alias_info = r.json()
        if alias_info and len(alias_info)>0:
            index = alias_info.keys()[0]
        else:
            index = 'topics-all'

        for _type in ('topic_clusters', 'ranked_phrases'):
            fn = os.path.join(destdir, "topics.{}.json.gz".format(_type))
            local("{python} bulk_load.py -H {HOST}:{port} --doctype={_type} --index={index} -i {fn}".format(python=_python,
                                                                                          index=index,
                                                                                          port=port,
                                                                                          HOST=host,
                                                                                          _type=_type,
                                                                                          fn=fn))

def send_email_file(filename, dryrun=False):
    output = open(filename).read()
    send_email(output)


def send_email(output, dryrun=False):
    import ConfigParser

    config = ConfigParser.RawConfigParser()
    # /home/telvis/conf/mail.cfg
    config.read(os.path.join('/home/telvis', 'conf', 'mail.cfg'))

    """
    read email from config. An example is:
    [dbname]
    to = me@foo.com
    """
    _send_email(config, 'telvis07@gmail.com', 'Daily Cron', output, dryrun=dryrun)


def _send_email(config, to, subj, msg, dryrun=False):
    """
    Send email based on config. Sample below:

    [email]
    mailfrom = Foo <foo@bar.com>
    username = foo
    password = fooF00!
    server=mail.bar.com
    port=25
    """
    toaddrs = [addr.strip() for addr in to.split(',')]
    # Config and Credentials (if needed)  
    me = config.get('email','mailfrom')
    username = config.get('email','username')
    password = config.get('email','password')
    server = config.get('email','server')
    port = config.getint('email','port')

    # We must choose the body charset manually
    for body_charset in 'US-ASCII', 'ISO-8859-1', 'UTF-8':
        try:
            msg.encode(body_charset)
        except UnicodeError:
            pass
        else:
            break
          
    # The actual mail send  
    try:
        msg = MIMEText(msg.encode(body_charset), 'plain', body_charset)
        msg['Subject'] = subj
        msg['From'] = me
        msg['To'] = ", ".join(toaddrs)

        if dryrun:
            print "Dry-run email:",msg.as_string()
            return

        server = smtplib.SMTP(server, port=port)
        server.login(username,password)  
        server.sendmail(me, toaddrs, msg.as_string())  
        server.quit() 
        print "Sent email:",msg.as_string()
    except smtplib.SMTPException:
        print "Error: unable to send email"


def stop_storm():
    local("storm kill habakkuk")


def start_storm():
    with lcd('./java/habakkuk-core'):
        local("storm jar target/habakkuk-core-0.0.1-SNAPSHOT-jar-with-dependencies.jar "\
              "technicalelvis.habakkuk.MainTopology habakkuk.properties")


def fix_the_data():
    pass
    # ./manage.py regex --fix /opt/habakkuk_data/ --fix-output-dir /tmp/habakkuk_data/
    # sudo mv /opt/habakkuk_data/ /opt/habakkuk_data.pre.20140417/
    # sudo mv /tmp/habakkuk_data/ /opt/habakkuk_data/
    # rsync -avz /opt/habakkuk_data.pre.20140417 bootsy:/mnt/goflex/habakkuk
    # rsync -avz /opt/habakkuk_data bootsy:/mnt/goflex/habakkuk
    # fab new_index:yoyoma
    # python elasticsearch/bulk_load.py -H yoyoma:9201 --index=habakkuk-revnum-3 -i /opt/habakkuk_data/
    # fab new_index:es-1
    # python elasticsearch/bulk_load.py -H es-1:9201 --index=habakkuk-revnum-2 -i /opt/habakkuk_data/
