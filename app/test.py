import unittest
import os
import pandas as pd
import servicelayer 

class testGrowESGPortfolio(unittest.TestCase):

    def testGetStocks(self):
        df_sample_master = pd.read_csv('data/portfolio_sample_master.csv')
        expected = df_sample_master['Ticker'].unique().tolist()
        expected.sort()
        actual = servicelayer.get_stocks()
        self.assertEqual(expected, actual, "getStocks Test Failed")

    def testPortfolios(self):
        df_sample_master = pd.read_csv('data/portfolio_list.csv')
        expected = df_sample_master['Name'].unique().tolist()
        expected.sort()
        actual = servicelayer.get_portfolios()
        self.assertEqual(expected, actual, "getPortfolios Test Failed")


if __name__ == '__main__':
    unittest.main()