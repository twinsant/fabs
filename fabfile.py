import os

from fabric.api import run
from fabric.api import prefix
from fabric.api import put
from fabric.api import sudo

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
