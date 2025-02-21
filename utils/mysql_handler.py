import pymysql
import traceback
import threading


class MysqlHandler:
    def __init__(self, host, port, user, password, dbname):
        self.host = host  # Host
        self.port = port  # 端口
        self.user = user  # 用户
        self.password = password  # 密码
        self.dbname = dbname  # 数据库的名，新建的数据库名
        self.conn = None
        self.cursor = None

    def connect(self):  # 用于连接数据库
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.dbname, charset='utf8')
        self.cursor = self.conn.cursor()

    def close(self):  # 用于断开连接
        self.cursor.close()
        self.conn.close()

    def get_one(self, sql):  # 查询一条数据；类型为元组
        res = None  # sql参数为查询mysql语句
        try:
            self.connect()
            self.cursor.execute(sql)  # 执行查询
            res = self.cursor.fetchone()  # 获取数据
            self.close()  # 关闭
        except Exception as e:
            res = ("error, " + str(res) + str(traceback.format_exc()) + str(e),)
        return res

    def get_all(self, sql):  # 获取所有；类型为元组
        res = ()  # sql参数为查询mysql语句
        try:
            self.connect()  # 连接数据库
            self.cursor.execute(sql)  # 执行查询语句
            res = self.cursor.fetchall()  # 接收全部的返回结果行
            self.close()
        except Exception as e:
            res = ("error, " + str(res) + str(traceback.format_exc()) + str(e),)
        return res

    def get_all_obj(self, sql, table_name, *args):  # 获取所有；类型为列表
        res_list = []  # sql:sql查询语句
        fields_list = []
        if len(args) > 0:
            for item in args:  # 遍历字典key
                fields_list.append(item)  # 添加kry
        else:
            fields_sql = "select COLUMN_NAME from information_schema.COLUMNS where " \
                         "table_name ='%s'and table_schema = '%s'" % (table_name, self.dbname)
            # column name列名 information sheet： 信息表
            fields = self.get_all(fields_sql)  # 执行语句，获取所有表信息(("id,"),("name",),("age,"))
            for item in fields:  # 遍历key
                fields_list.append(item[0])  # 添加
        res = self.get_all(sql)  # 获取传参的查询语句的数据，元组类型tuple
        for item in res:
            obj = {}
            count = 0
            for x in item:
                obj[fields_list[count]] = x
                count += 1
            res_list.append(obj)
        return res_list

    def insert(self, sql):  # 插入
        return self.__edit(sql)

    def update(self, sql):  # 修改
        return self.__edit_update(sql)

    def delete(self, sql):  # 删除
        return self.__edit(sql)

    def __edit_update(self, sql):
        res = ''
        count = 0
        lock = threading.Lock()
        lock.acquire()
        try:
            self.connect()
            count = self.cursor.execute(sql)
            res = self.cursor.lastrowid
            self.conn.commit()
            self.close()
        except Exception as e:
            res = {
                "count": count,
                "content": "failed" + "\n" + str(count) + "\n" + str(traceback.format_exc()) + str(e),
                "success": count
            }
            self.conn.rollback()
        finally:
            lock.release()
            # json cannot add str
            # return res + str(count)
            return res

    def __edit(self, sql):
        count = 0
        try:
            self.connect()
            count = self.cursor.execute(sql)
            res = self.cursor.lastrowid
            self.conn.commit()
            self.close()
        except Exception as e:
            res = {
                "count": count,
                "content": "failed" + "\n" + str(count) + "\n" + str(traceback.format_exc()) + str(e),
                "success": count
            }
            self.conn.rollback()
        # json cannot add str
        # return res + str(count)
        return res
