# coding:utf-8
from pymysql import connect
import json

def main():
    conn = connect(host='localhost', port=3306,  user='root', password='1994', charset='utf8')
    node_id = 5001
    cursor = conn.cursor()
    database = 'blockchain_{}'.format(node_id)
    sql = 'create database if not exists '+database+' character Set utf8'
    cursor.execute(sql)
    cursor.execute('use blockchain_5001')

    sqlblock = 'create table if not exists blockchain(height int unsigned primary key not null, previous_hash varchar(64),time_stamp varchar(30),proof int unsigned)'
    cursor.execute(sqlblock)
    cursor.execute('truncate table blockchain')

    cursor.execute('create table if not exists transactions(sender VARCHAR(512),'
                   'recipient VARCHAR(512),'
                   'amount DOUBLE(10,2),'
                   'signature VARCHAR(256),'
                   'provenance_code VARCHAR(128),'
                   'drug_name VARCHAR(128),'
                   'classes VARCHAR(8),'
                   'information TEXT,'
                   'block_height INT UNSIGNED)')

    cursor.execute('truncate table transactions')


    saveable_chain =[{"index": 0, "previous_hash": "", "timestamp": 0, "transactions": [], "proof": 100}, {"index": 1, "previous_hash": "c775ae7455f086e2fc68520d31bfebfdb18ffeaceb933085c510d5f8d2177813", "timestamp": "2020-12-07 15:48:16", "transactions": [{"sender": "MINING", "recipient": "30819f300d06092a864886f70d010101050003818d0030818902818100da06423f3ee2df9e5b81f99752c5edb5bcde5ee784091d0f4334d136eda921074be8a16f5ad04e9e2fd67306dcc4e9d7bfa780dde4e2d9c97b8f92bfbf612f07b0e557d127ca984f0b1bf2472657a4c8bc3af6e18299d0b196acb1e3ba12b2fa2cd84bc73629ca14da4f295b8617a28a17d6ecf8a94983812ca3744ecd021a5d0203010001", "amount": 10, "provenance_code": "", "signature": "", "drug_name": "", "classes": "", "information": ""}], "proof": 92}, {"index": 2, "previous_hash": "00299a1efd7e624249a6a618df342350444dde8848085ed4d0377e2511e51b30", "timestamp": "2020-12-07 15:48:16", "transactions": [{"sender": "30819f300d06092a864886f70d010101050003818d0030818902818100da06423f3ee2df9e5b81f99752c5edb5bcde5ee784091d0f4334d136eda921074be8a16f5ad04e9e2fd67306dcc4e9d7bfa780dde4e2d9c97b8f92bfbf612f07b0e557d127ca984f0b1bf2472657a4c8bc3af6e18299d0b196acb1e3ba12b2fa2cd84bc73629ca14da4f295b8617a28a17d6ecf8a94983812ca3744ecd021a5d0203010001", "recipient": "30819f300d06092a864886f70d010101050003818d0030818902818100996bcaca188eaee932ed47548430d2ec607283609553ea0b0094a29d86947efc4f3a0c42bb916a5f084d9d2fa8be30ff3f46ca6611270cdccfd461e32cbffb0bf31e6e84f73cfbbe4c6249a4f3bc5cb38fbed41181835496967d4a40ac6a5e128d6359c86280a9063146bd22a727d98e1913928320c2a0cb6700657af62c507f0203010001", "amount": 5, "provenance_code": "1001", "signature": "166d33714cb91f1c28069b1435af021249bcb60d450ebee044c9093acf1c7bdb8021c6a5f7d59d34ad6886923bcdf4ddc723932bce1c4bbf058bed1725a43f2b19e3bcdb8fb86678d35518083c6ac2c0b4e6e6ba7245d8336d82f35e5d286f4eaaa1e875f7a528b793bc654a590e725daaf77ef828f91799204ba91c02744e49", "drug_name": "999\u611f\u5192\u96f6", "classes": "pb", "information": {"\u751f\u4ea7\u65e5\u671f": "2020.11.05", "\u6279\u6b21": "12138", "\u8fd0\u8f93\u516c\u53f8": "\u987a\u4e30"}}, {"sender": "MINING", "recipient": "30819f300d06092a864886f70d010101050003818d0030818902818100da06423f3ee2df9e5b81f99752c5edb5bcde5ee784091d0f4334d136eda921074be8a16f5ad04e9e2fd67306dcc4e9d7bfa780dde4e2d9c97b8f92bfbf612f07b0e557d127ca984f0b1bf2472657a4c8bc3af6e18299d0b196acb1e3ba12b2fa2cd84bc73629ca14da4f295b8617a28a17d6ecf8a94983812ca3744ecd021a5d0203010001", "amount": 10, "provenance_code": "", "signature": "", "drug_name": "", "classes": "", "information": ""}], "proof": 707}, {"index": 3, "previous_hash": "8ebfbd90c40b3c893ea777358f6678935058291d12855a47d41f66419ba5c3f3", "timestamp": "2020-12-07 15:48:15", "transactions": [{"sender": "30819f300d06092a864886f70d010101050003818d0030818902818100996bcaca188eaee932ed47548430d2ec607283609553ea0b0094a29d86947efc4f3a0c42bb916a5f084d9d2fa8be30ff3f46ca6611270cdccfd461e32cbffb0bf31e6e84f73cfbbe4c6249a4f3bc5cb38fbed41181835496967d4a40ac6a5e128d6359c86280a9063146bd22a727d98e1913928320c2a0cb6700657af62c507f0203010001", "recipient": "30819f300d06092a864886f70d010101050003818d00308189028181009ea88c2baa73604195475fd0116529f0c244cf95e5a779a3df58fca2c3583ca487fed55fd9b1694ae3cd0bfbb236614e7515b01e5ac82ffa189d61e862bdd5b1435ea78501cc39b85f5bab502f13f0721548201d3c5eb93398aebaf55b7a6b05ff6abe1245471b48e96cc86acaf85eef564f18e2ac9a5ea61fb4eaaf638cac330203010001", "amount": 1, "provenance_code": "1001", "signature": "5ea28ba03251b5a7de8bd13774b1b071d965fcfb8dc730d1f89f478cede3004ebbc04c07a8abb297b7fcc0d25b7bdca9aae252b86bb34d8e2632290160f2318667530b92eb60a94d37595d3b82c15498614921f8a38a2fa5ae82f3e5045e31d39388b5d661343f34d0168df7a1392fb6500a7e2220bb4fa0b9c204b947a86081", "drug_name": "999\u611f\u5192\u96f6", "classes": "pb", "information": {"\u751f\u4ea7\u65e5\u671f": "2020.11.00", "\u6279\u6b21": "10013", "\u5b58\u50a8\u73af\u5883": "\u51b7\u85cf-5\u00b0C", "\u9500\u552e\u5355\u4f4d": "\u76db\u548c\u82d1\u793e\u533a", "\u9001\u8fbe\u65f6\u95f4": "2020.12.31"}}, {"sender": "MINING", "recipient": "30819f300d06092a864886f70d010101050003818d0030818902818100996bcaca188eaee932ed47548430d2ec607283609553ea0b0094a29d86947efc4f3a0c42bb916a5f084d9d2fa8be30ff3f46ca6611270cdccfd461e32cbffb0bf31e6e84f73cfbbe4c6249a4f3bc5cb38fbed41181835496967d4a40ac6a5e128d6359c86280a9063146bd22a727d98e1913928320c2a0cb6700657af62c507f0203010001", "amount": 10, "provenance_code": "", "signature": "", "drug_name": "", "classes": "", "information": ""}], "proof": 146}]
    for i in range(len(saveable_chain)):
        cursor.execute('insert into blockchain values(%s,%s,%s,%s)', (saveable_chain[i]['index'],saveable_chain[i]['previous_hash'], saveable_chain[i]['timestamp'], saveable_chain[i]['proof']))
        # 这是个列表，列表元素是字典
        transactions = saveable_chain[i]['transactions']
        if not transactions:
            continue
        else:
            for j in range(len(transactions)):
                params = (transactions[j]['sender'],transactions[j]['recipient'],transactions[j]['amount'],transactions[j]['signature'],
                          transactions[j]['provenance_code'],transactions[j]['drug_name'],transactions[j]['classes'],
                          json.dumps((transactions[j]['information'])),saveable_chain[i]['index'])
                cursor.execute('insert into transactions values(%s,%s,%s,%s,%s,%s,%s,%s,%s)', params)
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
