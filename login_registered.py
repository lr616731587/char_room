"""
创建一个数据表为user
    注册，终端输入 用户名和密码，将用户名和密码存入数据库中，用户名不重复
    登录，从终端输入用户名和密码，如果该用户存在则return登陆成功不存在则得到登录失败
    封装为类
"""
import  pymysql
import warnings
import hashlib


# 忽略警告
warnings.filterwarnings('ignore')

Database = 'stu'
HOST = '192.168.232.128'
USERNAME = 'zuozuo'
PASSWORD = 'qwe123'
Table = "create table if not exists user(id int primary key auto_increment,\
                            username varchar(16) unique not null, password varchar(32) not null );"
c_db = "create database if not exists USER1 charset utf8;"
u_db = "use USER1"


class User:
    def __init__(self):
        self.db = pymysql.connect(
            HOST,
            USERNAME,
            PASSWORD,
            Database,
            charset='utf8'
        )
        self.cur = self.db.cursor()
        self.cur.execute(c_db)
        self.cur.execute(u_db)
        self.cur.execute(Table)

    def registered(self):
        """
        注册
        :return:
        """
        while True:
            print('\r用户注册', end='')
            username = input('username')
            password = input('password')
            try:
                sql = "insert into user(username, password) values (%s, %s);"

                self.cur.execute(sql, [username, self.md5(password.encode())])
                self.db.commit()

                break
            except Exception as e:
                self.db.rollback()
                print('用户名已存在\n', e)
        print('{}注册成功'.format(username))

    def login(self):
        """
        登录
        :return:
        """
        print('\r用户登录')
        cum = 0
        while True:
            username = input('username')
            password = input('password')
            try:
                sql_u = "select * from user where username=%s;"
                self.cur.execute(sql_u, [username])
                data_u = self.cur.fetchone()
                if data_u is not None:
                    sql = "select * from user where username=%s and password=%s;"

                    self.cur.execute(sql, [username, self.md5(password.encode())])
                    data = self.cur.fetchone()
                    if data is None:
                        print('用户名或密码错误')
                        forget = input('是否找回密码：（Yes/No）')
                        if forget == 'Yes':
                            self.forget_pwd(username)
                    else:
                        print('{}登录成功'.format(data[1]))
                        break
                else:
                    print('用户名不存在')
                    cum += 1
                    if cum >= 3:
                        lo = input('是否注册(Yes/No)')
                        if lo == 'Yes':
                            self.registered()
            except Exception as e:
                print(e)

    def md5(self, password):
        """
        MD5加密
        :param password:
        :return:
        """
        md5 = hashlib.md5()
        md5.update(password)
        return md5.hexdigest()

    def close(self):
        self.cur.close()
        self.db.close()

    def forget_pwd(self, username):
        pwd = input('输入新的密码')
        sql = "update user set password=%s where username=%s;"
        try:
            self.cur.execute(sql, [self.md5(pwd.encode()), username])
            self.db.commit()
        except Exception as e:
            print('修改失败', e)
        print('{}修改密码成功'.format(username))


if __name__ == '__main__':
    u = User()
    while True:
        print('\r=====================\n\
                \r=====registered======\n\
                \r========login========\n\
                \r=========quit========\n\
                \r=====================', end='')
        cmd = input('\nCMD:')
        if cmd == 'registered':
            u.registered()
        elif cmd == 'quit':
            print('\r退出程序', end='')
            u.close()
            break
        else:
            u.login()