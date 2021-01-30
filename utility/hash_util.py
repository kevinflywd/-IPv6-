# coding:utf-8
import hashlib as hl
import json


def hash_string_256(string):
    return hl.sha256(string).hexdigest()


# 目前是把整个区块都hash了，看看以后会不会改进成hash区块头
def hash_block(block):
    hashable_block = block.__dict__.copy()  # .copy 是防止block.__dict__被篡改。（添加属性即可做到）
    hashable_block['transactions'] = [tx.to_ordered_dict() for tx in hashable_block['transactions']]
    return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())
