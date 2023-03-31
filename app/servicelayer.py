import os
import pandas as pd
import math
from dateutil.relativedelta import relativedelta
from datetime import datetime
import random

basedir = os.path.abspath(os.path.dirname(__file__))

def get_stocks():
    csv_sample_master = os.path.join(basedir, 'data/portfolio_sample_master.csv')
    df_sample_master = pd.read_csv(csv_sample_master)
    stocks = df_sample_master['Ticker'].unique().tolist()
    stocks.sort()
    return stocks
    
def get_portfolios():
    csv_portfolio_list = os.path.join(basedir, 'data/portfolio_list.csv')
    df_portfolio_list = pd.read_csv(csv_portfolio_list)
    portfolios = df_portfolio_list['Name'].unique().tolist()
    portfolios.sort()
    return portfolios

def get_portfolio_data(name):
   portfolio_file = os.path.join(basedir, 'data/' + name + '.csv')
   try:
       benchmark_file = os.path.join(basedir, 'data/benchmark_{0}.csv'.format(name))
       benchmark = pd.read_csv(benchmark_file)
   except:
       benchmark_file = os.path.join(basedir, 'data/benchmark.csv'.format(name))
       benchmark = pd.read_csv(benchmark_file)

   portfolio = pd.read_csv(portfolio_file)
   portfolio['CreatedDate']= pd.to_datetime(portfolio['CreatedDate'])
   benchmark['CreatedDate']= pd.to_datetime(benchmark['CreatedDate'])
   maxdate = portfolio['CreatedDate'].max()
   mindate = portfolio['CreatedDate'].min()
   tickers = portfolio['Ticker'].unique()
   portfolio_stocks = pd.DataFrame()
   benchmark_summary = pd.DataFrame()
   portfolio_summary = pd.DataFrame()
   invested_value_bench = benchmark.query('CreatedDate ==\'' + str(mindate) + '\'')['Invested_Value'].iloc[0]
   current_value_bench = benchmark.query('CreatedDate ==\'' + str(maxdate) + '\'')['Invested_Value'].iloc[0]
   benchmark_summary = benchmark_summary.append({'Invested_Value':invested_value_bench,'Current_Value':current_value_bench},ignore_index=True)

   invested_value_port = portfolio.query('CreatedDate ==\'' + str(mindate) + '\'')['Invested_Value'].sum()
   current_value_port = portfolio.query('CreatedDate ==\'' + str(maxdate) + '\'')['Invested_Value'].sum()
   portfolio_summary = portfolio_summary.append({'Invested_Value':invested_value_port,'Current_Value':current_value_port},ignore_index=True)

   for ticker in tickers:
        invested_value = portfolio.query('CreatedDate ==\'' + str(mindate) + '\' and Ticker ==\'' + ticker + '\'')['Invested_Value'].iloc[0]
        current_value = portfolio.query('CreatedDate ==\'' + str(maxdate) + '\' and Ticker ==\'' + ticker + '\'')['Invested_Value'].iloc[0]
        climate_value = portfolio.query('CreatedDate ==\'' + str(maxdate) + '\' and Ticker ==\'' + ticker + '\'')['Climate'].iloc[0]
        portfolio_stocks = portfolio_stocks.append({'Ticker':ticker,'Invested_Value': invested_value,'Current_Value':current_value,'Climate': climate_value},ignore_index=True)
   return portfolio_stocks, benchmark_summary, portfolio_summary


def get_portfolio_plot_data(name):
    portfolio = pd.read_csv(os.path.join(basedir,"data/{0}.csv".format(name)))
    portfolio_grouped = portfolio.groupby(['CreatedDate'])['Invested_Value'].agg("sum")
    portfolio_grouped_esg = portfolio.groupby(['CreatedDate'])['ESGScore'].agg("mean")

    portfolio_grouped.to_csv(os.path.join(basedir,"data/portfolio_grouped_stock_{0}.csv".format(name)))
    portfolio_grouped = pd.read_csv(os.path.join(basedir,"data/portfolio_grouped_stock_{0}.csv".format(name)))
    portfolio_grouped['CreatedDate']= pd.to_datetime(portfolio_grouped['CreatedDate'])
    portfolio_grouped.sort_values(['CreatedDate'],inplace=True)
    
    portfolio_grouped_esg.to_csv(os.path.join(basedir,"data/portfolio_grouped_esg_{0}.csv".format(name)))
    portfolio_grouped_esg = pd.read_csv(os.path.join(basedir,"data/portfolio_grouped_esg_{0}.csv".format(name)))
    portfolio_grouped_esg['CreatedDate']= pd.to_datetime(portfolio_grouped['CreatedDate'])
    portfolio_grouped_esg.sort_values(['CreatedDate'],inplace=True)
    return portfolio_grouped_esg

def get_portfolio_returns_data(name):
    basedir = os.path.abspath(os.path.dirname(__file__))
    portfolio_grouped = pd.read_csv(os.path.join(basedir,"data/portfolio_grouped_stock_{0}.csv".format(name)))

    benchmark = pd.DataFrame()
    try:
        benchmark_file = os.path.join(basedir, 'data/benchmark_{0}.csv'.format(name))
        benchmark = pd.read_csv(benchmark_file)
    except:
        benchmark_file = os.path.join(basedir, 'data/benchmark.csv'.format(name))
        benchmark = pd.read_csv(benchmark_file)
    
    portfolio_grouped['CreatedDate']= pd.to_datetime(portfolio_grouped['CreatedDate'])
    portfolio_grouped.sort_values(['CreatedDate'],inplace=True)
    portfolio_grouped['ROIC'] = portfolio_grouped['Invested_Value']
    return portfolio_grouped

def add_stock_to_portfolio(portfolio_name, portfolio_newname, ticker):
    portfolio_file = os.path.join(basedir, 'data/{0}.csv'.format(portfolio_name))
    portfolio = pd.read_csv(portfolio_file)
    portfolio_master = pd.read_csv(os.path.join(basedir,'data/{0}.csv'.format('portfolio_sample_master')))
    tickerquery = portfolio.query('Ticker ==\'' + ticker + '\'')
    added = False
    alreadyexists = False

    if tickerquery.empty == True:
        portfolio = portfolio.append(portfolio_master.query('Ticker ==\'' + ticker + '\''))
        added = True
    else:
        alreadyexists = True
    portfolio_to_file = os.path.join(basedir, 'data/{0}.csv'.format(portfolio_newname))
    portfolio.to_csv(portfolio_to_file)
    add_portfolio_to_list(portfolio_newname)
    return added, alreadyexists

def add_portfolio_to_list(portfolio_name):
    portfolio_file = os.path.join(basedir, 'data/portfolio_list.csv')
    portfoliolist = pd.read_csv(portfolio_file)
    res = portfoliolist.query('Name ==\'' + portfolio_name + '\'')
    if res.empty == True:
        portfoliolist = portfoliolist.append({'Name': portfolio_name}, ignore_index = True)
        portfoliolist.to_csv(portfolio_file)

def delete_stock_from_portfolio(portfolio_name, portfolio_newname, ticker):
    portfolio_file = os.path.join(basedir, 'data/{0}.csv'.format(portfolio_name))
    to_portfolio_file = os.path.join(basedir, 'data/{0}.csv'.format(portfolio_newname))
    portfolio = pd.read_csv(portfolio_file)
    portfolio['Ticker'].str.replace(' ','')
    portfolio.drop(portfolio[portfolio['Ticker'].str.contains(ticker.replace(' ',''))].index, inplace = True)
    add_portfolio_to_list(portfolio_newname)
    portfolio.to_csv(to_portfolio_file)
    return True

def get_projection_data(portfolio_name):
    pd_result = pd.DataFrame()
    projection_file = os.path.join(basedir, 'data/projected_result_{0}.csv'.format(portfolio_name))
    portfolio_file = os.path.join(basedir, 'data/{0}.csv'.format(portfolio_name))
    portfolio = pd.read_csv(portfolio_file)
    portfolio['CreatedDate']= pd.to_datetime(portfolio['CreatedDate'])
    final_date = portfolio['CreatedDate'].max()
    year, month, day = str(final_date).split('-')
    projection = pd.read_csv(projection_file)
    projection['CreatedDate']= pd.to_datetime(projection['CreatedDate'])
    maxdate = projection['CreatedDate'].max()
    mindate = projection['CreatedDate'].min()
    pd_result_2050 = projection.query('CreatedDate ==\''+str(maxdate)+'\'')
    for index, row in pd_result_2050.iterrows():       
        invested_amount = projection.query('CreatedDate ==\''+str(mindate)+'\' and Ticker ==\'' + row['Ticker']+ '\'')['Invested_Value'].iloc[0]
        print(invested_amount)
        pd_result = pd_result.append({'Ticker':row['Ticker'],'Invested_Value': invested_amount,'_2050_Value':row['Invested_Value'],'Company':row['Company'],'Country':row['Country']},ignore_index=True)

    projection_grouped = projection.groupby(['CreatedDate'])['Invested_Value'].sum()
    result_df = projection_grouped
      
    result_df.to_csv(os.path.join(basedir,"data/result_df_grouped_{0}.csv".format(portfolio_name)))
    result_df = pd.read_csv(os.path.join(basedir,"data/result_df_grouped_{0}.csv".format(portfolio_name)))
    result_df['CreatedDate']= pd.to_datetime(result_df['CreatedDate'])
    
    result_df.sort_values(['CreatedDate'],inplace=True)
    result_df_grouped = result_df.groupby(['CreatedDate'])['Invested_Value'].sum()
    
    result_df_grouped.to_csv(os.path.join(basedir,"data/result_df_grouped_1_{0}.csv".format(portfolio_name)))
    result_df_grouped = pd.read_csv(os.path.join(basedir,"data/result_df_grouped_1_{0}.csv".format(portfolio_name)))
    result_df_grouped['CreatedDate']= pd.to_datetime(result_df_grouped['CreatedDate'])

    return result_df_grouped, pd_result

def calculate_SAD(latitude, created_date):
    print('SAD calculation entered')
    latitude = float(latitude)
    year, month, day = created_date.split('-')
    day=day[:2]
    inside = 2 * 3.14 / 365 * (float(day) - 80.25)
    sun_inclination_angle = 0.4102 * math.sin(inside)
    ht = 24 - (7.72 * (- math.tan(2 * 3.14 * latitude / 360) * math.tan(sun_inclination_angle)))
    SAD = ht - 12
    return(SAD/(24*100))

def run_temp_model_SAD(portfolio_name, discount_rate, growth_rate, year):
    print('model calculation entered')
    vol_list = [(-0.10/252) * 30, 0,(0.10/252) * 30  ]
    print('volatility loaded')

    portfolio = pd.DataFrame()
    portfolio_file = os.path.join(basedir, 'data/' + portfolio_name + '.csv')
    portfolio = pd.read_csv(portfolio_file)
    print('climate data loaded')
    climate_file = os.path.join(basedir, 'data/climate_master.csv')
    climate_data = pd.DataFrame()
    climate_data = pd.read_csv(climate_file)
    print('correlation data loaded')
    corr_file = os.path.join(basedir, 'data/corr_master.csv')
    corr_data = pd.DataFrame()
    corr_q = pd.read_csv(corr_file)
    corr_q = corr_q.query('Stock_Price != 1')
    corr_q.update(corr_q.fillna(0))
    corr_data = corr_q

    output_file = os.path.join(basedir, "data/projected_result_{0}.csv".format(portfolio_name))

    discount_rate = discount_rate/12
    growth_rate = growth_rate/12
    print(year)
    
    a_df=portfolio.filter(items=['Company','Country','Ticker','Quantity','Latitude']).drop_duplicates()
    a_df_temp = a_df.copy()
    a_df_temp['CreatedDate'] = datetime.now
    a_df_temp['Stock_Price'] = 0
    a_df_temp['Invested_Value'] = 0
    a_df_temp.drop(a_df_temp.index,inplace=True) 
    start_date_projection = pd.to_datetime(portfolio['CreatedDate']).max()
    print('iterating through the list of stocks to forecast')

    for index,row in a_df.iterrows():
        print(row)
        precond_df = portfolio.query('Country ==\''+ row['Country'] + '\' and Ticker==\'' + row['Ticker'] + '\'')
        precond_df['CreatedDate']= pd.to_datetime(precond_df['CreatedDate'])
        start_date_projection = precond_df['CreatedDate'].max()
        start_year = start_date_projection.year
        no_of_years = year - start_year
        no_of_months = no_of_years * 12
        precond_df = precond_df.query('CreatedDate ==\'' + str(start_date_projection)+ '\'')
        precond_df=precond_df.filter(items=['Company','Country','Ticker','Quantity','CreatedDate','Stock_Price','Invested_Value'])
        print('the no of months to forecast ' + str(no_of_months))

        previous_month_date = start_date_projection
        another_temp = precond_df.query('CreatedDate ==\'' + str(previous_month_date)+ '\' and Ticker ==\'' +row['Ticker']+ '\'')
        prev_stock_price = another_temp['Stock_Price'].iloc[0]
        for month in range (1, no_of_months):
            next_month_date = start_date_projection + relativedelta(months=+month)
            another_temp = a_df_temp.query('CreatedDate ==\'' + str(previous_month_date)+ '\' and Ticker ==\'' +row['Ticker']+ '\'')
            try:
                if month != 1:
                    prev_stock_price = another_temp['Stock_Price'].iloc[0]
            except:
                continue
            print('get the previous stock value')
            query_fossil = climate_data.query('Ticker ==\'' + row['Ticker'] + '\'')
            print(query_fossil)
            vol = random.choice(vol_list)
            print('calculate the new stock value')
            if query_fossil.empty == False and query_fossil['Ticker'].iloc[0] == row['Ticker']:
                query_corr= corr_data.query('Country ==\'' + row['Country']+ '\'')
                query_corr = query_corr[query_corr['Measure'].str.contains("Fossil")]
                if query_corr.empty == True:
                    corr = 0
                else:
                    corr = query_corr['Stock_Price'].mean()

                new_stock_price = prev_stock_price * (1 - calculate_SAD(row['Latitude'],str(previous_month_date)) - (corr/12) - discount_rate + vol+ growth_rate)
            else:
                new_stock_price = prev_stock_price * (1 - discount_rate + vol + growth_rate)
            a_df_temp = a_df_temp.append({'Company':row['Company'],'Country':row['Country'],'Ticker':row['Ticker'],'Quantity':row['Quantity'], 'CreatedDate':next_month_date,'Stock_Price':new_stock_price,'Invested_Value':row['Quantity'] * new_stock_price}, ignore_index=True)
            print(prev_stock_price)
            print('update the new stock value and continue the loop')
            previous_month_date = next_month_date
    print(a_df_temp)
    a_df_temp = a_df_temp.append(portfolio)
    a_df_temp.to_csv(output_file)
    return True

