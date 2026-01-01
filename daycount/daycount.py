from datetime import date

def year_fraction_computation(start_date, end_date, convention):
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
            if start_date.day == 31:
                   start_date.day = 30
            if end_date.day == 31:
                   end_date.day = 30
            timedelta = end_date - start_date
            year_fraction = timedelta.days/360
    else:
           year_fraction = "This day count convention is either not recognised or has not yet been implemented."
    return year_fraction