import datetime
from fabric import task, Connection
from invoke import Responder
try:
    from fabfile_secret import sudo_passwords
except ImportError:
    def sudo_passwords():
        return {}


def get_path():
    filename = "velolv_%s" % int(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    return "/var/backups/postgresql/%s" % filename, filename


@task
def rebuild_docker(c):
    c.run("docker build -t ameriks/project_velo:latest .")
    c.run("docker-compose -f dev.yml build django")
    c.run("docker push ameriks/project_velo:latest")


def dump_db(c, restore_to="/Users/agris/dumps/", path=None, filename=None):
    if not path or not filename:
        path, filename = get_path()

    c.run(
        "docker exec velo_postgres_1 sh -c \"su - postgres -c 'pg_dump -F c -b -v -f %(path)s.backup velolv'\"" % locals())

    c.get("%s.backup" % path, "%s%s.backup" % (restore_to, filename))
    return path


def restore_helper_function(c, postgres_id, db, path):
    # TERMINATE existing sessions
    c.run(
        "docker exec %(postgres_id)s sh -c \"su - postgres -c 'psql -c \\\"SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pid <> pg_backend_pid();\\\"'\"" % locals())

    # DROP and CREATE database
    c.run("docker exec %(postgres_id)s sh -c \"su - postgres -c 'psql -c \\\"DROP DATABASE IF EXISTS %(db)s;\\\"'\"" % locals())
    c.run("docker exec %(postgres_id)s sh -c \"su - postgres -c 'psql -c \\\"CREATE DATABASE %(db)s WITH OWNER = %(db)s;\\\"'\"" % locals())
    c.run("docker exec %(postgres_id)s sh -c \"su - postgres -c 'psql -d %(db)s -c \\\"CREATE EXTENSION postgis;\\\"'\"" % locals())
    # RESTORE
    c.run("docker exec %(postgres_id)s sh -c \"su - postgres -c 'pg_restore -d %(db)s --no-owner --role=%(db)s --disable-triggers --superuser=postgres -v %(path)s.backup'\"" % locals(), warn=True)


@task
def restore_local_db(c):
    path, filename = get_path()
    print(path)
    print(filename)
    with Connection('velo') as cc:
        cc.run('whoami')
        dump_db(cc, path=path, filename=filename)
    restore_helper_function(c, 'source_postgres_1', 'velolv', path)
