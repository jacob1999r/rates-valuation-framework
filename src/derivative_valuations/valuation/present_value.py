from datetime import date
from derivative_valuations.df_curve.discount_factor import DiscountCurve

def pv(cashflows: list[tuple[date, float]], curve: DiscountCurve):
    #function to compute present value of future cash flows from a discount factor given on the curve
    pv = 0.0

    #validation checks
    if not cashflows:
        raise ValueError("Cash flows are empty!")

    #cycle through cashflows, discount them using the curve and then add to pv
    for cashflow in cashflows:
        pv = pv + curve.df(cashflow[0])*cashflow[1]
    return pv

def DV01(cashflows: list[tuple[date, float]], curve: DiscountCurve, bp: float, absolute: bool = False):
    #compute DV01 given a set of cashflows, a curve and a basis point bump
    #optionally compute as absolute
    #first bump curve
    bumped_curve = curve.bump_curve(bp)
    #bumped pv less base pv
    DV01 = pv(cashflows, bumped_curve) - pv(cashflows, curve)
    if absolute == True:
        return abs(DV01)
    else:
        return DV01