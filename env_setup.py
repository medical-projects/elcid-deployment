"""
Setup environment by reading configuration variables
"""
import os
import ConfigParser

from fabric.api import env


config = ConfigParser.RawConfigParser()
config.read(os.environ.get('ELCID_ENV', 'settings.ini'))


def get_release_name():
    return "{0}-{1}".format(env.project_name, env.branch_name)


def get(section, option, default=None):
    try:
        return config.get(section, option)
    except ConfigParser.NoOptionError:
        print 'No option for', section, option
        return default
    except ConfigParser.NoSectionError:
        print 'No section for', section, option
        return default


def setup_fab_env():
    env.project_name = get('project', 'name')
    env.settings_module_name = get('project', 'settings_module_name')
    env.branch_name = get('project', 'branch')
    env.log_dir = get('project', 'log_dir')
    env.release_name = get_release_name()
    github_user = get('project', 'github_user')
    env.github_url = "https://github.com/{0}/{1}.git".format(
        github_user, env.project_name,
    )
    env.database_owner = get('db', 'os_user')
    env.home_dir = os.path.abspath(config.get('system', 'base_dir'))
    env.project_path = os.path.join(env.home_dir, env.release_name)
    env.nix_user = get('project', 'user')
    env.app_owner = get('db', 'db_username')
    env.app_password = get('db', 'db_password')
    env.db_name = env.release_name.replace("-", "").replace(".", "")
    env.app_name = env.project_name
    env.http_proxy = get('system', 'http_proxy')
    # not set up to begin with created by common.create_virtual_env
    env.virtual_env_path = "/home/{0}/.virtualenvs/{1}".format(
        env.nix_user, env.release_name
    )
    env.pg_version = (9, 3)
    db_dump_dir = get('db', 'db_dump_dir')
    if db_dump_dir:
        env.db_dump_dir = os.path.join(env.home_dir, db_dump_dir)
    else:
        env.db_dump_dir = None

    env.host_string = get('remote', 'sync_host')
    env.password = get('remote', 'sync_password')

    env.pem_key = get('sync', 'pem_key')
    env.out_file = get('sync', 'out_file')
