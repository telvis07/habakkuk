__author__ = 'telvis'

from fabric.api import run, local, env, sudo, settings
from fabric.contrib.files import append, contains, exists

env.user = 'telvis'

def chef_install():
    # setup chef dir

    install_ruby()
    run("gem install chef --no-rdoc --no-ri --version 11.10.4")
    line = "export rvmsudo_secure_path=1"
    append('/home/telvis/.profile', line)

def add_telvis():
    env.user = 'root'
    if not contains('/etc/passwd', 'telvis'):
        run("useradd -m -s /bin/bash -d /home/telvis telvis")
        run("cp -r /root/.ssh /home/telvis/")

    if not exists('/home/telvis/.ssh/'):
        run("chown -R telvis:telvis /home/telvis/.ssh/")

    # if not in sudoers
    line = "telvis    ALL=(ALL)       NOPASSWD: ALL"
    with settings(warn_only=True):
        ret = run("grep telvis /etc/sudoers")
    if ret.failed:
        append('/etc/sudoers', line)

def install_ruby():
    with settings(warn_only=True):
        run("source ~/.profile")
        ruby_path_failed = run("source $(rvm 2.1.1 do rvm env --path)").failed
        ruby_version_failed = run("ruby -v").failed

    if ruby_path_failed or ruby_version_failed:
        sudo("yum -y update")
        sudo("yum -y install curl")
        run("curl -L get.rvm.io | bash -s stable")
        run("source ~/.profile")
        run("rvm requirements")
        run("rvm install ruby-2.1.1")
        run("rvm use 2.1.1 --default")

    run("source $(rvm 2.1.1 do rvm env --path)")
    run("ruby -v")
    