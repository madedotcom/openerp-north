from osv import osv
from osv import fields

'''
TODO: we might want to rename this:
    migration - can be confused with migrating to version 8
    release - does not really represent the concept of one-off script
'''


class migration(osv.osv):
    _name = 'north.migration'
    _columns = {
        'name': fields.char('Name', size=64, required=True)
    }
    _sql_constraints = [(
        'name_uniq',
        'unique(name)',
        'Migrations must be unique!'
    )]
    _order = 'name asc'
