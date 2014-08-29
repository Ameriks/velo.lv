class LegacyRouter(object):

    def db_for_read(self, model, **hints):
        """Point all operations on legacy models to the 'legacy' DB."""
        if model._meta.app_label == 'legacy':
            return 'legacy'
        return 'default'

    def db_for_write(self, model, **hints):
        """Our 'legacy' DB is read-only."""
        return False

    def allow_relation(self, obj1, obj2, **hints):
        """Forbid relations from/to Legacy to/from other app."""
        obj1_is_legacy = (obj1._meta.app_label == 'legacy')
        obj2_is_legacy = (obj2._meta.app_label == 'legacy')
        return obj1_is_legacy == obj2_is_legacy

    def allow_syncdb(self, db, model):
        return db != 'legacy' and model._meta.app_label != 'legacy'
