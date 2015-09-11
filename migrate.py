import os, sys
from openerp import tools
import glob
import importlib

import util
import config

# TODO: self install through migrate
# TODO: rename to something else that is not migrate since that sounds like migration to v8
# TODO: tests
# TODO: Readme , example config file


def install_module(cr, pool, module_name):
    module_pool = pool.get('ir.module.module')
    module_pool.update_list(cr, 1)
    module = module_pool.search(cr, 1, [('name', '=', module_name)])
    module = module[0]
    module = module_pool.browse(cr, 1, module)
    if module.state != "installed":
        module_pool.button_immediate_install(cr, 1, [module.id])
        db_name = tools.config['db_name']
        pool.restart()


def get_steps():
    path = config.get_releases_path()
    steps = []
    for filepath in glob.glob(os.path.join(path, "*.py")):
        fn = os.path.basename(filepath)
        # TODO: should ignore filenames that are not \d{4}.*
        if fn != "__init__.py":
            mod, _ = os.path.splitext(fn)
            steps.append(mod)
    return path, sorted(steps)


def get_last_applied_step(cr, pool):
    mig_pool = pool.get('north.migration')
    mig_ids = mig_pool.search(cr, 1, [])
    if len(mig_ids):
        return mig_pool.browse(cr, 1, mig_ids)[-1].name
    else:
        return '0000'


def apply_steps(cr, pool):
    last_applied = get_last_applied_step(cr, pool)
    path, steps = get_steps()
    sys.path.append(path)
    steps_to_apply = [step for step in steps if step > last_applied]
    if steps_to_apply:
        for step in steps_to_apply:
            apply_step(cr, pool, step)
            store_applied(cr, pool, step)
    else:
        print "\033[92mNothing to apply. Everything up to date.\033[0m"


def apply_step(cr, pool, name):
    mod = importlib.import_module(name)
    print("\033[92m[%s]\033[0m" % name)
    mod.main(cr, pool)


def store_applied(cr, pool, name):
    mig_pool = pool.get('north.migration')
    mig_pool.create(cr, 1, {
        "name": name
    })


def main():
    print "Migrating"
    db_name = config.load_config()
    pool = util.PoolProxy(db_name)
    with config.cursor() as cr:
        apply_steps(cr, pool)


if __name__ == '__main__':
    main()
