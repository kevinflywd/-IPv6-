# coding:utf-8
from utility.hash_util import hash_string_256, hash_block
from wallet import Wallet


class Verification:
    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
        guess_hash = hash_string_256(guess)
        # print(guess_hash)
        return guess_hash[0:2] == '00'


    @classmethod
    def verify_chain(cls, blockchain):
        """ Verify the current blockchain and return True if it's valid"""
        for index, block in enumerate(blockchain):
            if index == 0:
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):
                return False
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('Proof of work is invalid')
                return False
        return True


    @staticmethod
    def verify_transaction(transaction):
        return Wallet.verify_transaction(transaction)

    @classmethod
    def verify_transactions(cls, open_transactions):
        return all([cls.verify_transaction(tx) for tx in open_transactions])
