import math
from datetime import date
from derivative_valuations.payment_schedule.accrual_period_payment_schedule import generate_schedule
from derivative_valuations.cashflows.cash_flow import build_bond_cashflows
from derivative_valuations.daycount_conventions.daycount import year_fraction_computation
from derivative_valuations.df_curve.discount_factor import DiscountCurve
from derivative_valuations.valuation.present_value import pv

class FRA:
#class for holding information about a FRA (forward rate agreement)
#pay_fixed is True if we pay fixed, False otherwise
#the payment convention defaults to payment on the start date, can be adjusted to be end date
    def __init__(self, start_date: date, end_date: date, strike_rate: float, notional: float, convention: str, pay_fixed: bool):
        self.start_date = start_date
        self.end_date = end_date
        self.strike_rate = strike_rate
        self.notional = notional
        self.convention = convention
        self.pay_fixed = pay_fixed
    
    
def money_market_forward_rate_from_curve(t_0: date, t_1: date, curve: DiscountCurve, convention: str):
    #function for computing a forward rate between t_0 and t_1
    #recall that valuation_date is stored in the curve object

    #validation checks
    if t_1 <= t_0:
        raise ValueError("The forward start date must be before the end date.")
    if curve.valuation_date > t_0:
        raise ValueError("Valuation date cannot be before the forward start date.")
    
    #compute discount factors at t_0 and t_1 from the curve
    df_t_0 = curve.df(t_0)
    df_t_1 = curve.df(t_1)

    #validation checks
    if df_t_0 <= 0 or df_t_1 <= 0:
        raise ValueError("Discount factors must be nonzero and positive.")

    #compute year fraction of the forward
    year_fraction_t_0_t_1 = year_fraction_computation(t_0, t_1, convention)

    #the forward rate is implied by the curve by the following formula, which gives the simple forward rate between t_0 and t_1 (money-market style)
    forward_rate = (1/year_fraction_t_0_t_1)*((df_t_0/df_t_1)-1)

    return forward_rate

def _FRA_payoff(fra: FRA, curve: DiscountCurve):
    #compute FRA payoff at start date in-line with standards

    #compute the implied forward rate
    implied_forward_rate = money_market_forward_rate_from_curve(fra.start_date, fra.end_date, curve, fra.convention)

    year_fraction_start_date_end_date = year_fraction_computation(fra.start_date, fra.end_date, fra.convention)
    payoff = fra.notional*year_fraction_start_date_end_date*((implied_forward_rate-fra.strike_rate)/(1+year_fraction_start_date_end_date*implied_forward_rate))

    #consider whether paying fixed or paying floating
    if fra.pay_fixed == False:
        payoff = payoff * -1
    return payoff
    


def FRA_price(fra: FRA, curve: DiscountCurve, valuation_date: date):
    #prices an FRA by computing the implied simple forward rate from the curve, then discounting the sole cashflow

    #validation checks
    if valuation_date != curve.valuation_date:
        raise ValueError("The curve used to price the bond is for a different valuation date!")

    #assume we settle at t_0 in-line with standards
    payoff = _FRA_payoff(fra, curve)

    #compute the cashflow from the payoff
    fra_cashflow = [(fra.start_date, payoff)]

    return pv(fra_cashflow, curve)





