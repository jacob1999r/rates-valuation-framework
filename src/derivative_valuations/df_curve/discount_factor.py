import math
from datetime import date
from derivative_valuations.daycount_conventions.daycount import year_fraction_computation
from operator import itemgetter
import copy

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

def _extrapolate_log_df(valuation_date_t_0_year_fraction: float,  df_0: float, valuation_date_t_year_fraction: float, valuation_date_t_1_year_fraction: float, df_1: float):
    #helper function used to extrapolate when t lies ahead of the final known discount factor date pair
    #uses flat forward rate extrapolation to coincide with the log DF interpolation
    
    #validation check
    if valuation_date_t_year_fraction <= valuation_date_t_1_year_fraction:
        raise ValueError("Extrapolation called but not required!")
    
    #compute the forward rate between t_0 and t_1
    t_0_t_1_forward_rate = (1/(valuation_date_t_1_year_fraction-valuation_date_t_0_year_fraction))*(math.log(df_0/df_1))

    #we now assume this rate holds indefinitely after t_1 and compute the df under that assumption using continuous compounding

    df = df_1*math.exp(-t_0_t_1_forward_rate*(valuation_date_t_year_fraction - valuation_date_t_1_year_fraction))
    return df

def interpolate_log_df(valuation_date_t_0_year_fraction: float,  df_0: float, valuation_date_t_year_fraction: float, valuation_date_t_1_year_fraction: float, df_1: float):
#given the year fraction between the date of the valuation and the target date t, this function will linearly interpolate the logarithms of the discount factors at dates t_0 and t_1 to get an result for the discount factor at t
#valuation date is the date at which the valuation is being computed


#we compute the year fractions [unused, now fed from function that calls]
    #valuation_date_t_0_year_fraction = year_fraction_computation(valuation_date,t_0,convention)
    #valuation_date_t_1_year_fraction = year_fraction_computation(valuation_date,t_1,convention)
    #valuation_date_t_year_fraction = year_fraction_computation(valuation_date,t,convention)

    
#validation checks
    if valuation_date_t_year_fraction < valuation_date_t_0_year_fraction:
        raise ValueError("The date specified lies before the first given discount factor!")
    if df_0 <= 0 or df_1 <= 0:
        raise ValueError("Discount factors must be greater than 0.")
    if valuation_date_t_0_year_fraction == valuation_date_t_1_year_fraction:
        raise ValueError("Interpolation boundaries cannot be equal.")
    
    #extrapolate if needed
    if valuation_date_t_year_fraction > valuation_date_t_1_year_fraction:
        df = _extrapolate_log_df(valuation_date_t_0_year_fraction,  df_0, valuation_date_t_year_fraction, valuation_date_t_1_year_fraction, df_1)
        return df

#delta represents distance along t_0 to t_1 that t lies
    delta = (valuation_date_t_year_fraction - valuation_date_t_0_year_fraction)/(valuation_date_t_1_year_fraction - valuation_date_t_0_year_fraction)

#linear interpolation of the discount factor logarithms
    df = math.exp((1-delta)*math.log(df_0)+delta*math.log(df_1))
    return df

class DiscountCurve:
#object class for the curve of discount rates
    def __init__(self, valuation_date: date, interpolation_dates: list, interpolation_dfs: list, convention: str):
    #__init__ function to setup the year fractions of the given list of interpolation boundary points, first orders them and error checks, then converts to year fractions via a given convention
        self.valuation_date = valuation_date
        self.convention = convention
        self.interpolation_dates = interpolation_dates
        self.interpolation_dfs = interpolation_dfs

        #validation checks
        if len(self.interpolation_dates) != len(self.interpolation_dfs):
            raise ValueError("Each given date must have a corresponding discount factor and vice versa!")
        if any(df <= 0 for df in self.interpolation_dfs):
            raise ValueError("Discount factors must be greater than 0.")
        
        #sort into chronological order
        self._sort()

        #compute year fractions from the list of dates to use for the interpolation
        self.interpolation_year_fractions = [year_fraction_computation(self.valuation_date, d, self.convention) for d in self.interpolation_dates] 

        #validation check that the year fraction list is strictly increasing
        for i in range(len(self.interpolation_year_fractions)-1):
            if self.interpolation_year_fractions[i+1] <= self.interpolation_year_fractions[i]:
                raise ValueError("Year fractions for each interpolation boundary must be strictly increasing!")

    def add_known_dates(self, new_interpolation_dates: list, new_interpolation_dfs: list):
        #method to add new dates that can be used for interpolation

        #validation checks
        if len(new_interpolation_dates) != len(new_interpolation_dfs):
            raise ValueError("Each given date must have a corresponding discount factor and vice versa!")
        if any(df <= 0 for df in new_interpolation_dfs):
            raise ValueError("Discount factors must be greater than 0.")
        
        #add the dates
        for d in new_interpolation_dates:
            self.interpolation_dates.append(d)
        for df in new_interpolation_dfs:
            self.interpolation_dfs.append(df)
        #sort into chronological order
        self._sort()

        #recompute year fractions from the list of dates to use for the interpolation
        self.interpolation_year_fractions = [year_fraction_computation(self.valuation_date, d, self.convention) for d in self.interpolation_dates] 

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
            elif valuation_date_t_0_year_fraction > valuation_date_t_year_fraction:
                raise ValueError("Target date cannot be before the first known date!")
            elif valuation_date_t_year_fraction > self.interpolation_year_fractions[-1]:
                return interpolate_log_df(self.interpolation_year_fractions[-2],self.interpolation_dfs[-2], valuation_date_t_year_fraction, self.interpolation_year_fractions[-1], self.interpolation_dfs[-1])
            
    def bump_curve(self, bp: float):
        #bump the curve by a given amount of basis points (1bp is 0.01% or 0.0001)
        #first copy the curve
        bumped_curve = copy.deepcopy(self)

        #validation check
        if len(bumped_curve.interpolation_dfs) != len(bumped_curve.interpolation_year_fractions):
            raise ValueError("The list of discount factors must coincide with the list of year fractions.")

        #for loop through discount factors in the copied curve, calculating the zero rate at each, bumping and then recomputing
        for i in range(len(bumped_curve.interpolation_dfs)):
            #skip if valuation date
            if bumped_curve.interpolation_year_fractions[i] == 0:
                continue

            zero_rate=_zero_rate_from_df(bumped_curve.interpolation_dfs[i],bumped_curve.interpolation_year_fractions[i])
            #bump the zero rate using _zero_rates_from_df helper
            bumped_zero_rate = zero_rate + (bp/10000)
            #recompute using _df_from_zero_rate helper
            bumped_curve.interpolation_dfs[i] =_df_from_zero_rate(bumped_zero_rate, bumped_curve.interpolation_year_fractions[i])

        return bumped_curve

    
    def _sort(self):
        #helper to sort the interpolation dates and discount factors
        #sort the interpolation dates into chronological order whilst maintaining the corresponding discount rate
        date_df_pairs=sorted(zip(self.interpolation_dates, self.interpolation_dfs), key=itemgetter(0))
        #unzip the dates and the discount factors, now ordered chronologically
        dates, dfs = zip(*date_df_pairs)
        self.interpolation_dates = list(dates)
        self.interpolation_dfs = list(dfs)

#unused present value function
"""        
def pv(cashflows: list[tuple[date, float]], curve: DiscountCurve):
    #compute the present value of some cashflows at certain dates, with discount rates at those dates given by interpolation
    pv = 0
    for i in range(len(cashflows)):
        pv = pv + curve.df(cashflows[i][0])*cashflows[i][1]
    return pv
"""
