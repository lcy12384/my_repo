from pymysql import Connection
import json

def cre_mysql():
    # 创建数据库连接
    con = None
    try:
        con = Connection(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            database='course_recommend',
            autocommit=True
        )

        cursor = con.cursor()  # 建立游标对象
        return cursor

    except Exception as e:
        print('异常：', e)

def save_inf(i,cursor):
    try:
        load_f = open(f"D:/WorkSpace/毕业设计/xueyin_course_inf-2024.3.7/page{i}.txt", "r", encoding="utf-8")
        load_line = load_f.readlines()
        for line in load_line:
            l = line.strip()
            dic = json.loads(l)
            #课程基础信息
            sql_1 = (f"insert into course_inf values ({int(dic['id'])},'{dic['name']}',"
                   f"'{dic['teacher']}','{dic['school']}',{float(dic['scores'])},{int(dic['commentsCount'])},"
                   f"{int(dic['chooseCourseCount'])},{int(dic['curChooseCourseCount'])},{int(dic['curBbsAllCount'])},"
                   f"{int(dic['bbsAllCount'])},{int(dic['viewTimes'])},'{dic['url']}','{dic['courseLevel']}')")
            cursor.execute(sql_1)
            #课程开设期次
            sql_2 = f"insert into course_time values ({int(dic['id'])},'{dic['qici'][-1][0]}','{dic['endtime'][0]}')"
            cursor.execute(sql_2)
        load_f.close()
    except Exception as e:
        print("异常:",e)

def save_dir(i,cursor):
    try:
        load_f = open(f"D:/WorkSpace/毕业设计/xueyin_course_dir-2024.3.7/page{i}.txt", "r", encoding="utf-8")
        load_line = load_f.readlines()
        for line in load_line:
            l = line.strip()
            dic = json.loads(l)
            i = 1
            for dir in dic['dir']:
                sql = f"insert into course_dir values ({int(dic['id'])},'{dir}',{i})"
                cursor.execute(sql)
                i += 1
    except Exception as e:
        print("异常:", e)

def main():
    cursor = cre_mysql()
    for i in range(1,1056):
        # save_inf(i,cursor)
        # print(f"第{i}页课程基础信息输入完成！")
        save_dir(i,cursor)
        print(f"第{i}页课程目录信息输入完成！")
    if cursor:
        # 关闭连接
        cursor.close()

if __name__ == "__main__":
    main()