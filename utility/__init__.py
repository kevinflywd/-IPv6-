# coding:utf-8
from utility.hash_util import hash_string_256

"""
__all__在别的包中可用于模块导入时限制，此时被导入模块若定义了__all__属性，则只有__all__内指定的属性、方法、类可被导入。
比如这时候在从别的.py文件导入时，只能用'hash_string_256', 并不能用json、hl、'hash_block'，
"""
__all__ = ['hash_string_256']