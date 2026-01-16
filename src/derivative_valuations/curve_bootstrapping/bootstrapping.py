import math
from datetime import date
from operator import methodcaller, attrgetter

from derivative_valuations.curve_bootstrapping.financial_instruments import DepositQuote, FixedForFloatingSwapQuote
from derivative_valuations.df_curve.discount_factor import DiscountCurve

def bootstrap_discount_curve(valuation_date: date, deposit_quotes: list[DepositQuote], swap_quotes: list[FixedForFloatingSwapQuote], convention: str,):
    #function for bootstrapping a curve given a list of deposit quotes and a list of swap quotes
    #declare empty lists
    interpolation_dates = []
    interpolation_dfs = []
    
    #first we sort deposit quotes
    deposit_quotes.sort(key=methodcaller("year_fraction"))
    #validate the sorting worked correctly
    key = methodcaller("year_fraction")
    for i in range(len(deposit_quotes)-1):
        assert key(deposit_quotes[i+1])>=key(deposit_quotes[i]), "The list of deposit quotes could not be sorted."
    
    for quote in deposit_quotes:
    #for a deposit we add the end date and the implied discount factor add that date to their corresponding lists
        interpolation_dates.append(quote.end_date)
        interpolation_dfs.append(quote.df_implied())
    
    #we create our curve
    curve = DiscountCurve(valuation_date, interpolation_dates, interpolation_dfs, convention)

    #sort swap quotes
    swap_quotes.sort(key=attrgetter("maturity_date"))
    #validate the sorting worked correctly
    for i in range(len(swap_quotes)-1):
        assert swap_quotes[i+1].maturity_date>=swap_quotes[i].maturity_date, "The list of swap quotes could not be sorted."

    #we use the curve to get the discount factors at maturity for the swap quotes
    #add the new dates for use in interpolation at each step
    for quote in swap_quotes:
        new_interpolation_dates = [quote.maturity_date]
        new_interpolation_dfs = [quote.solve_last_df(curve)]
        curve.add_known_dates(new_interpolation_dates, new_interpolation_dfs)

    return curve