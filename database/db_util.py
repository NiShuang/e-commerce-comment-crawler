import MySQLdb


def get_mysql_db(database_config):

    return  MySQLdb.connect(
        host=database_config['host'],
        port=database_config['port'],
        user=database_config['user'],
        passwd=database_config['password'],
        db=database_config['db'],
        charset=database_config['charset']
    )
