from flask import Flask, redirect, url_for, render_template, make_response, jsonify, request
from flask_restx import Api, Resource, fields
from logging.config import dictConfig

import servicelayer as sl

app = Flask(__name__)
api = Api(app, version='1.0', title='GROW - ESG Analytics API')

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

pf = api.namespace('portfoliomanagement')
prj = api.namespace('projection')
mr = api.namespace('modelrun')

portfolioupdate = pf.model('PortfolioUpdate', {
    'portfolio_newname': fields.String,
    'tickeradded': fields.String,
    'tickerremoved': fields.String
})

modelparamters = mr.model('ModelParameters', {
    'discount_rate': fields.Float,
    'growth_rate': fields.Float,
    'forecast_year': fields.Integer
})

@pf.route('/stocks')
class Stocks(Resource):
   def get(self):
        response = {}
        response['stocks'] = sl.get_stocks()
        return jsonify(response)
   
@pf.route('/portfolios')
class Portfolios(Resource):
   def get(self):
        response = {}
        response['portfolios'] = sl.get_portfolios()
        return jsonify(response)

@pf.route('/portfolios/<name>')
class Portfolio(Resource):
    def get(self, name):
        portfolio_stocks, benchmark_summary, portfolio_summary = sl.get_portfolio_data(name)
        portfolio_plot_data_esg, portfolio_plot_data = sl.get_portfolio_plot_data(name)
        portfolio_returns_data, benchmark = sl.get_portfolio_returns_data(name)
        response = {}
        response['portfolio_summary'] = portfolio_summary.to_dict(orient='records')
        response['benchmark_summary'] = benchmark_summary.to_dict(orient='records')
        response['portfolio_stocks'] = portfolio_stocks.to_dict(orient='records')
        response['plot_data'] = portfolio_plot_data.to_dict(orient='records')
        response['plot_data_esg'] = portfolio_plot_data_esg.to_dict(orient='records')
        response['returns_data'] = portfolio_returns_data.to_dict(orient='records')
        response['benchmark'] = benchmark.to_dict(orient='records')
        return jsonify(response)
   
    @pf.expect(portfolioupdate)
    def post(self, name):
        portfolio_newname = api.payload['portfolio_newname']
        tickeradded = api.payload['tickeradded']
        tickerremoved = api.payload['tickerremoved']
        added = False
        alreadyexists = False
        removed = False
        response = {}

        if (portfolio_newname is None or len(portfolio_newname) == 0):
            portfolio_newname = name
        
        if (tickeradded is not None and len(tickeradded) > 0):
            added, alreadyexists = sl.add_stock_to_portfolio(name, portfolio_newname, tickeradded)
        
        if (tickerremoved  is not None and len(tickerremoved) > 0):
            removed = sl.delete_stock_from_portfolio(name, portfolio_newname, tickerremoved)
        
        response['added'] = added
        response['alreadyexists'] = alreadyexists
        response['removed'] = removed

        return jsonify(response)
       
@prj.route('/portfolios/<name>')
class Projection(Resource):
    def get(self, name):
        result_df_grouped, pd_result, final_date = sl.get_projection_data(name)
        response = {}
        response['result_df_grouped'] = result_df_grouped.to_dict(orient = 'records')
        response['pd_result'] = pd_result.to_dict(orient = 'records')
        response['final_date'] = final_date

        return jsonify(response)

@prj.route('/comparison/<port1>/<port2>')
class Comparison(Resource):
    def get(self, port1, port2):
        response = {}
        port1_df_grouped, port1_result = sl.get_projection_data(port1)
        port2_df_grouped, port2_result = sl.get_projection_data(port2)
        response['port1_df_grouped'] = port1_df_grouped.to_dict(orient = 'records')
        response['port1_result'] = port1_result.to_dict(orient = 'records')
        response['port2_df_grouped'] = port2_df_grouped.to_dict(orient = 'records')
        response['port2_result'] = port2_result.to_dict(orient = 'records')

        return jsonify(response)

@mr.route('/portfolios/<name>')
class ModelRun(Resource):
    @mr.expect(modelparamters)
    def post(self, name):
        discount_rate = api.payload['discount_rate']
        growth_rate = api.payload['growth_rate']
        forecast_year = api.payload['forecast_year']
        ran = sl.run_temp_model_SAD(name, discount_rate, growth_rate, forecast_year)
        return jsonify({'ModelRan': ran})

if __name__ == '__main__':
    app.run(port = 5001)