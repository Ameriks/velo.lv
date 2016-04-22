from .local import *

DATABASES = {
    'default': env.db("DATABASE_URL", default="postgres://postgres:postgres@postgres/velolv"),
}
