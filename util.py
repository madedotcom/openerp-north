from openerp import pooler


class PoolProxy(object):
    _pool = None
    _instance = None
    _db_name = None
    def __new__(cls, db_name):
        if not cls._instance:
            cls._db_name = db_name
            pool = pooler.get_pool(cls._db_name)
            cls._pool = pool
            cls._instance = super(PoolProxy, cls).__new__(cls)
        return cls._instance

    def get(self, *args, **kwargs):
        return self._pool.get(*args, **kwargs)

    def restart(self):
        _, self._pool = pooler.restart_pool(self._db_name)


