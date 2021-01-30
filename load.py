# coding:utf-8
from pymysql import *
import json

def load_database():
    try:
        database = 'blockchain_5001'
        conn = connect(host='localhost', port=3306, user='root', password='1994', database=database, charset='utf8')
        # 获得Cursor对象
        # blockchain = []
        cursor = conn.cursor(cursor=cursors.DictCursor)
        cursor.execute('select * from blockchain')
        # 列表里面套字典 把transactions多交易形成列表，加入到其中
        blockchain = cursor.fetchall()
        # blockchain['transactions'] =[]
        cursor.execute('select * from transactions')
        # 列表里面套字典
        transactions = cursor.fetchall()
        index = 0
        for i in range(0, len(blockchain)):
            length_transactions = len(transactions)

            transaction_list = []
            # 这个地方可以优化，想一想如何优化，如果取出，下次查找直接跳过,由于顺序表，如果不等于可以直接跳出循环
            while index < length_transactions:
                if blockchain[i]['height'] == transactions[index]['block_height']:
                    transaction = transactions[index].copy()
                    transaction.pop('block_height')
                    transaction['information'] = json.loads(transaction['information'])
                    print(transaction)
                    transaction_list.append(transaction)
                else:
                    break
                index += 1
            blockchain[i]['transactions'] = transaction_list

        # cursor.execute('select peernode from peernodes')
        # print(cursor.fetchall())
        print(blockchain)


        # cursor.execute('SELECT * FROM blockchain AS b LEFT JOIN transactions AS t ON b.height = t.block_height')
        # print(cursor.fetchall())
        # for i in range(count):
        #     result = cursor.fetchone()
        #     print(result)
        #     length = len(result)
        #     updated_block = []
        #     for j in range(length):
        #         updated_block.append(result[j])
        #     blockchain.append(updated_block)
        # print(blockchain)
        cursor.close()
        conn.close()
    except (IOError, IndexError):
        pass
    finally:
        print('Cleanup')


load_database()