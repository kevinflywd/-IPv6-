# coding:utf-8
from collections import OrderedDict
from utility.printable import Printable


class Transaction(Printable):


    def __init__(self, sender, recipient, signature,  provenance_code, drug_name, classes, information):
        self.sender = sender
        self.recipient = recipient
        self.provenance_code = provenance_code
        self.signature = signature
        self.drug_name = drug_name
        self.classes = classes
        self.information = information

    def to_ordered_dict(self):
        return OrderedDict([('sender', self.sender), ('recipient', self.recipient), ('provenance_code', self.provenance_code),
                            ('drug_name', self.drug_name), ('classes', self.classes),
                            ('information', self.information)])

