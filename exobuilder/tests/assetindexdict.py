from exobuilder.data.assetindex import AssetIndexBase
import pickle
import gzip


class AssetIndexDicts(AssetIndexBase):
    def __init__(self):
        self.instr_name = 'EP'

        with gzip.GzipFile(self.instr_name + '_instrument.pgz', 'r') as f:
            self.instrument_dict = pickle.load(f)

        with gzip.GzipFile(self.instr_name + '_futures.pgz', 'r') as f:
            self.futures_dict = pickle.load(f)

        with gzip.GzipFile(self.instr_name + '_options.pgz', 'r') as f:
            self.options_dict = pickle.load(f)

    def get_instrument_info(self, symbol):
        if symbol != self.instr_name:
            raise NotImplementedError("This is a test class works only with 'ES' instrument")

        return self.instrument_dict

    def get_futures_list(self, date, instrument, limit):
        if instrument.name != self.instr_name:
            raise NotImplementedError("This is a test class works only with 'ES' instrument")

        return self.futures_dict


