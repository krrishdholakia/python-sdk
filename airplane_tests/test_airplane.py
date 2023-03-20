import airplane

import airplane_tests


@airplane.task(
    resources = [
        airplane_tests.Resource('demo_db', 'db')
    ]
)
def call_another_task():
    results = airplane_tests.sql.query('db', 'select * from accounts')
    return results.output

