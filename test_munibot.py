from datetime import datetime
import unittest

import munibot


class TestBotShouldBeActive(unittest.TestCase):
    def test_weekday_within_interval_is_active(self):
        for i in range(5):
            dt_5p = datetime(2016, 11, 7 + i, 17, 0, 0, 0)
            self.assertTrue(munibot.bot_should_be_active(dt_5p))
            dt_6p = datetime(2016, 11, 7 + i, 18, 0, 0, 0)
            self.assertTrue(munibot.bot_should_be_active(dt_6p))
            dt_7p = datetime(2016, 11, 7 + i, 19, 0, 0, 0)
            self.assertTrue(munibot.bot_should_be_active(dt_7p))

    def test_weekday_at_8pm_is_inactive(self):
        for i in range(5):
            dt_8p = datetime(2016, 11, 7 + i, 20, 0, 0, 0)
            self.assertFalse(munibot.bot_should_be_active(dt_8p))

    def test_weekday_before_start_time_is_inactive(self):
        for i in range(5):
            dt_4p = datetime(2016, 11, 7 + i, 16, 0, 0, 0)
            self.assertFalse(munibot.bot_should_be_active(dt_4p))

    def test_weekend_within_active_times_is_inactive(self):
            sat_dt_6p = datetime(2016, 11, 5, 18, 0, 0, 0)
            self.assertFalse(munibot.bot_should_be_active(sat_dt_6p))
            sun_dt_6p = datetime(2016, 11, 6, 18, 0, 0, 0)
            self.assertFalse(munibot.bot_should_be_active(sun_dt_6p))


class TestSecsTilActive(unittest.TestCase):
    def test_saturday_before_start_hour(self):
        # Saturday, Nov 5, 2016 at 3:55:35pm
        dt = datetime(2016, 11, 5, 15, 55, 35, 886983)
        self.assertEqual(munibot.secs_til_active(dt), 176664)

    def test_saturday_after_end_hour(self):
        # Saturday, Nov 5, 2016 at 11:00pm
        dt = datetime(2016, 11, 5, 23, 0, 0, 0)
        self.assertEqual(munibot.secs_til_active(dt), 151200)

    def test_sunday_before_start_hour(self):
        # Sunday, Nov 6, 2016 at 1:23pm
        dt = datetime(2016, 11, 6, 13, 23, 0, 0)
        self.assertEqual(munibot.secs_til_active(dt), 99420)

    def test_sunday_after_end_hour(self):
        # Sunday, Nov 6, 2016 at 10pm
        dt = datetime(2016, 11, 6, 22, 0, 0, 0)
        self.assertEqual(munibot.secs_til_active(dt), 68400)

    def test_weekday_before_start_time(self):
        for i in range(5):
            # M-F in the week of Nov 7, 2016 at 10am
            dt = datetime(2016, 11, 7 + i, 10, 0, 0, 0)
            self.assertEqual(munibot.secs_til_active(dt), 25200)

    def test_mon_to_thurs_after_end_time(self):
        for i in range(4):
            # M-Th in the week of Nov 7, 2016 at 9pm
            dt = datetime(2016, 11, 7 + i, 21, 0, 0, 0)
            self.assertEqual(munibot.secs_til_active(dt), 72000)

    def test_fri_after_end_time(self):
        # Friday, Nov 11, 2016 at 9:30pm
        dt = datetime(2016, 11, 11, 21, 30, 0, 0)
        self.assertEqual(munibot.secs_til_active(dt), 243000)

    def test_across_months(self):
        # Wednesday, Nov 30, 2016 at 9pm
        dt = datetime(2016, 11, 30, 21, 0, 0, 0)
        self.assertEqual(munibot.secs_til_active(dt), 72000)

    def test_across_year(self):
        # Saturday, Dec 31, 2016 at 2am
        dt = datetime(2016, 12, 31, 2, 0, 0, 0)
        self.assertEqual(munibot.secs_til_active(dt), 226800)
