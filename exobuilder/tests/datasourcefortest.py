from exobuilder.data.datasource import DataSourceBase


class DataSourceForTest(DataSourceBase):
    def __init__(self, assetindex, date, futures_limit, options_limit):
        super().__init__(assetindex, date, futures_limit, options_limit)

    def get_extra_data(self, key, date):
        if key == 'riskfreerate':
            return 0.255
        else:
            raise NotImplementedError()

    def get_option_data(self, dbid, date):
        if dbid == 11558454:
            return {"impliedvol": 0.356}
        else:
            raise Exception()

    def get_fut_data(self, dbid, date):
        return {'close': 2770.0}