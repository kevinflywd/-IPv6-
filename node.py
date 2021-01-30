# coding:utf-8
from flask import Flask, jsonify, request, send_from_directory, redirect, url_for, render_template, session, g
from wallet import Wallet
import json
# 当调用服务端的域名与服务端不一致(前后端分离)的时候会出现跨域问题，可使用Flask-Cors解决
from flask_cors import CORS
from blockchain import Blockchain
from pymysql import *
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = "sdfklas0lk42j"
CORS(app)

user = [1, 2, 3]
identifier1 = 0
identifier2 = 0
identifier3 = 0


@app.route('/', methods=['GET'])
def get_register_ui():
    return send_from_directory('templates', 'node.html')


@app.route('/index', methods=['GET'])
def get_index_ui():
    return send_from_directory('templates', 'index.html')


@app.route('/login', methods=['GET'])
def get_login_ui():
    return send_from_directory('templates', 'login.html')


@app.route('/loginredirect', methods=['POST'])
def get_login_redirect():
    values = request.get_json()
    print(values)
    conn = connect(host='localhost', port=3306, user='****', password='***', database='blockchain_5003',
                   charset='utf8')
    cursor = conn.cursor(cursor=cursors.DictCursor)
    cursor.execute('select * from logininformation where username=%s', values['username'])
    tup = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    session.pop('identifier', None)
    if not tup:
        response = {'msg': '用户名不存在', 'url': '0'}
        return jsonify(response), 200
    dic = tup[0]
    if dic['password'] == values['password'] and dic['identifier'] == values['identifier']:
        if values['identifier'] == '1':
            print(url_for('get_node_ui'))
            response = {'msg': '登录成功', 'url': url_for('get_node_ui')}
            session['identifier'] = values['identifier']
            return jsonify(response), 200
        if values['identifier'] == '2':
            response = {'msg': '登录成功', 'url': url_for('get_logistics_ui')}
            return jsonify(response), 200
        if values['identifier'] == '3':
            response = {'msg': '登录成功', 'url': url_for('get_retail_ui')}
            return jsonify(response), 200
    elif dic['password'] != values['password']:
        response = {'msg': '密码错误', 'url': '0'}
        return jsonify(response), 200
    elif dic['identifier'] != values['identifier']:
        response = {'msg': '身份错误', 'url': '0'}
        return jsonify(response), 200


@app.route('/producter', methods=['GET'])
def get_node_ui():
    return send_from_directory('templates', 'producter.html')


@app.route('/logistics', methods=['GET'])
def get_logistics_ui():
    return send_from_directory('templates', 'logistics.html')


@app.route('/retail', methods=['GET'])
def get_retail_ui():
    return send_from_directory('templates', 'retail.html')


@app.route('/loginout', methods=['GET'])
def logout():
    pass

@app.route('/network', methods=['GET'])
def get_network_ui():
    return send_from_directory('templates', 'network.html')


@app.route('/provenanceDrug', methods=['GET'])
def get_provenanceDrug_ui():
    return send_from_directory('templates', 'provenanceDrug.html')


@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_keys()
    if wallet.save_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,

        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Saving the keys failed.'
        }
        return jsonify(response), 500


@app.route('/wallet', methods=['GET'])
def load_keys():
    if wallet.load_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,

        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Loading the keys failed.'
        }
        return jsonify(response), 500


@app.route('/broadcast-transaction', methods=['POST'])
def broadcast_transaction():
    values = request.get_json()
    if not values:
        response = {'message': 'No data found.'}
        return jsonify(response), 400
    required = {'sender', 'recipient', 'signature', 'provenance_code', 'drug_name', 'classes', 'information'}
    if not all(key in values for key in required):
        response = {'message': 'Some data is missing.'}
        return jsonify(response), 400
    success = blockchain.add_transaction(values['recipient'], values['sender'], values['signature'],
                                         values['provenance_code'], values['drug_name'], values['classes'],
                                         values['information'],
                                         is_receiving=True)
    if success:
        response = {
            'message': 'Successfully added transaction.',
            'transaction': {
                'sender': values['sender'],
                'recipient': values['recipient'],
                'signature': values['signature'],
                'provenance_code': values['provenance_code'],
                'drug_name': values['drug_name'],
                'classes': values['classes'],
                'information': values['information']

            }
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a transaction failed.'
        }
        return jsonify(response), 500


@app.route('/broadcast-block', methods=['POST'])
def broadcast_block():
    values = request.get_json()
    if not values:
        response = {'message': 'No data found.'}
        return jsonify(response), 400
    if 'block' not in values:
        response = {'message': 'Some data is missing.'}
        return jsonify(response), 400
    block = values['block']
    if block['index'] == blockchain.chain[-1].index + 1:
        if blockchain.add_block(block):
            response = {'message': 'Block added'}
            return jsonify(response), 201
        else:
            response = {'message': 'Block seems invalid.'}
            return jsonify(response), 409
    elif block['index'] > blockchain.chain[-1].index:
        response = {'message': 'Blockchain seems to differ from local blockchain.'}
        blockchain.resolve_conflicts = True
        return jsonify(response), 200
    else:
        response = {'message': 'Blockchain seems to be shorter, block not added'}
        return jsonify(response), 409


@app.route('/transaction', methods=['POST'])
def add_transaction():
    if wallet.public_key == None:
        response = {
            'message': 'No wallet set up'
        }
        return jsonify(response), 400

    values = request.form.to_dict()
    print(values)
    if not values:
        response = {
            'message': 'No data found.'
        }
        return jsonify(response), 400
    required_fields = ['recipient', 'provenance_code', 'drug_name', 'classes', 'information']
    # 检查所有的required_fields是否都在上面的values中
    if not all(field in values for field in required_fields):
        response = {
            'message': 'Required data is missing.'
        }
        # 看看这个上面返回 response有何区别
        return jsonify(response), 400
    recipient = values['recipient']
    # amount = values['amount']
    provenance_code = values['provenance_code']
    drug_name = values['drug_name']
    classes = values['classes']

    information = values['information']
    signature = wallet.sign_transaction(wallet.public_key, recipient, provenance_code, drug_name, classes, information)
    success = blockchain.add_transaction(recipient, wallet.public_key, signature, provenance_code, drug_name, classes,
                                         information)
    if success:

        response = {
            "message": "Successfully added transaction."
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a transaction failed.'
        }
        return jsonify(response), 500


@app.route('/mine', methods=['POST'])
def mine():
    if blockchain.resolve_conflicts:
        response = {'message': 'Resolve conflicts first, block not added!'}
        return jsonify(response), 409
    block = blockchain.mine_block()
    if block != None:
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
        response = {
            'message': 'Block added successfully.',
            'block': dict_block
        }
        """
        201状态码英文名称是Created，该状态码表示已创建。成功请求并创建了新的资源，该请求已经被实现，
        而且有一个新的资源已经依据请求的需要而建立，且其 URI 已经随Location 头信息返回。假如需要的资源无法及时建立的话，
        应当返回 '202 Accepted'。
        """
        return jsonify(response), 201
    else:
        response = {
            'message': 'Adding a block failed.',
            'wallet_set_up': wallet.public_key != None,
        }
        return jsonify(response), 500


@app.route('/resolve-conflicts', methods=['POST'])
def resolve_conflicts():
    replaced = blockchain.resolve()
    if replaced:
        response = {'message': 'Chain was replaced!'}
    else:
        response = {'message': 'Local chain kept!'}
    return jsonify(response), 200


# 公开交易
@app.route('/transactions', methods=['POST', 'GET'])
def get_open_transaction():
    transactions = blockchain.get_open_transactions()
    dict_transactions = [tx.__dict__ for tx in transactions]

    print(dict_transactions)
    if request.method == 'POST':
        form_dic = request.form
        limit = int(form_dic['limit'])
        page = int(form_dic['page'])
        response = {
            "code": 0,
            "msg": "",
            "count": len(dict_transactions),
            "data": dict_transactions[(page - 1) * limit:page * limit]
        }
        return jsonify(response), 200
    else:
        return jsonify(dict_transactions), 200


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = blockchain.chain
    dict_chain = [block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dict_chain:
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
    return jsonify(dict_chain), 200


@app.route('/node', methods=['POST'])
def add_node():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data attached.'
        }
        return jsonify(response), 400
    if 'node' not in values:
        response = {
            'message': 'No data found.'
        }
        return jsonify(response), 400
    node = values['node']
    blockchain.add_peer_node(node)
    response = {
        'message': 'Node added successfully.',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 201


@app.route('/node/<node_url>', methods=['DELETE'])
def remove_node(node_url):
    if node_url == '' or node_url == None:
        response = {
            'message': 'No node found.'
        }
        return jsonify(response), 400
    blockchain.remove_peer_node(node_url)
    response = {
        'message': 'Node removed',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 200


@app.route('/provenance', methods=['POST'])
def get_provenance_transactions():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data attached.'
        }
        return jsonify(response), 400
    if 'provenance_code' not in values:
        response = {
            'message': 'No data found.'
        }
        return jsonify(response), 400
    provenance_code = values['provenance_code']
    provenance_transactions = blockchain.get_provenance(provenance_code)
    if not provenance_transactions:
        response = {
            'message': 'No provenance_transactions about provenance_code'
        }
        return jsonify(response), 400
    else:
        response = {
            'message': 'The query is successful!',
            'provenance_transactions': provenance_transactions
        }
        return jsonify(response), 200


@app.route('/nodes', methods=['GET', 'POST'])
def get_nodes():
    response = {
        "code": 0,
        "msg": ""
    }
    form_dict = request.form.to_dict()
    print(form_dict)
    page = int(form_dict['page'])
    limit = int(form_dict['limit'])
    database = 'blockchain_{}'.format(port)
    response['data'] = cursor.fetchall()
    response['count'] = cursor.fetchall()[0]['count(*)']
    return jsonify(response), 200


@app.route('/alltransactions', methods=['GET'])
def get_alltransactions():
    response = {"code": 0, "msg": ""}
    database = 'blockchain_{}'.format(port)
    conn = connect(host='localhost', port=3306, user='*', password='*', database=database,
                   charset='utf8')
    cursor = conn.cursor(cursor=cursors.DictCursor)
    cursor.execute("select count(*) from transactions")
    response['count'] = cursor.fetchall()[0]['count(*)']
    cursor.execute("select * from transactions")
    list_transactions = cursor.fetchall()
    for i in list_transactions:
        i['information'] = json.loads(i['information'])

    response['data'] = list_transactions
    return jsonify(response), 200


@app.route('/druginformation', methods=['GET', 'POST'])
def get_druginformation():
    form_dict = request.form
    limit = int(form_dict['limit'])
    page = int(form_dict['page'])
    database = 'blockchain_{}'.format(port)
    conn = connect(host='localhost', port=3306, user='root', password='1994', database=database, charset='utf8')
    cursor = conn.cursor(cursor=cursors.DictCursor)
    response = {"code": 0, "msg": ""}
    cursor.execute("select count(*) from druginformation where status!=1")
    response['count'] = cursor.fetchall()[0]['count(*)']
    cursor.execute('select * from druginformation where status!=1 limit %s,%s', ((page - 1) * limit, limit))
    response["data"] = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify(response)


@app.route('/druginformationsearch', methods=['GET', 'POST'])
def get_druginformationsearch():
    database = 'blockchain_{}'.format(port)
    conn = connect(host='localhost', port=3306, user='**', password='**', database=database,
                   charset='utf8')
    cursor = conn.cursor(cursor=cursors.DictCursor)
    response = {"code": 0, "msg": ""}
    form_dict = request.form.to_dict()
    print(form_dict)
    page = int(form_dict['page'])
    limit = int(form_dict['limit'])
    if 'provenance_code' in form_dict:
        provenance_code = form_dict['provenance_code']
        cursor.execute("select count(*) from druginformation where provenance_code = %s ", provenance_code)
        response['count'] = cursor.fetchall()[0]['count(*)']
        cursor.execute('select * from druginformation where provenance_code=%s limit %s,%s',
                       (provenance_code, (page - 1) * limit, limit))
        response["data"] = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify(response)
    return jsonify(response)


# 在生产商完成添加药品信息 ----生产
@app.route('/adddruginformationproducer', methods=['POST'])
def add_druginformation_producer():
    form_dic = request.form.to_dict()
    print(form_dic)
    conn = connect(host='localhost', port=3306, user='root', password='1994', database='blockchain_5000',
                   charset='utf8')
    cursor = conn.cursor(cursor=cursors.DictCursor)
    cursor.execute("insert into druginformation values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",
                   (form_dic['provenance_code'],
                    form_dic['drug_name'],
                    form_dic['classes'],
                    form_dic['dosage'],
                    form_dic['producer'],
                    form_dic['batch'],
                    form_dic['quality_inspector'],
                    form_dic['date_in_produced'],
                    form_dic['expiration_date'],
                    0))
    conn.commit()
    cursor.close()
    conn.close()
    response = {
        'message': "success add drug information"
    }
    return jsonify(response), 200


@app.route('/adddruginformationlogistics', methods=['POST'])
def add_druginformation_logistics():
    form_dic = request.form.to_dict()
    print(form_dic)
    conn = connect(host='localhost', port=3306, user='**', password='*', database='blockchain_5001',
                   charset='utf8')
    cursor = conn.cursor(cursor=cursors.DictCursor)
    cursor.execute("insert into druginformation values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",
                   (form_dic['provenance_code'],
                    form_dic['drug_name'],
                    form_dic['classes'],
                    form_dic['logistics_company'],
                    form_dic['carrier'],
                    form_dic['vehicle_type'],
                    form_dic['license'],
                    form_dic['starting_place'],
                    form_dic['storage_environment'],
                    form_dic['starting_time'], 0))
    conn.commit()
    cursor.close()
    conn.close()
    response = {
        'message': "success add drug information"
    }
    return jsonify(response), 200


@app.route('/adddruginformationretail', methods=['POST'])
def add_druginformation_retail():
    form_dic = request.form.to_dict()
    print(form_dic)
    conn = connect(host='localhost', port=3306, user='***', password='**', database='blockchain_5002',
                   charset='utf8')
    cursor = conn.cursor(cursor=cursors.DictCursor)
    cursor.execute("insert into druginformation values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",
                   (form_dic['provenance_code'],
                    form_dic['drug_name'],
                    form_dic['classes'],
                    form_dic['retail_store'],
                    form_dic['address'],
                    form_dic['seller'],
                    form_dic['consumer'],
                    form_dic['storage_environment'],
                    form_dic['date_of_purchase'],
                    form_dic['date_of_sale'], 0))
    conn.commit()
    cursor.close()
    conn.close()
    response = {
        'message': "success add drug information"
    }
    return jsonify(response), 200


@app.route('/modifydruginformationproducer', methods=['POST'])
def modify_druginformation_producer():
    form_dic = request.form.to_dict()
    print(form_dic)
    conn = connect(host='localhost', port=3306, user='****', password='***', database='blockchain_5000',
                   charset='utf8')
    cursor = conn.cursor(cursor=cursors.DictCursor)
    cursor.execute(
        'update druginformation set provenance_code=%s,drug_name=%s,classes=%s,dosage=%s,producer=%s,batch=%s,quality_inspector=%s,date_in_produced=%s,expiration_date=%s,status=%s where provenance_code=%s',
        (form_dic['provenance_code'],
         form_dic['drug_name'],
         form_dic['classes'],
         form_dic['dosage'],
         form_dic['producer'],
         form_dic['batch'],
         form_dic['quality_inspector'],
         form_dic['date_in_produced'],
         form_dic['expiration_date'],
         0,
         form_dic['provenance_code']))
    conn.commit()
    cursor.close()
    conn.close()
    response = {
        'message': "success modify drug information"
    }
    return jsonify(response), 200


@app.route('/modifydruginformationlogistics', methods=['POST'])
def modify_druginformation_logistics():
    form_dic = request.form.to_dict()
    print(form_dic)
    conn = connect(host='localhost', port=3306, user='root', password='1994', database='blockchain_5001',
                   charset='utf8')
    cursor = conn.cursor(cursor=cursors.DictCursor)
    cursor.execute(
        'update druginformation set provenance_code=%s,drug_name=%s,classes=%s,logistics_company=%s,carrier=%s,vehicle_type=%s,license=%s,starting_place=%s,storage_environment=%s,starting_time=%s,status=%s where provenance_code=%s',
        (form_dic['provenance_code'],
         form_dic['drug_name'],
         form_dic['classes'],
         form_dic['logistics_company'],
         form_dic['carrier'],
         form_dic['vehicle_type'],
         form_dic['license'],
         form_dic['starting_place'],
         form_dic['storage_environment'],
         form_dic['starting_time'],
         0,
         form_dic['provenance_code']))
    conn.commit()
    cursor.close()
    conn.close()
    response = {
        'message': "success modify drug information"
    }
    return jsonify(response), 200


@app.route('/modifydruginformationretail', methods=['POST'])
def modify_druginformation_retail():
    form_dic = request.form.to_dict()
    print(form_dic)
    conn = connect(host='localhost', port=3306, user='****', password='***', database='blockchain_5002',
                   charset='utf8')
    cursor = conn.cursor(cursor=cursors.DictCursor)
    cursor.execute(
        'update druginformation set provenance_code=%s,drug_name=%s,classes=%s,retail_store=%s,address=%s,seller=%s,consumer=%s,storage_environment=%s,date_of_purchase=%s,date_of_sale=%s,status=%s where provenance_code=%s',
        (form_dic['provenance_code'],
         form_dic['drug_name'],
         form_dic['classes'],
         form_dic['retail_store'],
         form_dic['address'],
         form_dic['seller'],
         form_dic['consumer'],
         form_dic['storage_environment'],
         form_dic['date_of_purchase'],
         form_dic['date_of_sale'],
         0,
         form_dic['provenance_code']))
    conn.commit()
    cursor.close()
    conn.close()
    response = {
        'message': "success modify drug information"
    }
    return jsonify(response), 200


@app.route('/modifystatus', methods=['POST'])
def modify_status():
    form_dic = request.form.to_dict()
    # print(form_dic)
    database = 'blockchain_{}'.format(port)
    conn = connect(host='localhost', port=3306, user='***', password='***', database=database,
                   charset='utf8')
    cursor = conn.cursor(cursor=cursors.DictCursor)
    cursor.execute('update druginformation set status=%s where provenance_code=%s',
                   (form_dic['status'], form_dic['provenance_code']))
    conn.commit()
    cursor.close()
    conn.close()
    response = {
        'message': "success save drug information"
    }
    return jsonify(response), 200


@app.route('/deletedruginformation', methods=['POST'])
def delete_druginformation():
    form_dic = request.form.to_dict()
    # print(form_dic)
    database = 'blockchain_{}'.format(port)
    conn = connect(host='localhost', port=3306, user='****', password='***', database=database,
                   charset='utf8')
    cursor = conn.cursor(cursor=cursors.DictCursor)
    cursor.execute('delete from druginformation where provenance_code=%s', form_dic['provenance_code'])
    conn.commit()
    cursor.close()
    conn.close()
    response = {
        'message': "success delete drug information"
    }
    return jsonify(response), 200


@app.route('/linetable', methods=['GET'])
def draw_linetable():
    xdata = []
    ydata = []
    today = datetime.date.today()
    for i in range(7, 0, -1):
        oneday = datetime.timedelta(days=i)
        oldday = str(today - oneday)
        xdata.append(oldday)
    database = 'blockchain_{}'.format(port)
    conn = connect(host='localhost', port=3306, user='root', password='1994', database=database,
                   charset='utf8')
    cursor = conn.cursor(cursor=cursors.DictCursor)
    for i in xdata:
        cursor.execute(
            'SELECT count(*) FROM  blockchain JOIN transactions ON transactions.`block_height` = blockchain.height  WHERE time_stamp LIKE %s',
            i + '%')
        ydata.append(cursor.fetchall()[0]['count(*)'])
    conn.commit()
    cursor.close()
    conn.close()
    response = {
        'xdata': xdata,
        'ydata': ydata
    }
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000)
    args = parser.parse_args()
    port = args.port
    wallet = Wallet(port)
    blockchain = Blockchain(wallet.public_key, port)
    app.run(host='0.0.0.0', port=port)
