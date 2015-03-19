'''
Created on 2015-03-19

@author: Brydon Eastman
'''


class CustomErrorException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
