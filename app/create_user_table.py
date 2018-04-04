from werkzeug.security import generate_password_hash, check_password_hash

import os,sys
pkg_path = os.path.sep.join(
    (os.path.abspath(os.curdir).split(os.path.sep)[:-2]))
if pkg_path not in sys.path:
    sys.path.append(pkg_path)

from future_mysql import dbBase
from pbc_crawler import db_api as city_table_api
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Index, Float, Boolean
from sqlalchemy import Table

get_cities = city_table_api.get_cities

class User(dbBase.DB_BASE):

    def __init__(self):
        db_name = 'flask'
        table_name = 'password'
        super(User, self).__init__(db_name)

        self.table_struct = Table(table_name, self.meta,
                                  Column('id',Integer,primary_key=True,autoincrement=False),
                                  Column('username', String(64)),
                                  Column('work_unit',String(64)),
                                  Column('password_hash', String(128)))

    def create_table(self):
        self.user_struct = self.quick_map(self.table_struct)
        
class Task(dbBase.DB_BASE):
    
    def __init__(self):
        db_name = 'flask'
        table_name = 'task'
        super(Task, self).__init__(db_name)

        self.table_obj = Table(table_name, self.meta,
                                  Column('index',Integer,primary_key = True,autoincrement = True),
                                  Column('username', String(64)),
                                  Column('task_from', String(64)),
                                  Column('task_to',String(64)),
                                  Column('task_name',String(64)),
                                  Column('task_id',String(128)),
                                  Column('orgnization',String(128)),
                                  Column('level',String(16)),
                                  Column('submit_date',Integer),
                                  Column('submit_time',Integer),
                                  Column('params',String(256))
                                  )

    def create_table(self):
        self.table_struct = self.quick_map(self.table_obj)

def create_user_table():
    user = User()
    user.create_table()
    indict = {
        'id': 3,
        'username': 'lyx',
        'password_hash': generate_password_hash('123456'),
        'work_unit':'beijing'
    }
    user.insert_dictlike(user.user_struct, indict)
    print 'successed!'
    
def create_task_table():
    task = Task()
    task.create_table()
    print 'successed!'
    
def test_insert():
    dbapi = Task()
    dbapi.create_table()
    d = {i:str(1) for i in dbapi.get_column_names(dbapi.table_struct)}
    d.pop('index')
    dbapi.insert_dictlike(dbapi.table_struct,d)
    a = [None,]
    a.extend([ i for i in d.values() ])
    dbapi.insert_listlike(dbapi.table_struct,a)

    
if __name__ == '__main__':
#     create_task_table()
#     test_insert()
    create_user_table()
    
    