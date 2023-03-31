import unittest
import os
import pandas as pd
import servicelayer
import random

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

    def testAddPortfolio(self):
        expected = len(pd.read_csv('data/portfolio_list.csv')) + 1
        servicelayer.add_portfolio_to_list("AppTestPortfolio" + str(random.randint(10, 100)))
        portfoliolist = pd.read_csv('data/portfolio_list.csv')
        actual = len(portfoliolist)
        self.assertEqual(expected, actual, "testAddPortfolio Test Failed")

    def testAddStockToPortfolio(self):
        added, alreadyexists = servicelayer.add_stock_to_portfolio("portfolio_sample_2", "portfolio_sample_1", "Test1")
        self.assertEqual(True, added, "testAddStockToPortfolio Test Failed")

    def testDeleteStockToPortfolio(self):
        deleted = servicelayer.delete_stock_from_portfolio("portfolio_sample_2", "portfolio_sample_1", "Test1")
        self.assertEqual(True, deleted, "testDeleteStockToPortfolio Test Failed")

    def testCalculateSAD(self):
        actual = servicelayer.calculate_SAD(23.6, "31-Mar-2023")
        self.assertEqual(0.004482437194820285, actual, "testCalculateSAD Test Failed")

if __name__ == '__main__':
    unittest.main()