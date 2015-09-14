
# openerp-north

Usage examples:

You want to install a new module testmodule1:

```python
# 0001_install_test_module.py
from util import install_module

def main(cr, pool):
    install_module(cr, pool, 'testmodule1')
```

You can apply this change with `python migrate.py --config=<path_to_openerp_conf>`

```
Migrating
[0001_install_test_module]
```

Run it again, now the output will be:

```
Migrating
Nothing to apply. Everything up to date.
```

You make changes to the module, like add another column `name2`. You need to create a migration script like:


```python
# 0002_change_test_module.py
from util import update_module

def main(cr, pool):
    update_module(cr, pool, 'testmodule1')

    pool.get('test.mod1').create(cr, 1, {
        "name" : "vim is awesome",
        "name2" : "for sure",
    })
```

You can apply this change with `python migrate.py --config=<path_to_openerp_conf>`

```
Migrating
[0002_change_test_module]
```

The changes will now be applied.
