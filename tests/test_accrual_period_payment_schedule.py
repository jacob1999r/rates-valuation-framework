from datetime import date
import pytest
from derivative_valuations.payment_schedule.accrual_period_payment_schedule import generate_schedule

class TestGenerateSchedule:
    def test_end_date_before_start_date(self):
        with pytest.raises(ValueError, match="End date must be after start date!"):
            generate_schedule(date(1999,11,23), date(1999,2,23), 1)

    def test_payment_frequency_0(self):
        with pytest.raises(ValueError, match="Payment frequency must be greater than 0."):
            generate_schedule(date(2026,1,1), date(2026, 4, 1), 0)

    def test_payment_frequency_negative(self):
        with pytest.raises(ValueError, match="Payment frequency must be greater than 0."):
            generate_schedule(date(2026,1,1), date(2026, 4, 1), -1)

    def test_payment_frequency_greater_than_months(self):
        with pytest.raises(ValueError, match="The frequency of payments cannot be greater than the number of months between the start date and the end date."):
            generate_schedule(date(2026,1,1), date(2026, 4, 1), 6)
    
    def test_basic_schedule(self):
        assert generate_schedule(date(2026, 1, 1),date(2026, 4, 1), 1) == [
        (date(2026,1,1), date(2026,2,1), date(2026,2,1)),
        (date(2026,2,1), date(2026,3,1), date(2026,3,1)),
        (date(2026,3,1), date(2026,4,1), date(2026,4,1))]

    def test_basic_schedule2(self):
        assert generate_schedule(date(2026, 1, 1),date(2027, 1, 1), 4) == [
        (date(2026,1,1), date(2026,5,1), date(2026,5,1)),
        (date(2026,5,1), date(2026,9,1), date(2026,9,1)),
        (date(2026,9,1), date(2027,1,1), date(2027,1,1))]

    def test_advanced_schedule_with_stub(self):
        assert generate_schedule(date(2026, 1, 1),date(2027, 7, 1), 4) == [
        (date(2026,1,1), date(2026,5,1), date(2026,5,1)),
        (date(2026,5,1), date(2026,9,1), date(2026,9,1)),
        (date(2026,9,1), date(2027,1,1), date(2027,1,1)),
        (date(2027,1,1), date(2027,5,1), date(2027,5,1)),
        (date(2027,5,1), date(2027,7,1), date(2027,7,1))]