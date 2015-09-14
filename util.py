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


def install_module(cr, pool, module_name):
    module_pool = pool.get('ir.module.module')
    module_pool.update_list(cr, 1)
    module = module_pool.search(cr, 1, [('name', '=', module_name)])
    module = module[0]
    module = module_pool.browse(cr, 1, module)
    if module.state != "installed":
        module_pool.button_immediate_install(cr, 1, [module.id])
        pool.restart()


def update_module(cr, pool, module_name):
    module_pool = pool.get('ir.module.module')
    module_pool.update_list(cr, 1)
    module = module_pool.search(cr, 1, [('name', '=', module_name)])
    module = module[0]
    module = module_pool.browse(cr, 1, module)
    if module.state == "installed":
        module_pool.button_upgrade(cr, 1, [module.id])
        upgrade_pool = pool.get('base.module.upgrade')
        upgrade_pool.upgrade_module(cr, 1, None)
        pool.restart()

