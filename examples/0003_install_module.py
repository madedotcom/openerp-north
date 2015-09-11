from migrate import install_module

def main(cr, pool):
    install_module(cr, pool, 'testmodule1')
