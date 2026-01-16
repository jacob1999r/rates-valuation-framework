from datetime import date
import pytest
from cash_flow.cash_flow import build_fixed_leg_cashflows, build_bond_cashflows

class TestFixedLegCashflows:
    def test_empty_schedule(self):
        with pytest.raises(ValueError, match="Payment schedule is empty!"):
            build_fixed_leg_cashflows([], 100, 0.05, "ACT/360")

    def test_negative_notional(self):
        with pytest.raises(ValueError, match="Notional payment must not be less than 0."):
            build_fixed_leg_cashflows([
        (date(2026,1,1), date(2026,2,1), date(2026,2,1)),
        (date(2026,2,1), date(2026,3,1), date(2026,3,1)),
        (date(2026,3,1), date(2026,4,1), date(2026,4,1))], -100, 0.05, "ACT/360")
            
    def test_negative_fixed_rate(self):
        with pytest.raises(ValueError, match="Fixed rate must not be less than 0."):
            build_fixed_leg_cashflows([
        (date(2026,1,1), date(2026,2,1), date(2026,2,1)),
        (date(2026,2,1), date(2026,3,1), date(2026,3,1)),
        (date(2026,3,1), date(2026,4,1), date(2026,4,1))], 100, -0.05, "ACT/360")

    def test_basic_cashflow_ACT_360(self):
        assert build_fixed_leg_cashflows([
        (date(2026,1,1), date(2026,2,1), date(2026,2,1)),
        (date(2026,2,1), date(2026,3,1), date(2026,3,1)),
        (date(2026,3,1), date(2026,4,1), date(2026,4,1))],
        100, 0.05, "ACT/360") == [
    (date(2026,2,1), pytest.approx(100 * 0.05 * (31/360))),
    (date(2026,3,1), pytest.approx(100 * 0.05 * (28/360))),
    (date(2026,4,1), pytest.approx(100 * 0.05 * (31/360)))
        ]
    
    def test_basic_cashflow_ACT_365(self):
        assert build_fixed_leg_cashflows([
        (date(2026,1,1), date(2026,2,1), date(2026,2,1)),
        (date(2026,2,1), date(2026,3,1), date(2026,3,1)),
        (date(2026,3,1), date(2026,4,1), date(2026,4,1))],
        100, 0.05, "ACT/365") == [
    (date(2026,2,1), pytest.approx(100 * 0.05 * (31/365))),
    (date(2026,3,1), pytest.approx(100 * 0.05 * (28/365))),
    (date(2026,4,1), pytest.approx(100 * 0.05 * (31/365)))
        ]

    def test_basic_cashflow_30E_360(self):
    #31/01/2026 -> 28/02/2026 is still 28 days when adjusted for 30E/360
    #using the formula gives (360(2026-2026)+30(2-1)+(28-30))/360=28/360
    #28/02/2026 -> 31/03/2026 is 32 days when adjusted for 30E/360
    #using the formula gives (360(2026-2026)+30(3-2)+(30-28))/360=28/360
    #31/03/2026 -> 30/04/2026 is 30 days when adjusted for 30E/360
    #using the formula gives (360(2026-2026)+30(4-3)+(30-30))/360=28/360
        assert build_fixed_leg_cashflows([
        (date(2026,1,31), date(2026,2,28), date(2026,2,28)),
        (date(2026,2,28), date(2026,3,31), date(2026,3,31)),
        (date(2026,3,31), date(2026,4,30), date(2026,4,30))],
        100, 0.05, "30E/360") == [
    (date(2026,2,28), pytest.approx(100 * 0.05 * (28/360))),
    (date(2026,3,31), pytest.approx(100 * 0.05 * (32/360))),
    (date(2026,4,30), pytest.approx(100 * 0.05 * (30/360)))
        ]

class TestBondCashflows:
    def test_empty_schedule(self):
        with pytest.raises(ValueError, match="Payment schedule is empty!"):
            build_bond_cashflows([], 100, 0.05, "ACT/360", False)

    def test_negative_notional(self):
        with pytest.raises(ValueError, match="Notional payment must not be less than 0."):
            build_bond_cashflows([
        (date(2026,1,1), date(2026,2,1), date(2026,2,1)),
        (date(2026,2,1), date(2026,3,1), date(2026,3,1)),
        (date(2026,3,1), date(2026,4,1), date(2026,4,1))], -100, 0.05, "ACT/360", False)
            
    def test_negative_fixed_rate(self):
        with pytest.raises(ValueError, match="Fixed rate must not be less than 0."):
            build_bond_cashflows([
        (date(2026,1,1), date(2026,2,1), date(2026,2,1)),
        (date(2026,2,1), date(2026,3,1), date(2026,3,1)),
        (date(2026,3,1), date(2026,4,1), date(2026,4,1))], 100, -0.05, "ACT/360", False)

    def test_basic_cashflow_ACT_360(self):
        assert build_bond_cashflows([
        (date(2026,1,1), date(2026,2,1), date(2026,2,1)),
        (date(2026,2,1), date(2026,3,1), date(2026,3,1)),
        (date(2026,3,1), date(2026,4,1), date(2026,4,1))],
        100, 0.05, "ACT/360", False) == [
    (date(2026,2,1), pytest.approx(100 * 0.05 * (31/360))),
    (date(2026,3,1), pytest.approx(100 * 0.05 * (28/360))),
    (date(2026,4,1), pytest.approx(100 * 0.05 * (31/360)))
        ]

    def test_with_maturity_cashflow_ACT_360(self):
        assert build_bond_cashflows([
        (date(2026,1,1), date(2026,2,1), date(2026,2,1)),
        (date(2026,2,1), date(2026,3,1), date(2026,3,1)),
        (date(2026,3,1), date(2026,4,1), date(2026,4,1))],
        100, 0.05, "ACT/360", True) == [
    (date(2026,2,1), pytest.approx(100 * 0.05 * (31/360))),
    (date(2026,3,1), pytest.approx(100 * 0.05 * (28/360))),
    (date(2026,4,1), pytest.approx(100 * 0.05 * (31/360))),
    (date(2026,4,1), 100)
        ]
    
    def test_with_maturity_cashflow_ACT_365(self):
        assert build_bond_cashflows([
        (date(2026,1,1), date(2026,2,1), date(2026,2,1)),
        (date(2026,2,1), date(2026,3,1), date(2026,3,1)),
        (date(2026,3,1), date(2026,4,1), date(2026,4,1))],
        100, 0.05, "ACT/365", True) == [
    (date(2026,2,1), pytest.approx(100 * 0.05 * (31/365))),
    (date(2026,3,1), pytest.approx(100 * 0.05 * (28/365))),
    (date(2026,4,1), pytest.approx(100 * 0.05 * (31/365))),
    (date(2026,4,1), 100)
        ]

    def test_with_maturity_cashflow_30E_360(self):
    #31/01/2026 -> 28/02/2026 is still 28 days when adjusted for 30E/360
    #using the formula gives (360(2026-2026)+30(2-1)+(28-30))/360=28/360
    #28/02/2026 -> 31/03/2026 is 32 days when adjusted for 30E/360
    #using the formula gives (360(2026-2026)+30(3-2)+(30-28))/360=28/360
    #31/03/2026 -> 30/04/2026 is 30 days when adjusted for 30E/360
    #using the formula gives (360(2026-2026)+30(4-3)+(30-30))/360=28/360
        assert build_bond_cashflows([
        (date(2026,1,31), date(2026,2,28), date(2026,2,28)),
        (date(2026,2,28), date(2026,3,31), date(2026,3,31)),
        (date(2026,3,31), date(2026,4,30), date(2026,4,30))],
        100, 0.05, "30E/360", True) == [
    (date(2026,2,28), pytest.approx(100 * 0.05 * (28/360))),
    (date(2026,3,31), pytest.approx(100 * 0.05 * (32/360))),
    (date(2026,4,30), pytest.approx(100 * 0.05 * (30/360))),
    (date(2026,4,30), 100)
        ]
    