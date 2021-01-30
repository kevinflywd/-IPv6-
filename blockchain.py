# coding:utf-8
from functools import reduce
# import hashlib as hl
# from collections import OrderedDict
import json
import requests
from utility.hash_util import hash_block
from utility.verification import Verification
from block import Block
from transaction import Transaction
from wallet import Wallet
from pymysql import *

MINING_REWARD = 10  # python导入包的时候会先在内存执行一遍，所以在另一个文件中导入可以在下面类中用到
print(__name__)


class Blockchain:

    def __init__(self, public_key, node_id):
        # Our starting block for the blockchain
        genesis_block = Block(0, '', [], 100, 0)

        self.chain = [genesis_block]
        # 未处理的交易
        self.__open_transactions = []

        self.public_key = public_key

        self.__peer_nodes = set()
        self.node_id = node_id
        self.resolve_conflicts = False

        self.load_database()
        # 新创建的节点读取数据后会覆盖genesis_block
        if not self.chain:
            self.chain = [genesis_block]

    @property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, val):
        self.__chain = val

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def create_database(self):
        conn = connect(host='localhost', port=3306, user='root', password='1994', charset='utf8')
        # 获得Cursor对象

        cursor = conn.cursor()
        # 创建数据库
        database = 'blockchain_{}'.format(self.node_id)
        create_database = 'create database  if not exists ' + database + ' Character Set UTF8'
        cursor.execute(create_database)
        use_database = 'use ' + database
        cursor.execute(use_database)
        # 创建blockchain表
        sqlblock = 'create table if not exists blockchain(height int unsigned primary key not null, previous_hash varchar(64),time_stamp varchar(30),proof int unsigned)'
        cursor.execute(sqlblock)
        # 创建transactions表
        cursor.execute('create table if not exists transactions(sender VARCHAR(512),'
                       'recipient VARCHAR(512),'
                       'signature VARCHAR(256),'
                       'provenance_code VARCHAR(128),'
                       'drug_name VARCHAR(128),'
                       'classes VARCHAR(8),'
                       'information TEXT,'
                       'block_height INT UNSIGNED)')
        # 创建peernodes表
        sqlpeernodes = 'CREATE TABLE IF NOT EXISTS peernodes(id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,' \
                       'peernode VARCHAR(30))'
        cursor.execute(sqlpeernodes)
        # 创建opentransactions表
        cursor.execute('create table if not exists opentransactions(sender VARCHAR(512),'
                       'recipient VARCHAR(512),'
                       'signature VARCHAR(256),'
                       'provenance_code VARCHAR(128),'
                       'drug_name VARCHAR(128),'
                       'classes VARCHAR(8),'
                       'information TEXT)')
        conn.commit()
        cursor.close()
        conn.close()

    def load_data(self):

        try:
            with open('blockchain-{}.txt'.format(self.node_id), mode='r') as f:
                file_content = f.readlines()

                blockchain = json.loads(file_content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount'],
                                                tx['provenance_code'], tx['drug_name'], tx['classes'],
                                                tx['information'])
                                    for tx in block['transactions']]
                    updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'],
                                          block['timestamp'])

                    updated_blockchain.append(updated_block)

                self.chain = updated_blockchain

                open_transactions = json.loads(file_content[1][:-1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount'],
                                                      tx['provenance_code'], tx['drug_name'], tx['classes'],
                                                      tx['information'])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions
                peer_nodes = json.loads(file_content[2])
                self.__peer_nodes = set(peer_nodes)
        except (IOError, IndexError):
            pass
        finally:
            print('Cleanup')

    def load_database(self):
        try:
            database = 'blockchain_{}'.format(self.node_id)
            conn = connect(host='localhost', port=3306, user='root', password='1994', database=database, charset='utf8')
            cursor = conn.cursor(cursor=cursors.DictCursor)
            cursor.execute('select * from blockchain')
            blockchain = cursor.fetchall()
            cursor.execute('select * from transactions')
            transactions = cursor.fetchall()
            index = 0
            for i in range(0, len(blockchain)):
                length_transactions = len(transactions)
                transaction_list = []
                while index < length_transactions:
                    if blockchain[i]['height'] == transactions[index]['block_height']:
                        transaction = transactions[index].copy()
                        transaction.pop('block_height')
                        transaction['information'] = json.loads(transaction['information'])
                        transaction_list.append(transaction)
                    else:
                        break
                    index += 1
                blockchain[i]['transactions'] = transaction_list
            updated_blockchain = []
            for block in blockchain:
                converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['signature'],
                                            tx['provenance_code'], tx['drug_name'], tx['classes'],
                                            (tx['information']))
                                for tx in block['transactions']]
                updated_block = Block(block['height'], block['previous_hash'], converted_tx, block['proof'],
                                      block['time_stamp'])
                updated_blockchain.append(updated_block)
            self.chain = updated_blockchain
            cursor.execute('select * from opentransactions')
            open_transactions = cursor.fetchall()
            updated_transactions = []
            for tx in open_transactions:
                tx['information'] = json.loads(tx['information'])
                updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['signature'],
                                                  tx['provenance_code'], tx['drug_name'], tx['classes'],
                                                  tx['information'])
                updated_transactions.append(updated_transaction)
            self.__open_transactions = updated_transactions

            cursor.execute('select peernode from peernodes')
            peer_nodes = cursor.fetchall()
            peer_nodes_set = set()
            for node in peer_nodes:
                peer_nodes_set.add(node['peernode'])
            self.__peer_nodes = peer_nodes_set
            cursor.close()
            conn.close()
        except (IOError, IndexError):
            pass
        finally:
            print('Cleanup')

    def save_data(self):
        try:

            with open('blockchain-{}.txt'.format(self.node_id), mode='w') as f:
                saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash,
                                                                     [tx.__dict__ for tx in block_el.transactions],
                                                                     block_el.proof, block_el.timestamp) for block_el in
                                                               self.__chain]]
                f.write(json.dumps(saveable_chain))
                f.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_tx))
                f.write('\n')
                f.write(json.dumps(list(self.__peer_nodes)))

        except IOError:
            print('Saving failed!')

    def save_blockchain(self):
        try:
            database = 'blockchain_{}'.format(self.node_id)
            conn = connect(host='localhost', port=3306, user='root', password='1994', database=database, charset='utf8')
            cursor = conn.cursor()
            cursor.execute('truncate table blockchain')
            cursor.execute('truncate table transactions')
            # 这是个列表，列表里面存的字典
            saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash,
                                                                 [tx.__dict__ for tx in block_el.transactions],
                                                                 block_el.proof, block_el.timestamp) for block_el in
                                                           self.__chain]]
            for i in range(len(saveable_chain)):
                cursor.execute('insert into blockchain values(%s,%s,%s,%s)', (
                    saveable_chain[i]['index'], saveable_chain[i]['previous_hash'], saveable_chain[i]['timestamp'],
                    saveable_chain[i]['proof']))
                # 这是个列表，列表元素是字典
                transactions = saveable_chain[i]['transactions']
                if not transactions:
                    continue
                else:
                    for j in range(len(transactions)):
                        params = (transactions[j]['sender'], transactions[j]['recipient'],
                                  transactions[j]['signature'],
                                  transactions[j]['provenance_code'], transactions[j]['drug_name'],
                                  transactions[j]['classes'],
                                  json.dumps(transactions[j]['information']), saveable_chain[i]['index'])
                        cursor.execute('insert into transactions values(%s,%s,%s,%s,%s,%s,%s,%s)', params)
            conn.commit()
            cursor.close()
            conn.close()
        except IOError:
            print('Saving blockchain failed!')

    def save_open_transactions(self):
        try:
            database = 'blockchain_{}'.format(self.node_id)
            conn = connect(host='localhost', port=3306, user='root', password='1994', database=database, charset='utf8')
            # 获得Cursor对象
            cursor = conn.cursor()
            # 初始化
            cursor.execute('truncate table opentransactions')
            saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
            if not saveable_tx:
                conn.commit()
            else:
                for i in range(len(saveable_tx)):
                    params = (saveable_tx[i]['sender'], saveable_tx[i]['recipient'],
                              saveable_tx[i]['signature'],
                              saveable_tx[i]['provenance_code'], saveable_tx[i]['drug_name'],
                              saveable_tx[i]['classes'],
                              json.dumps(saveable_tx[i]['information']))
                    cursor.execute('insert into opentransactions values(%s,%s,%s,%s,%s,%s,%s)', params)
                conn.commit()
                cursor.close()
                conn.close()
        except IOError:
            print('Saving opentransactions failed!')

    def save_peer_nodes(self):
        try:
            database = 'blockchain_{}'.format(self.node_id)
            conn = connect(host='localhost', port=3306, user='root', password='1994', database=database, charset='utf8')
            # 获得Cursor对象
            cursor = conn.cursor()

            cursor.execute('truncate table peernodes')
            saveable_nodes = list(self.__peer_nodes)
            for i in range(len(saveable_nodes)):
                cursor.execute('insert into peernodes values(null,%s)', saveable_nodes[i])
            conn.commit()
            cursor.close()
            conn.close()

        except IOError:
            print('Saving peernodes failed!')

    def proof_of_work(self):
        last_block = self.__chain[-1]
        # hash_block把区块转换成previous_hash
        last_hash = hash_block(last_block)
        proof = 0
        # Try different PoW numbers and return the first valid one
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_last_blockchain_value(self):
        """返回当前区块链最后一个区块值"""
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    def add_transaction(self, recipient, sender, signature, provenance_code='', drug_name='', classes='',
                        information='', is_receiving=False):

        transaction = Transaction(sender, recipient, signature, provenance_code, drug_name, classes,
                                  information)

        if Verification.verify_transaction(transaction):
            self.__open_transactions.append(transaction)
            self.save_open_transactions()
            self.save_blockchain()
            if not is_receiving:
                for node in self.__peer_nodes:
                    url = 'http://{}/broadcast-transaction'.format(node)

                    try:
                        response = requests.post(url, json={'sender': sender, 'recipient': recipient,
                                                            'signature': signature,
                                                            'provenance_code': provenance_code, 'drug_name': drug_name,
                                                            'classes': classes,
                                                            'information': information})
                        if response.status_code == 400 or response.status_code == 500:
                            print('Transaction declined, needs resolving ')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        return False

    def mine_block(self):
        if self.public_key == None:
            return None
        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()

        copied_transactions = self.__open_transactions[:]

        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return None

        block = Block(len(self.__chain), hashed_block, copied_transactions, proof)  # 不用上传时间戳。有默认值
        # 返回刚挖上的这个区块（是个对象）
        self.__chain.append(block)
        """交易执行后，上链之后，把交易列表置空，避免交易重复上链"""
        self.__open_transactions = []
        # self.save_data()
        self.save_blockchain()
        self.save_open_transactions()
        for node in self.__peer_nodes:
            url = 'http://{}/broadcast-block'.format(node)
            converted_block = block.__dict__.copy()
            converted_block['transactions'] = [tx.__dict__ for tx in converted_block['transactions']]
            try:
                response = requests.post(url, json={'block': converted_block})
                if response.status_code == 400 or response.status_code == 500:
                    print('Block declined, needs resolving ')

                if response.status_code == 409:
                    self.resolve_conflicts = True
            except requests.exceptions.ConnectionError:
                continue
        return block

    def add_block(self, block):
        transactions = [Transaction(tx['sender'], tx['recipient'], tx['signature'],
                                    tx['provenance_code'], tx['drug_name'], tx['classes'], tx['information'])
                        for tx in block['transactions']]
        proof_is_value = Verification.valid_proof(transactions, block['previous_hash'], block['proof'])
        hashed_match = hash_block(self.chain[-1]) == block['previous_hash']
        if not proof_is_value or not hashed_match:
            return False
        # 把字典类型转化成Block类
        converted_block = Block(block['index'], block['previous_hash'], transactions, block['proof'],
                                block['timestamp'])
        self.__chain.append(converted_block)
        stored_transactions = self.__open_transactions[:]

        for itx in block['transactions']:
            for opentx in stored_transactions:
                if opentx.sender == itx['sender'] and opentx.recipient == itx['recipient'] and \
                        opentx.signature == itx['signature'] \
                        and opentx.provenance_code == itx['provenance_code'] and opentx.drug_name == itx[
                    'drug_name'] and opentx.classes == itx['classes'] \
                        and opentx.information == itx['information']:
                    try:
                        self.__open_transactions.remove(opentx)
                    except ValueError:
                        print('Item was already removed')
        self.save_blockchain()
        self.save_open_transactions()
        return True

    def resolve(self):
        winner_chain = self.chain
        replace = False
        for node in self.__peer_nodes:
            url = 'http://{}/chain'.format(node)
            try:
                response = requests.get(url)
                node_chain = response.json()
                node_chain = [Block(block['index'], block['previous_hash'], [Transaction(
                    tx['sender'], tx['recipient'], tx['signature'], tx['provenance_code'],
                    tx['drug_name'], tx['classes'], tx['information'])
                    for tx in block['transactions']], block['proof'], block['timestamp']) for block in node_chain]
                node_chain_length = len(node_chain)
                local_chain_length = len(winner_chain)
                if node_chain_length > local_chain_length and Verification.verify_chain(node_chain):
                    winner_chain = node_chain
                    replace = True
            except requests.exceptions.ConnectionError:
                continue
        self.resolve_conflicts = False
        self.chain = winner_chain
        # replace 把不合法的交易置空
        if replace:
            self.__open_transactions = []
        # self.save_data()
        self.save_blockchain()
        self.save_open_transactions()
        return replace

    def add_peer_node(self, node):

        self.__peer_nodes.add(node)
        # self.save_data()
        self.save_peer_nodes()

    def remove_peer_node(self, node):

        self.__peer_nodes.discard(node)

        self.save_peer_nodes()

    def get_peer_nodes(self):

        return list(self.__peer_nodes)
