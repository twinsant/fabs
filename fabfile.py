import os

from fabric.api import run
from fabric.api import prefix
from fabric.api import put
from fabric.api import sudo
from fabric.api import cd
from fabric.api import local
from fabric.api import env
from fabric.contrib.files import exists

def mk_ve_sentry():
    '''fab -H user@host mk_ve_sentry
    '''
    run('mkvirtualenv -p python2.7 --no-site-packages --distribute sentry')

def install_sentry():
    with prefix('workon sentry'):
        run('pip install MySQL-python')
        run('pip install eventlet')
        run('pip install -U sentry')
        run('pip install -U raven') # Fix 401 error
        run('pip freeze')

def cat_sentry_conf():
    run('cat ~/.sentry/sentry.conf.py')

def init_sentry():
    '''http://sentry.readthedocs.org/en/latest/config/index.html
    http://sentry.readthedocs.org/en/latest/quickstart/index.html

    mysql setup:
    mysql> create database sentry;
    mysql> grant all privileges on sentry.* to 'user'@'localhost' identified by 'password';
    mysql> flush privileges;

    sentry upgrade
    '''
    with prefix('workon sentry'):
        run('sentry init')

# MySQL
def yum_q_mysql():
    run('rpm -q mysql')

def cat_my_cnf():
    run('cat /etc/my.cnf')

def put_root(filename, path):
    dest = os.path.join(path, filename)
    put(filename, dest, use_sudo=True)
    sudo('chown root:root %s' % dest)
    run('ls -lh %s' % dest)

def config_mysql():
    i = raw_input('Will overwrite /etc/my.cnf. [nY]: ')
    if i == 'Y':
        put_root('my.cnf', '/etc/')

def install_build():
    sudo('apt-get install build-essential libpcre3-dev zlib1g-dev libssl-dev tcl8.5')

def install_redis():
    latest = 'redis-2.6.10.tar.gz'

    run('mkdir -p dl')
    with cd('dl'):
        run('pwd')
        run('rm -f %s' % latest)
        run('wget http://redis.googlecode.com/files/%s' % latest)
    run('tar -zxvf dl/%s' % latest)
    with cd(latest.replace('.tar.gz', '')):
        run('make')
        run('make test')

def restart_redis():
    sudo('/etc/init.d/redis_6379 stop')
    sudo('/etc/init.d/redis_6379 start')

def config_redis():
    latest = 'redis-2.6.10.tar.gz'
    with cd('%s/utils' % latest.replace('.tar.gz', '')):
        # Press enter and set redis exe path, e.g. /home/twinsant/redis-2.6.10/src/redis-server
        sudo('./install_server.sh')
    sudo('mkdir -p /srv/db/redis/6379')
    # 6379.conf change lines: bind, dir
    put_root('6379.conf', '/etc/redis/')
    # redis_6379 change lines: EXEC, CLIEXEC, REDISHOST
    put_root('redis_6379', '/etc/init.d/')
    sudo('chmod +x /etc/init.d/redis_6379')
    restart_redis()

def ntpdate():
    sudo('/usr/sbin/ntpdate 1.pool.ntp.org')
    run('date')

def install_svn():
    sudo('apt-get install subversion')

def install_venv():
    sudo('pip install virtualenvwrapper')
    run('mkdir -p ~/.virtualenvs')

def config_venv():
    # Modify .bashrc
    # export WORKON_HOME=~/.virtualenvs
    # source /usr/local/bin/virtualenvwrapper.sh
    run('cat ~/.bashrc')

def install_supervisor():
    sudo('pip install supervisor')

def config_supervisor():
    if not exists('/etc/supervisord.conf'):
        sudo('/usr/local/bin/echo_supervisord_conf > /etc/supervisord.conf')
    else:
        local('cat supervisord.conf')

# fab -H git@host git_bare_init --set project=foo
def git_bare_init():
    project_dir = '%s.git' % env.project
    run('mkdir %s' % project_dir)
    run('cd %s&&git --bare init' % project_dir)
