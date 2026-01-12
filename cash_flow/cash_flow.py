from datetime import date
from ..daycount.daycount import year_fraction_computation

def build_fixed_leg_cashflows(schedule: list[tuple[date, date, date]], notional: float, fixed_rate: float, convention: str):
    #function for building cash flows of a fixed rate coupon as a list
    cashflows= []
    for payment in schedule:
        #add a 2-tuple to the cashflows list, which has both the payment date and the payment amount
        cashflows.append((payment[2], notional*fixed_rate*year_fraction_computation(payment[0], payment[1], convention)))
    return cashflows

def build_bond_cashflows(schedule: list[tuple[date, date, date]], notional: float, fixed_rate: float, convention: str, redemption_at_maturity: bool):
    #function for building cash flows of a bond as a list, with the option for redemption at maturity as a boolean
    cashflows = []
    for payment in schedule:
        #add a 2-tuple to the cashflows list, which has both the payment date and the payment amount
        cashflows.append((payment[2], notional*fixed_rate*year_fraction_computation(payment[0], payment[1], convention)))
    if redemption_at_maturity == True:
        cashflows.append((schedule[-1][-1], notional))
    return cashflows

def build_float_leg_cashflows(schedule: list[tuple[date, date, date]], notional: float, convention: str):
    #function for building cash flows of a floating rate coupon as a list
    cashflows= []
    for payment in schedule:
        #add a 2-tuple to the cashflows list, which has both the payment date and the payment amount
        #calls a function to determine the floating rate
        cashflows.append((payment[2], notional*float_rate_computation(payment[0], payment[1])*year_fraction_computation(payment[0], payment[1], convention)))
    return cashflows