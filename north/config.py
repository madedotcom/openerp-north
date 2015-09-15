import os
import sys
from openerp import tools, netsvc
import openerp
import argparse
from contextlib import contextmanager
import threading


class ConfigHelper(object):

    def __init__(self, env=os.environ, config=tools.config):
        self._env = env
        self._config = config

    def override_if_set_in_env(self, config_key, env_key):
        value = self._env.get(env_key)
        if value is not None:
            self._config[config_key] = value


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
    parser.add_argument(
        '--loglevel',
        default='error',
        help=(
            'Log level: choose from "info", "debug_rpc", "warn", "test", '
            '"critical", "debug_sql", "error", "debug", "debug_rpc_answer", '
            '"notset"'
        )
    )
    return parser.parse_args(args)


def load_config():

    env = os.environ
    arguments = parse_args()
    tools.config.parse_config(['--config', arguments.config])
    tools.config['log_level'] = arguments.loglevel
    tools.config['syslog'] = False
    netsvc.init_logger()

    config_helper = ConfigHelper(env, tools.config)
    override = config_helper.override_if_set_in_env
    override('db_host', 'DB_HOST')
    override('db_name', 'DB_NAME')
    override('db_user', 'DB_USER')
    override('db_password', 'DB_PASSWORD')

    return tools.config['db_name']


def get_releases_path():
    releases_path = tools.config.get('releases', None)
    if not releases_path:
        print(
            "Setup 'releases' in config file, it should be"
            " the absolute path of release steps directory"
        )
        sys.exit(1)
    return releases_path


@contextmanager
def cursor():
    try:
        cr = openerp.modules.registry.RegistryManager.get(
            threading.current_thread().dbname
        ).db.cursor()
        yield cr
        cr.commit()
    except:
        cr.rollback()
        raise
    finally:
        cr.close()
