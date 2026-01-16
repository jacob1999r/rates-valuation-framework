from datetime import date

def year_fraction_computation(start_date: date, end_date: date, convention: str):
    #validation checks
    if end_date < start_date:
           raise ValueError("End date must be after start date!")

    #check which convention is being used
    if convention == "ACT/360":
            #ACT/360
            #computes number of days using standard python datetime library then divides by 360
            timedelta = end_date - start_date
            year_fraction = timedelta.days/360
    elif convention == "ACT/365":
            #ACT/365
            #computes number of days using standard python datetime library then divides by 365
            timedelta = end_date - start_date
            year_fraction = timedelta.days/365
    elif convention == "30E/360":
            #30/360 European/Eurobond basis (ISDA 2006)
            d_0 = start_date.day
            d_1 = end_date.day
            if d_0 == 31:
                   d_0 = 30
            if d_1 == 31:
                   d_1 = 30
            year_fraction = (1/360)*(360*(end_date.year-start_date.year)+30*(end_date.month-start_date.month)+(d_1-d_0))
    else:
           raise ValueError("This day count convention is either not recognised or has not yet been implemented.")
    return year_fraction