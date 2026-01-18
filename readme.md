# Derivative Valuations Tool

## Jacob Russell

A small fixed-income valuation and risk analytics library, with the following features:
- bootstrap discount curves from deposit quotes and par swap quotes, using the '`DiscountCurve` object;
- interpolate/extrapolate the discount curve to find discount factors at a given date;
- generate cashflows using a number of daycount conventions,
- compute PV and risk sensitivities via bump/revalue.

The following features are a work in progress:
- implementation of additional financial instruments to price;
- alternative extrapolation methods;
- using BoE API to draw real market data and produce a daily output highlighting changes to prices;
- full unit test library.

## Features
### Curve construction
- Sequential curve bootstrapping:
  - Money-market deposits give implied discount factors;
  - Fixed-for-floating par swap quotes are used to solve the last discount factor iteratively.
- `DiscountCurve` supports:
  - log discount factor interpolation between curve nodes;
  - extrapolation beyond last node using flat forward rate assumption;
  - parallel bumps to node zero rates (continuous compounding).

### Cashflows and schedules
- Accrual-period payment schedule generation.
- Day count conventions:
  - ACT/360;
  - ACT/365;
  - 30E/360 (Eurobond).
- Cashflow builders:
  - fixed leg coupon cashflows;
  - bond cashflows (with optional redemption at maturity).
- Bond pricing:
  - accrued interest;
  - clean / dirty pricing.

### Valuation and risk
- Present value of dated cashflows using a `DiscountCurve`
- DV01 via bump/revalue on the discount curve for parallel shifts
- Convexity via symmetric bump/revalue (second difference)

## Project layout
- `src/derivative_valuations/`
  - `curve_bootstrapping/` deposits + swaps + bootstrap logic
  - `df_curve/` discount curve object, interpolation/extrapolation and curve bumping
  - `daycount_conventions/` year fraction computations
  - `payment_schedule/` accrual schedule generation
  - `cashflows/` cashflow generation
  - `valuation/` risk sensitivities and instrument pricing utilities
- `tests/` pytest unit tests