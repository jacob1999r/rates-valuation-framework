09/01/2026 v0.4 - Added a present value computation module discount\_factor.py.

&nbsp;		  Introduced the DiscountCurve class, which holds a set of dates with known discount rates to be interpolated to find a discount rate at a given date.

&nbsp; 		  Added helper functions to compute the zero rate from a discount rate and vice versa.

&nbsp;		  Changed placeholder error string in daycount.py to be an actual value error.



03/01/2026 v0.3 - Added functions for computing cash flows for fixed rate coupons, floating rate coupons and bonds.

 		  Added placeholder function to determine float rates over a period (TODO)

 		  Adjusted previously implemented functions to include type hints.



02/01/2026 v0.2 - Implemented functionality for generating a list of payment schedules when given a start date, end date and payment frequency.



01/01/2026 v0.1 - Implemented functionality for computing year fractions from different day count conventions, specifically ACT/360, ACT/365 and 30E/360.

