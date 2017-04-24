import datetime

from fabric.api import run, env, hosts, sudo, cd, task, local, get
from fabric.tasks import Task

env.hosts = ['velo', ]
env.use_ssh_config = True

@task
def dump_db():
    name = "velo_%s.backup" % int(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    path = "/var/backups/postgresql/%s" % name
    postgres_id = run('docker ps | grep "velo_postgres_1" | cut -c1-12')
    run("docker exec %(postgres_id)s sh -c \"su - postgres -c 'pg_dump -F c -b -v -f %(path)s velolv'\"" % locals())

    get(path, "~/dumps/")

    local_postgres_id = local('docker ps | grep "source_postgres_1" | cut -c1-12', capture=True)

    # TERMINATE existing sessions
    local("docker exec %(local_postgres_id)s sh -c \"su - postgres -c 'psql -c \\\"SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pid <> pg_backend_pid();\\\"'\"" % locals())

    # DROP and CREATE database
    local("docker exec %(local_postgres_id)s sh -c \"su - postgres -c 'psql -c \\\"DROP DATABASE IF EXISTS velolv;\\\"'\"" % locals())
    local("docker exec %(local_postgres_id)s sh -c \"su - postgres -c 'psql -c \\\"CREATE DATABASE velolv WITH OWNER = velolv;\\\"'\"" % locals())

    # RESTORE
    local("docker exec %(local_postgres_id)s sh -c \"su - postgres -c 'pg_restore -d velolv -v %(path)s'\"" % locals())


@task
def rebuild_docker():
    local("docker build -t ameriks/project_velo:latest .")
    local("docker-compose -f dev.yml build django")
    local("docker push ameriks/project_velo:latest")


@task
def upgrade():
    sudo('apt-get update')
    sudo('apt-get upgrade -y')


@task
def update_all_dockers():
    with cd('/var/lib/app/project_velo'):
        # Pull all base images
        run("docker pull redis:alpine")
        run("docker pull ameriks/project_velo:latest")

        # Build all images
        run("docker-compose -p velo build --pull elk")
        run("docker-compose -p velo build --pull postgres")
        run("docker-compose -p velo build --pull mariadb")
        run("docker-compose -p velo build --pull sendy")
        run("docker-compose -p velo build --pull mainrouter")
        run("docker-compose -p velo build --pull letsencrypt")
        run("docker-compose -p velo build --pull duplicity")

        # UP
        run("docker-compose -p velo up -d -t 30")

        # Removed all unused images
        run('docker rmi -f $(docker images | grep "<none>" | awk "{print \$3}")')


class VeloDeploy(Task):
    name = "deploy"
    docker_id = None
    need_static_regenerate = False
    need_migrate = False
    need_service_restart = False
    need_full_restart = False
    pull_new = False

    def get_projectvelo_id(self):
        self.docker_id = run('docker ps | grep "velo_projectvelo_1" | cut -c1-12')

    def collect_static(self):
        run("docker exec -it %s /app/manage.py collectstatic --no-input" % self.docker_id)
        self.need_static_regenerate = False

    def restart_services(self):
        # Restart all services
        run("docker exec -it %s s6-svc -h /var/run/s6/services/gunicorn" % self.docker_id)
        run("docker exec -it %s s6-svc -h /var/run/s6/services/celeryworker" % self.docker_id)
        run("docker exec -it %s s6-svc -h /var/run/s6/services/celerybeat" % self.docker_id)

    def migrate(self):
        run("docker exec -it %s /app/manage.py migrate" % self.docker_id)
        self.need_migrate = False

    def git_pull(self):
        git_output = run("docker exec -it %s sh -c 'cd /app && git pull'" % self.docker_id)
        if "static/" in git_output or 'requirements/' in git_output:
            self.need_static_regenerate = True

        if "migrations/" in git_output:
            self.need_migrate = True

        if ".py" in git_output or ".html" in git_output:
            self.need_service_restart = True

    def pull_docker(self):
        pull_result = run("docker pull ameriks/project_velo:latest")
        if 'Image is up to date' not in pull_result:
            self.need_full_restart = True

    def restart_docker_compose(self):
        with cd('/var/lib/app/project_velo'):
            run("docker-compose -p velo up -d projectvelo")

    def run(self):
        self.get_projectvelo_id()
        self.git_pull()
        if self.need_migrate:
            self.migrate()

        if self.need_static_regenerate:
            self.collect_static()

        if self.pull_new:
            self.pull_docker()

        if not self.need_full_restart and self.need_service_restart:
            self.restart_services()
        elif self.need_full_restart:
            self.restart_docker_compose()
instance = VeloDeploy()


