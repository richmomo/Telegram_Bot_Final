import pymysql


host='localhost'
port=3306
user='root'
password='o2tunes123'
db_name='test_ads'

def create_connection():
    conn = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_name, autocommit=True,
                       use_unicode=True, charset="utf8")
    return conn


def is_new_member(connection,member_id):
    print("i am checking if you are a new member")
    sql='''SELECT state FROM member_table 
            WHERE chat_id=%d''' %member_id
    cursor = connection.cursor()
    cursor.execute(sql)
    last_state = cursor.fetchone()
    print(last_state)
    if last_state==None:
        print('yeah you are new')
        return True
    else:
        print('nope you are not new')
        return False

def add_new_member(connection,member_id):
    print("i want to add your name into my database new commer")
    sql=''' INSERT INTO member_table
            VALUES (%d , 0)''' %member_id

    cursor = connection.cursor()
    cursor.execute(sql)
    print('your info has been recrded successfully')
    return


def update_state(member_id,next_state,connection):
    print("im in db helper,wanna store your desired action")
    cursor = connection.cursor()
    sql = 'UPDATE member_table SET state=%d WHERE chat_id=%d;' % (next_state, member_id)
    cursor.execute(sql)
    print('state is updated successfully')
    return


def fetch_state(chat_id,connection):
    print("im in db helper, wanna know your next state")
    # change the configuration as needed
    cursor = connection.cursor()
    sql = "SELECT state FROM member_table WHERE chat_id=%d" % chat_id
    cursor.execute(sql)
    last_state = cursor.fetchone()
    print('state retreived successfully')
    return last_state[0]

def insert_ad(member_id,ad_title,connection):
    print("im in db helper, create ad title, wanna store it into db")
    try:
        cursor = connection.cursor()
        if 'گزینه' in ad_title:
            pass
        sql = '''INSERT INTO ad_table (title,chat_id) VALUE ('%s','%d');''' % (ad_title, member_id)
        cursor.execute(sql)
        sql = '''SELECT max(id) FROM ad_table;'''
        cursor.execute(sql)
        id = cursor.fetchone()
        ad_id=id[0]
        print('your record has been successfully added, am in db helper, your ad id is')
        print(ad_id)
        print('in db helper i will call a method to update your state')
        update_state_new_title_added(member_id, ad_id, connection)
    except Exception as e:
        print("Exeception occured:{}".format(e))


def update_state_new_title_added(chat_id,ad_id,connection):
    print('i am in db helper, wanna update your state to your ad id for ease of process')
    cursor = connection.cursor()
    print('yoour chat id is')
    print(chat_id)
    print('your ad id in update state new title added is')
    print(ad_id)
    sql = 'UPDATE member_table SET state=%d WHERE chat_id=%d;' % (ad_id, chat_id)
    cursor.execute(sql)
    return


def list_null_fields(ad_id,connection):
    null_fields=[]
    print('i am in db helper, fetching your empty fields')
    cursor = connection.cursor()
    sql='''SELECT * FROM ad_table WHERE id=%d'''%ad_id
    cursor.execute(sql)
    fields=cursor.fetchone()
    if fields[2] is None:
        null_fields.append('price')
    if fields[3] is None:
        null_fields.append('mileage')
    if fields[4] is None:
        null_fields.append('transmission')
    if fields[5] is None:
        null_fields.append('release_year')
    if fields[6] is None:
        null_fields.append('model')
    if fields[7] is None:
        null_fields.append('brand')

    print(null_fields)
    return null_fields


def update_field(ad_id,field_name,field_value, connection):
    print(' i am updating your')
    print(field_name)
    print(field_value)
    cursor = connection.cursor()
    if 'price' in field_name:
        sql='''UPDATE ad_table SET price=%d WHERE id=%d''' %(field_value,ad_id)
        cursor.execute(sql)
    elif 'brand' in field_name:
        sql='''UPDATE ad_table SET brand='%s' WHERE id=%d''' %(field_value,ad_id)
        cursor.execute(sql)
    elif 'mileage' in field_name:
        sql = '''UPDATE ad_table SET mileage=%d WHERE id=%d''' % (field_value, ad_id)
        cursor.execute(sql)
    elif 'model' in field_name:
        sql='''UPDATE ad_table SET model='%s' WHERE id=%d''' %(field_value,ad_id)
        cursor.execute(sql)
    elif 'release_year' in field_name:
        sql='''UPDATE ad_table SET release_year=%d WHERE id=%d''' %(field_value,ad_id)
        cursor.execute(sql)
    elif 'transmission' in field_name:
        sql = '''UPDATE ad_table SET transmission=%d WHERE id=%d''' % (field_value, ad_id)
        cursor.execute(sql)
    print('update succssful')


def get_ad_id(chat_id,connection):
    print('i am in get ad id in dbhelper')
    print(chat_id)
    cursor = connection.cursor()
    sql='''SELECT state FROM member_table WHERE chat_id=%d''' %chat_id
    cursor.execute(sql)
    ad_id=cursor.fetchone()
    print('your ad id in get ad id is')
    print(ad_id[0])
    return ad_id[0]