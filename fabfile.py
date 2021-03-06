from django_helper import Django
from env_setup import setup_fab_env
from fabric.api import env
import deployment
import setup_server
from common import Git
from pip_helper import Pip
from postgres_helper import Postgres
from fabric.operations import put
from cron import Cron
from fabric.context_managers import lcd
from deployment import symlink_nginx, symlink_upstart


def dump_db():
    setup_fab_env()


def setup_cron():
    setup_fab_env()
    Cron.setup_backup()


def deploy_test():
    setup_fab_env()
    Pip.create_virtual_env()
    Git.checkout_branch()
    Pip.set_project_directory()
    with lcd(env.project_path):
        Pip.install_requirements()
    symlink_nginx()
    Postgres.create_user_and_database()
    symlink_upstart()
    Django.create_local_settings()
    if not env.db_dump_dir:
        print "no dump directory provided, not loading in any existing data"
    else:
        Postgres.load_data()
    Django.migrate()
    Django.collect_static()
    Django.create_gunicorn_settings()
    Django.create_celery_settings()
    setup_server.restart_app()
    setup_server.restart_nginx()


def deploy_prod():
    setup_fab_env()
    deployment.create_env()
    Django.create_local_settings()
    if not env.db_dump_dir:
        print "no dump directory provided, not loading in any existing data"
    else:
        Postgres.load_data()
    Django.migrate()
    Django.collect_static()
    Django.create_gunicorn_settings()
    Django.create_celery_settings()
    setup_cron()
    setup_server.restart_app()
    setup_server.restart_nginx()


def django_deploy():
    setup_fab_env()
    Django.create_local_settings()
    Django.migrate()
    Django.load_lookup_lists()
    Django.collect_static()


def server_setup():
    setup_fab_env()
    setup_server.create_users()
    setup_server.install_common()
    setup_server.install_nginx()
    setup_server.make_home_directory()
    setup_server.install_postgres()
    setup_server.create_log_directory()
    setup_server.create_run_directory()
    deployment.create_env()
    django_deploy()
    setup_server.start_supervisord_or_restart_app()
    setup_server.restart_nginx()


def delete_environment():
    # note this does not change symlinks for for example nginx
    setup_fab_env()
    Postgres.drop_database()
    Pip.remove_virtualenv()
    Git.remove_code_dir()


def restart_nginx():
    setup_fab_env()
    setup_server.restart_nginx()


def restart_everything():
    setup_fab_env()
    setup_server.restart_app()
    setup_server.restart_nginx()


def start_supervisord():
    setup_fab_env()
    setup_server.start_supervisord_or_restart_app()

def symlink_upstart():
    setup_fab_env()
    deployment.symlink_upstart()


def database_backup():
    setup_fab_env()
    Postgres.dump_data()
    # the assumption is that the place we're putting this is exactly the
    # same as the place we're getting it from
    put(
        Postgres.get_recent_database_dump_path(),
        Postgres.get_recent_database_dump_path()
    )


def postgres(method, *args, **kwargs):
    setup_fab_env()
    result = getattr(Postgres, method)(*args, **kwargs)
    print result
    return result


def pip(method, *args, **kwargs):
    setup_fab_env()
    result = getattr(Pip, method)(*args, **kwargs)
    print result
    return result
