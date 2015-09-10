def main(cr, pool):
    module_pool = pool.get('ir.module.module')
    module_pool.update_list(cr, 1)
    module = module_pool.search(cr, 1, [('name', '=', 'testmodule1')])
    module = module[0]
    module = module_pool.browse(cr, 1, module)
    if module.state != "installed":
        module_pool.button_immediate_install(cr, 1, [module.id])
