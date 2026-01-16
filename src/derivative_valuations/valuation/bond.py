from datetime import date
from derivative_valuations.payment_schedule.accrual_period_payment_schedule import generate_schedule
from derivative_valuations.cashflows.cash_flow import build_bond_cashflows
from derivative_valuations.daycount_conventions.daycount import year_fraction_computation
from derivative_valuations.df_curve.discount_factor import DiscountCurve
from derivative_valuations.valuation.present_value import pv

class Bond:
#class for holding information about a bond
    def __init__(self, issue_date: date, maturity_date: date, rate: float, frequency: int, notional: float, convention: str, redemption_at_maturity: bool = True):
        self.issue_date = issue_date
        self.maturity_date = maturity_date
        self.rate = rate
        self.frequency = frequency
        self.notional = notional
        self.convention = convention
        self.redemption_at_maturity = redemption_at_maturity

    def generate_schedule(self):
        return generate_schedule(self.issue_date, self.maturity_date, self.frequency)
    
    def build_bond_cashflows(self):
        return build_bond_cashflows(self.generate_schedule(), self.notional, self.rate, self.convention, self.redemption_at_maturity)
    
def bond_accrued_interest(bond: Bond, t: date):
    #function that calculates accrued interest on a target date t

    #first check that the target date is not before or after the bonds duration, if so return 0
    if t <= bond.issue_date:
        return 0.0
    if t >=bond.maturity_date:
        return 0.0
    
    schedule = bond.generate_schedule()
    #for each accrual period check whether target date is in the period, then either return 0 (if on payment date) or return the accrued interest
    for accrual_start_date, accrual_end_date, payment_date in schedule:
        if t == payment_date:
            return 0.0
        if accrual_start_date < t < accrual_end_date:
            return bond.notional*bond.rate*year_fraction_computation(accrual_start_date, t, bond.convention)
        
def bond_dirty_price(bond: Bond, curve: DiscountCurve, valuation_date: date):
    #function for computing the dirty price of a bond at a valuation date

    #validation checks
    if valuation_date != curve.valuation_date:
        raise ValueError("The curve used to price the bond is for a different valuation date!")
    
    #compute cashflows then separate future cashflows to be used for pricing
    cashflows = bond.build_bond_cashflows()
    future_cashflows = [(payment_date, amount) for payment_date, amount in cashflows if payment_date > valuation_date]

    #return a price of 0 if no future cashflows
    if not future_cashflows:
        return 0.0

    #otherwise return present value of future cashflows
    return pv(future_cashflows, curve)

def bond_clean_price(bond: Bond, curve: DiscountCurve, valuation_date: date):
    #calculates clean price as dirty price less accrued interest
    return bond_dirty_price(bond, curve, valuation_date) - bond_accrued_interest(bond, valuation_date)

def price_bond(bond: Bond, curve: DiscountCurve, valuation_date: date):
    return bond_clean_price(bond, curve, valuation_date), bond_dirty_price(bond, curve, valuation_date), bond_accrued_interest(bond, valuation_date)