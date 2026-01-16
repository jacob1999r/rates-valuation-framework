from datetime import date
from dateutil.relativedelta import relativedelta

def generate_schedule(start_date: date, end_date: date, frequency: int):
    #takes frequency as the number of months between payments to determine accrual periods and payment dates, outputting a list of 3-tuples (accrual start, accrual end and payment date)
    schedule = []

    #validation checks
    if end_date <= start_date:
        raise ValueError("End date must be after start date!")
    if frequency <= 0:
        raise ValueError("Payment frequency must be greater than 0.")
    delta = relativedelta(end_date,start_date)
    if (delta.years*12)+delta.months < frequency:
        raise ValueError("The frequency of payments cannot be greater than the number of months between the start date and the end date.")

    #run a while loop until period end date surpasses or equals the end date, then break and consider stub period
    #timedelta = end_date - start_date
    #n = math.ceil(timedelta.months/frequency)
    period_start = start_date
    period_end = period_start + relativedelta(months=frequency)
    while period_end < end_date:

        #to do, payment date computation taking into consideration bank holidays etc.
        payment_date = period_end

        schedule.append((period_start, period_end, payment_date))
        period_start = period_end
        period_end = period_start + relativedelta(months=frequency)

    #stub period, again needs modification for payment date
    if period_start != end_date:
        schedule.append((period_start, end_date, end_date))
    return schedule