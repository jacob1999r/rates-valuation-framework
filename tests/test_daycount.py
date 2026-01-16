from datetime import date
import pytest
from derivative_valuations.daycount_conventions.daycount import year_fraction_computation

class TestYearFractionComputation:
    def test_raises_if_end_before_start(self):
        with pytest.raises(ValueError, match="End date must be after start date!"):
            year_fraction_computation(date(1999,11,23), date(1999,11,22), "ACT/360")

    def test_raises_if_convention_unknown(self):
        with pytest.raises(ValueError, match="This day count convention is either not recognised or has not yet been implemented."):
            year_fraction_computation(date(1999,11,23), date(1999,12,23), "ACT/400")
    
    def test_act_360_basic(self):
        #01/01/2026 -> 31/01/2026 is 30 days
        assert year_fraction_computation(date(2026,1,1), date(2026,1,31), "ACT/360") == pytest.approx(30/360)

    def test_act_360_basic2(self):
        #01/01/2026 -> 28/02/2026 is 58 days
        assert year_fraction_computation(date(2026,1,1), date(2026,2,28), "ACT/360") == pytest.approx(58/360)

    def test_act_360_0(self):
        #test that gives 0 for same day
        assert year_fraction_computation(date(2026,1,1), date(2026,1,1), "ACT/360") == 0

    def test_act_365_basic(self):
        #01/01/2026 -> 31/01/2026 is 30 days
        assert year_fraction_computation(date(2026,1,1), date(2026,1,31), "ACT/365") == pytest.approx(30/365)

    def test_act_365_basic2(self):
        #01/01/2026 -> 28/02/2026 is 58 days
        assert year_fraction_computation(date(2026,1,1), date(2026,2,28), "ACT/365") == pytest.approx(58/365)

    def test_act_365_0(self):
        #test that gives 0 for same day
        assert year_fraction_computation(date(2026,1,1), date(2026,1,1), "ACT/365") == 0

    def test_30E_360_basic(self):
        #01/01/2026 -> 21/01/2026 is 20 days
        #using the formula gives (360(2026-2026)+30(1-1)+(21-1))/360=20/360
        assert year_fraction_computation(date(2026,1,1), date(2026,1,31), "30E/360") == pytest.approx(20/360)

    def test_30E_360_basic(self):
        #01/01/2026 -> 21/01/2026 is 20 days
        #using the formula gives (360(2026-2026)+30(1-1)+(21-1))/360=20/360
        assert year_fraction_computation(date(2026,1,1), date(2026,1,21), "30E/360") == pytest.approx(20/360)

    def test_30E_360_end_day_31(self):
        #01/01/2026 -> 31/01/2026 is 30 days but 29 when adjusted for 30E/360
        #using the formula gives (360(2026-2026)+30(1-1)+(30-1))/360=29/360
        assert year_fraction_computation(date(2026,1,1), date(2026,1,31), "30E/360") == pytest.approx(29/360)

    def test_30E_360_start_day_31(self):
        #31/01/2026 -> 28/02/2026 is still 28 days when adjusted for 30E/360
        #using the formula gives (360(2026-2026)+30(2-1)+(28-30))/360=28/360
        assert year_fraction_computation(date(2026,1,31), date(2026,2,28), "30E/360") == pytest.approx(28/360)

    def test_30E_360_0(self):
        #test that gives 0 for same day
        assert year_fraction_computation(date(2026,1,1), date(2026,1,1), "30E/360") == 0