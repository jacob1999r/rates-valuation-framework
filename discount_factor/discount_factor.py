import math
from datetime import date
from daycount.daycount import year_fraction_computation
from operator import itemgetter

def _df_from_zero_rate(zero_rate: float, year_fraction: float):
    #function that computes the discount factor from a zero rate, using continuous compounding (as is used throughout)
    df = math.exp(-year_fraction*zero_rate)
    return df

def _zero_rate_from_df(df: float, year_fraction: float):
    #function that computes the zero rate from a discount factor, using continuous compounding (as is used throughout)
    if year_fraction == 0:
        raise ValueError("In order to compute the zero rate from the discount factor, the start and end date cannot be the same.")
    zero_rate = math.log(df)/(-year_fraction)
    return zero_rate

def interpolate_log_df(valuation_date_t_0_year_fraction: float,  df_0: float, valuation_date_t_year_fraction: float, valuation_date_t_1_year_fraction: float, df_1: float):
#given the year fraction between the date of the valuation and the target date t, this function will linearly interpolate the logarithms of the discount factors at dates t_0 and t_1 to get an result for the discount factor at t
#valuation date is the date at which the valuation is being computed


#we compute the year fractions [unused, now fed from function that calls]
    #valuation_date_t_0_year_fraction = year_fraction_computation(valuation_date,t_0,convention)
    #valuation_date_t_1_year_fraction = year_fraction_computation(valuation_date,t_1,convention)
    #valuation_date_t_year_fraction = year_fraction_computation(valuation_date,t,convention)

    
#validation checks
    if valuation_date_t_year_fraction > valuation_date_t_1_year_fraction or valuation_date_t_year_fraction < valuation_date_t_0_year_fraction:
        raise ValueError("The date specified lies outside of the given interpolation boundaries.")
    if df_0 <= 0 or df_1 <= 0:
        raise ValueError("Discount factors must be greater than 0.")
    if valuation_date_t_0_year_fraction == valuation_date_t_1_year_fraction:
        raise ValueError("Interpolation boundaries cannot be equal.")

#λ represents distance along t_0 to t_1 that t lies
    λ = (valuation_date_t_year_fraction - valuation_date_t_0_year_fraction)/(valuation_date_t_1_year_fraction - valuation_date_t_0_year_fraction)

#linear interpolation of the discount factor logarithms
    df = math.exp((1-λ)*math.log(df_0)+λ*math.log(df_1))
    return df

class DiscountCurve:
#object class for the curve of discount rates
    def __init__(self, valuation_date: date, interpolation_dates: list, interpolation_dfs: list, convention: str):
    #__init__ function to setup the year fractions of the given list of interpolation boundary points, first orders them and error checks, then converts to year fractions via a given convention
        self.valuation_date = valuation_date
        self.convention = convention

        #validation checks
        if len(interpolation_dates) != len(interpolation_dfs):
            raise ValueError("Each given date must have a corresponding discount factor and vice versa!")
        if any(df <= 0 for df in interpolation_dfs):
            raise ValueError("Discount factors must be greater than 0.")
        
        #sort the interpolation dates into chronological order whilst maintaining the corresponding discount rate
        date_df_pairs=sorted(zip(interpolation_dates, interpolation_dfs), key=itemgetter(0))
        #unzip the dates and the discount factors, now ordered chronologically
        self.interpolation_dates, self.interpolation_dfs = zip(*date_df_pairs)

        #compute year fractions from the list of dates to use for the interpolation
        self.interpolation_year_fractions = [year_fraction_computation(self.valuation_date, date, self.convention) for date in self.interpolation_dates] 

        #validation check that the year fraction list is strictly increasing
        for i in range(len(self.interpolation_year_fractions)-1):
            if self.interpolation_year_fractions[i+1] <= self.interpolation_year_fractions[i]:
                raise ValueError("Year fractions for each interpolation boundary must be strictly increasing!")

    def df(self, t: date):
        #function that interpolates to find a discount rate on a target date t    
        
        #cashflows occurring before or on the valuation date have df 1.0
        if t <= self.valuation_date:
            return 1.0
        
        #otherwise compute target date year fraction (from valuation date to t)
        valuation_date_t_year_fraction = year_fraction_computation(self.valuation_date, t, self.convention)

        #edge cases where the target date is equal to a given date (from the available dates for interpolation)
        #just returns the discount factor at that date
        for valuation_date_t_i_year_fraction, df in zip(self.interpolation_year_fractions, self.interpolation_dfs):
            if valuation_date_t_i_year_fraction == valuation_date_t_year_fraction:
                return df
            
        #otherwise interpolate between the lower and upper nearest known dates
        for i in range(len(self.interpolation_year_fractions)-1):
            valuation_date_t_0_year_fraction = self.interpolation_year_fractions[i]
            valuation_date_t_1_year_fraction = self.interpolation_year_fractions[i+1]

            if valuation_date_t_0_year_fraction < valuation_date_t_year_fraction < valuation_date_t_1_year_fraction:
                return interpolate_log_df(valuation_date_t_0_year_fraction,self.interpolation_dfs[i], valuation_date_t_year_fraction, valuation_date_t_1_year_fraction, self.interpolation_dfs[i+1])
        raise ValueError("Target date lies outside range of known interpolation boundaries!")
        
def pv(cashflows: list[tuple[date, float]], curve: DiscountCurve):
    #compute the present value of some cashflows at certain dates, with discount rates at those dates given by interpolation
    pv = 0
    for i in range(len(cashflows)):
        pv = pv + curve.df(cashflows[i][0])*cashflows[i][1]
    return pv

