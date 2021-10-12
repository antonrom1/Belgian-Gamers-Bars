from datetime import time
from django.test import TestCase
from bars.models import Bar, Schedule
from django.core.exceptions import ValidationError
from django.templatetags.static import static


class AddressTest(TestCase):
    def setUp(self) -> None:
        self.bar = Bar.objects.create(
            name="Bar 1",
            description="Bar description 1",
            header_image=static('images/generic_header.png'),
            has_table_games=True
        )

    def test_normal_schedules_dont_overlap(self):
        schedules = [
            (time(hour=9), time(hour=12, minute=30), Schedule.Weekdays.MONDAY),
            (time(hour=19), time(hour=3), Schedule.Weekdays.MONDAY),
            (time(hour=3), time(hour=4, minute=30), Schedule.Weekdays.TUESDAY),
            (time(hour=5), time(hour=19, minute=30), Schedule.Weekdays.TUESDAY),
        ]

        for opens, closes, day in schedules:
            Schedule.objects.create(bar=self.bar, opens=opens, closes=closes, day=day)

    def test_overlapping_schedules_overlap(self):
        invalid_schedules = [
            [
                (time(hour=9), time(hour=12, minute=30), Schedule.Weekdays.MONDAY),
                (time(hour=19), time(hour=2, minute=15), Schedule.Weekdays.MONDAY),
                (time(hour=5), time(hour=19, minute=30), Schedule.Weekdays.TUESDAY),
                (time(hour=2), time(hour=4, minute=30), Schedule.Weekdays.TUESDAY),
            ],
            [
                (time(hour=9), time(hour=12, minute=30), Schedule.Weekdays.MONDAY),
                (time(hour=19), time(hour=2, minute=30), Schedule.Weekdays.MONDAY),
                (time(hour=5), time(hour=19, minute=30), Schedule.Weekdays.TUESDAY),
                (time(hour=2, minute=15), time(hour=4, minute=30), Schedule.Weekdays.TUESDAY),
            ],
            [
                (time(hour=12), time(hour=19, minute=30), Schedule.Weekdays.MONDAY),
                (time(hour=12), time(hour=19, minute=30), Schedule.Weekdays.TUESDAY),
                (time(hour=7), time(hour=12, minute=30), Schedule.Weekdays.WEDNESDAY),
                (time(hour=12), time(hour=19), Schedule.Weekdays.WEDNESDAY),
            ]
        ]

        self._test_invalid_schedules_list(invalid_schedules, ValidationError)

    def test_invalid_hours(self):
        invalid_schedules = [
            [
                (time(hour=9), time(hour=12, minute=30), Schedule.Weekdays.MONDAY),
                (time(hour=19), time(hour=2, minute=15), Schedule.Weekdays.MONDAY),
                (time(hour=5), time(hour=19, minute=30), Schedule.Weekdays.TUESDAY),
                (time(hour=0), time(hour=0), Schedule.Weekdays.WEDNESDAY),
            ],
        ]

        self._test_invalid_schedules_list(invalid_schedules, ValidationError)

    #

    def _test_invalid_schedules_list(self, invalid_schedules, expected_exception):
        for schedules in invalid_schedules:
            Schedule.objects.all().delete()
            for i, (opens, closes, day) in enumerate(schedules):
                if i + 1 == len(schedules):
                    # the last schedule should overlap with other schedules
                    self.assertRaises(
                        expected_exception,
                        Schedule.objects.create,
                        bar=self.bar, opens=opens, closes=closes, day=day
                    )

                else:
                    Schedule.objects.create(bar=self.bar, opens=opens, closes=closes, day=day)
