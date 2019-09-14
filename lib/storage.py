'''
    `storage.py`
    @author 810Teams
'''

from datetime import datetime
from lib.utils import error, notice
import os
import pandas

class Storage:
    def __init__(self, name):
        self.name = name
        self.storage = None

    def append(self, data):
        ''' User Method: Append Data '''
        time = str(datetime.now())
        self.storage = self.storage.append(pandas.DataFrame([[time[0:len(time)-7]] + data], columns=list(self.storage.columns)))
        notice('Data {} has been added to the storage.'.format(data))

    def load(self):
        ''' Indirect User Method: Load Storage '''
        try:
            self.storage = pandas.read_csv('data/' + self.name + '.csv')
        except FileNotFoundError:
            notice('Storage \'{}\' does not exist. Proceeding to storage set up.'.format(self.name))
            notice('Please input names of columns, separate values using commas.')
            Storage.setup(self, [i.strip() for i in input('(Input) ').split(',')])
    
    def reload(self):
        ''' Indirect User Method: Reload Storage '''
        try:
            self.storage = pandas.read_csv('data/' + self.name + '.csv')
            notice('Storage \'{}\' is reloaded.'.format(self.name))
        except FileNotFoundError:
            self.load()

    def save(self):
        ''' User Method: Save Storage '''
        try:
            os.remove(self.name + '.csv')
        except FileNotFoundError:
            pass
        self.storage.to_csv('data/' + self.name + '.csv', index=None, header=True)
        self.reload()
    
    def setup(self, columns):
        ''' System Method: View Storage '''
        try:
            self.storage = pandas.DataFrame([], columns=['timestamp'] + columns)
        except:
            error('Something unexpected happened. Please try again.')

    def view(self):
        ''' User Method: View Storage '''
        print(self.storage)
