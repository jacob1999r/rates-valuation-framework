import math
from datetime import date

from derivative_valuations.df_curve.discount_factor import DiscountCurve
from derivative_valuations.daycount_conventions.daycount import year_fraction_computation
from derivative_valuations.payment_schedule.accrual_period_payment_schedule import generate_schedule
from derivative_valuations.cashflows.cash_flow import build_fixed_leg_cashflows

class DepositQuote:
    #class for a money market deposit instrument quote
    def __init__(self, start_date: date, end_date: date, rate: float, convention: str):
        self.start_date = start_date
        self.end_date = end_date
        self.rate = rate
        
        self.convention = convention

        #validation checks
        if self.end_date <= self.start_date:
            raise ValueError("Deposit end date cannot be before the deposit start date!")

    def year_fraction(self):
        #method for computing year fraction of the deposit over its lifetime
        return year_fraction_computation(self.start_date, self.end_date, self.convention)

    def df_implied(self):
        #deposit quotes are quoted money-market style, not as continuous compounding
        #as we are not computing a new discount rate here but rather deriving it from what is known, it is suitable to use simple money-market style
        return 1/(1+self.year_fraction()*self.rate)
    
class FixedForFloatingSwapQuote:
    #class for a given fixed-for-floating swap quote at a given maturity, frequencies are given as number of months
    #assume swap is at par, so we can use the par swap equation
    def __init__(self, effective_date: date, maturity_date: date, fixed_rate: float, fixed_frequency_months: int, fixed_convention: str, float_frequency_months: int, float_convention: str, notional: float = 1.0):
        self.effective_date = effective_date
        self.maturity_date = maturity_date
        self.fixed_rate = fixed_rate
        self.fixed_frequency_months = fixed_frequency_months
        self.fixed_convention = fixed_convention
        self.float_frequency_months = float_frequency_months
        self.float_convention = float_convention
        self.notional = notional

        #validation checks
        if self.maturity_date <= self.effective_date:
            raise ValueError("Swap maturity date cannot be before the effective date!")
        if self.fixed_frequency_months <= 0 or self.float_frequency_months <= 0:
            raise ValueError("Fixed payment frequency and floating payment frequency must be greater than 0!")
        
    def fixed_schedule(self):
        #method to return accrual periods for fixed leg of the swap
        return generate_schedule(self.effective_date, self.maturity_date, self.fixed_frequency_months)
    
    def floating_schedule(self):
        #method to return accrual periods for floating leg of the swap
        return generate_schedule(self.effective_date, self.maturity_date, self.float_frequency_months)
        
    def fixed_cashflows(self, notional_override: float | None = None):
        if notional_override == None:
            return build_fixed_leg_cashflows(self.fixed_schedule(), self.notional, self.fixed_rate, self.fixed_convention)
        else:
            return build_fixed_leg_cashflows(self.fixed_schedule(), notional_override, self.fixed_rate, self.fixed_convention)
        
    def solve_last_df(self, curve: DiscountCurve):
        #method for solving for a discount factor at the swap's maturity date
        fixed_schedule = self.fixed_schedule()

        #validation checks
        if not fixed_schedule:
            raise ValueError("Fixed payment schedule is empty!")
        
        #build arrays of (payment_date, year_fraction)
        payment_dates: list[date] = []
        year_fractions: list[float] = []

        for period in fixed_schedule:
            if len(period) == 3:
                accrual_start, accrual_end, payment_date = period
            else:
                raise ValueError("The fixed payment schedule periods are not in the correct format.")

            year_fraction = year_fraction_computation(accrual_start, accrual_end, self.fixed_convention)
            if year_fraction <= 0:
                raise ValueError("The year fraction must be greater than 0.")
            payment_dates.append(payment_date)
            year_fractions.append(year_fraction)
        
        #in this method, the last payment date must match the maturity date
        if payment_dates[-1] != self.maturity_date:
            raise ValueError("Last fixed payment date must equal the swap maturity_date.")
        
        #the discount factor at maturity_date is given by a/b, where
        #a = 1 - fixed_rate*sum(year_fraction_t_i * DF(t_i))
        #b = 1 + fixed_rate*year_fraction_t_n

        #to evaluate a, sum over payment dates then insert into formula
        a_sum = 0.0
        for payment_date, year_fraction in zip(payment_dates[:-1], year_fractions[:-1]):
            df = curve.df(payment_date)
            a_sum = a_sum + year_fraction*df
        a = 1 - self.fixed_rate*a_sum

        #to evaluate b, insert into formula
        b = 1 + self.fixed_rate*year_fractions[-1]

        df_maturity_date = a/b

        #validation check of result
        if df_maturity_date <= 0:
            raise ValueError("Solved discount factor at maturity date of the swap is not greater than 0!")

        return df_maturity_date
