16/01/2026 v1.1 - Implemented functionality for computing DV01 given present values.
                  Added method to DiscountCurve to produce a bumped curve by a given number of basis points.

16/01/2026 v1.0 - Implemented functionality for pricing bonds at dirty price and clean price.
                  Overhauled file structure and folder names.
                  Bug fixes.

16/01/2026 v0.9 - Added unit tests for cash_flow.py.
                  Bug fixes.

14/01/2026 v0.8 - Added unit tests for accrual_period_payment_schedule.py.

14/01/2026 v0.7 - Added unit tests for daycount.py.

14/01/2026 v0.6 - Added bootstrapping.py, which returns a DiscountCurve bootstrapped from deposit and swap quotes.
                  Added method to DiscountCurve object for adding new interpolation dates.
                  Added extrapolation functionality to interpolate_log_df.
                  Various bug fixes and consistency changes.

12/01/2026 v0.5 - Added classes for deposit quotes and interest rate swap quotes.
                  Changed imports to relative imports.
				  Corrected the 30E/360 function to use the formula.
				  Various additional validation checks and bug fixes.       

09/01/2026 v0.4 - Added a present value computation module discount\_factor.py.
                  Introduced the DiscountCurve class, which holds a set of dates with known discount rates to be interpolated to find a discount rate at a given date.
                  Added helper functions to compute the zero rate from a discount rate and vice versa.
				  Changed placeholder error string in daycount.py to be an actual value error.

03/01/2026 v0.3 - Added functions for computing cash flows for fixed rate coupons, floating rate coupons and bonds.
                  Added placeholder function to determine float rates over a period (TODO)
				  Adjusted previously implemented functions to include type hints.

02/01/2026 v0.2 - Implemented functionality for generating a list of payment schedules when given a start date, end date and payment frequency.

01/01/2026 v0.1 - Implemented functionality for computing year fractions from different day count conventions, specifically ACT/360, ACT/365 and 30E/360.

