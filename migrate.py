import os, sys
from openerp import tools, netsvc
import openerp
import threading
import glob
import importlib
import argparse
from util import PoolProxy

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

class ConfigHelper(object):

    def __init__(self, env=os.environ, config=tools.config):
        self._env = env
        self._config = config

    def override_if_set_in_env(self, config_key, env_key):
        value = self._env.get(env_key)
        if value is not None:
            self._config[config_key] = value


def cursor():
    return openerp.modules.registry.RegistryManager.get(
        threading.current_thread().dbname
    ).db.cursor()


def get_releases_path():
    releases_path = tools.config.get('releases', None)
    if not releases_path:
        print(
            "Setup 'releases' in config file, it should be"
            " the absolute path of release steps directory"
        )
        sys.exit(1)
    return releases_path


def get_steps():
    path = get_releases_path()
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
    cr.commit()


def load_config():

    env = os.environ
    arguments = parse_args()
    tools.config.parse_config(['--config', arguments.config])
    tools.config['log_level'] = 'info'
    tools.config['syslog'] = False
    netsvc.init_logger()

    config_helper = ConfigHelper(env, tools.config)
    override = config_helper.override_if_set_in_env
    override('db_host', 'DB_HOST')
    override('db_name', 'DB_NAME')
    override('db_user', 'DB_USER')
    override('db_password', 'DB_PASSWORD')


def parse_args():
    prog, args = sys.argv[0], sys.argv[1:]
    parser = argparse.ArgumentParser(
        prog=prog
    )
    parser.add_argument(
        '--config',
        required=True,
        help=('Absolute path to openerp.conf')
    )
    return parser.parse_args(args)


def main():
    print "Migrating"
    load_config()

    db_name = tools.config['db_name']

    pool = PoolProxy(db_name)

    cr = cursor()
    apply_steps(cr, pool)
    cr.close()


if __name__ == '__main__':
    main()
