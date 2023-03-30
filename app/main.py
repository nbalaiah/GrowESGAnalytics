from flask import Flask, redirect, url_for, render_template, make_response, jsonify, request
from flask_restx import Api, Resource, fields
import servicelayer as sl

app = Flask(__name__)
api = Api(app, version='1.0', title='GROW - ESG Analytics API')
ns = api.namespace('api')

portfolioupdate = ns.model('PortfolioUpdate', {
    'portfolio_newname': fields.String,
    'tickeradded': fields.String,
    'tickerremoved': fields.String
})

@ns.route('/stocks')
class Stocks(Resource):
   def get(self):
        response = {}
        response['stocks'] = sl.get_stocks()
        return jsonify(response)
   
@ns.route('/portfolios')
class Portfolios(Resource):
   def get(self):
        response = {}
        response['portfolios'] = sl.get_portfolios()
        return jsonify(response)

@ns.route('/portfolios/<name>')
class Portfolio(Resource):
    def get(self, name):
        portfolio_stocks, benchmark_summary, portfolio_summary = sl.get_portfolio_data(name)
        portfolio_plot_data = sl.get_portfolio_plot_data(name)
        portfolio_returns_data = sl.get_portfolio_returns_data(name)
        response = {}
        response['portfolio_summary'] = portfolio_summary.to_dict(orient='records')
        response['benchmark_summary'] = benchmark_summary.to_dict(orient='records')
        response['portfolio_stocks'] = portfolio_stocks.to_dict(orient='records')
        response['plot_data'] = portfolio_plot_data.to_dict(orient='records')
        response['returns_data'] = portfolio_returns_data.to_dict(orient='records')
        return jsonify(response)
   
    @ns.expect(portfolioupdate)
    def put(self, name):
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
       
   

if __name__ == '__main__':
    app.run(debug = True, port = 5001)