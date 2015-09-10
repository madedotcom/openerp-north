def main(cr, pool):
    pool.get('idea.idea').create(cr, 1, {
        "name" : "first idea",
        "state": "draft",
        "category_id": 1
    })
