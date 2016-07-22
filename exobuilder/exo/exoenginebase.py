from exobuilder.exo.position import Position
from exobuilder.exo.transaction import Transaction
import pandas as pd
import pickle

class ExoEngineBase(object):
    def __init__(self, symbol, date, datasource):
        self._position = Position()
        self._date = date
        self._datasource = datasource
        self._series = pd.Series()
        self._extra_context = {}
        self._symbol = symbol
        self._transactions = []
        self._old_transactions = []
        self._exosuffix = '_ExoBase'

    @property
    def name(self):
        return self._symbol + self._exosuffix

    def is_rollover(self):
        pass

    def process_rollover(self):
        """
        Typically we should only close old position on rollover day
        :return:
        """
        pass

    def process_day(self):
        """
        Main EXO's position management method
        :return: list of Transactions to process
        """
        pass

    def calculate(self):
        """
        Main internal method to manage EXO data
        :return:
        """
        trans_list = []

        # Proto-code
        if self.is_rollover():
            roll_trans = self.process_rollover()
            if roll_trans is not None and len(roll_trans) > 0:
                trans_list += roll_trans

            # Process closed position PnL to change EXO price for current day
            # ???

        # Processing new day
        new_transactions = self.process_day()
        if new_transactions is not None and len(new_transactions) > 0:
            trans_list += new_transactions

        if len(trans_list) > 0:
            for t in trans_list:
                self.position.add(t)

        self._transactions += trans_list

        pnl = self.position.pnl

        self.series[self.date] = pnl

        # Save EXO state to DB
        self.save()







    def as_dict(self):
        """
        Save the EXO data to DB
        :return:
        """
        result = {}

        result['position'] = self.position.as_dict()

        result['transactions'] = self._old_transactions

        for t in self._transactions:
            result['transactions'].append(t.as_dict())

        result['name'] = self.name

        result['series'] = pickle.dumps(self.series)

        return result

    def load(self):
        exo_data = self.datasource.exostorage.load_exo(self.name)
        if exo_data is not None:
            self._position = Position.from_dict(exo_data['position'], self.datasource)
            self._old_transactions = exo_data['transactions']
            self._series = pickle.loads(exo_data['series'])
        return exo_data

    def save(self):
        """
        Save EXO data to storage
        :return:
        """
        self.datasource.exostorage.save_exo(self.as_dict())


    @property
    def position(self):
        """
        Returns current opened position of EXO engine
        If position is closed return None
        :return: None or Position()
        """
        return self._position

    @property
    def series(self):
        """
        Returns EXO price series values (before current date)
        :return:
        """
        return self._series

    @property
    def date(self):
        return self._date

    @property
    def datasource(self):
        return self._datasource