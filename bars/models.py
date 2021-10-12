import os
import logging
import datetime
from django.db import models
from django.utils import timezone
from bars.validators import validate_zip_code
from djrichtextfield.models import RichTextField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Game(models.Model):
    name = models.CharField(unique=True, max_length=100, blank=False)
    image = models.ImageField(upload_to="bars/images/games", blank=True)

    def __str__(self):
        return self.name


class AbstractPageModel(models.Model):
    name = models.CharField(max_length=100)
    header_image = models.ImageField(upload_to="bars/images")
    description = models.CharField(max_length=350)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        try:
            os.remove(self.header_image.path)
        except OSError as e:
            logging.error(f"Image deletion failed: {e}")
        super(AbstractPageModel, self).delete(using=using, keep_parents=keep_parents)

    def __str__(self):
        return self.name

    @property
    def published_recently(self):
        return self.date_added >= timezone.now() - datetime.timedelta(days=1)


class Bar(AbstractPageModel):
    header_image = models.ImageField(upload_to="bars/images/bars")

    email = models.EmailField(blank=True)
    has_table_games = models.BooleanField(default=False)
    has_video_games = models.BooleanField(default=False)
    games = models.ManyToManyField(Game, related_name="bars")

    def clean(self):
        if not (self.has_video_games or self.has_table_games):
            # Un Bar doit avoir des jeux de société ou des jeux vidéos.
            raise ValidationError(_('A bar should at least have table games or video games'))
        super(Bar, self).clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Bar, self).save(*args, **kwargs)

    @property
    def schedule(self):
        """Outputs text version of the weekly schedule"""
        week_schedules = sorted(self.daily_schedules.all(), key=lambda s: s.opens)
        week_schedules_str = []

        for day in Schedule.Weekdays:
            day_schedules = [s.from_to_str for s in week_schedules if s.day == day]
            day_schedules_str = ", ".join(day_schedules) if day_schedules else _("closed")
            week_schedules_str.append(f'{Schedule.Weekdays(day)}: {day_schedules_str}')

        return '\n'.join(week_schedules_str)


class Address(models.Model):
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=25, blank=True)

    zip_code = models.PositiveSmallIntegerField(validators=[validate_zip_code])
    city = models.CharField(max_length=50)

    bar = models.OneToOneField(
        Bar,
        on_delete=models.CASCADE,
        related_name="address",
    )

    @property
    def full_address(self):
        if self.address_line_2:
            return "\n".join([self.address_line_1, self.address_line_2])
        return self.address_line_1

    def __str__(self):
        return "\n".join([self.full_address, f"{self.zip_code} {self.city}"])


class Schedule(models.Model):
    """
    Represents opening hours of a bar for a single day.
    It is possible to define opening hours past midnight.
    """

    OVERLAPPING_HOURS_ERROR_MESSAGE = _('Overlapping opening hours')
    SAME_TIME_OPEN_CLOSE_ERROR_MESSAGE = _('Cannot open and close at the same time')

    DISPLAY_TIME_FORMATTING = "minutes"

    class Weekdays(models.IntegerChoices):
        MONDAY = 0
        TUESDAY = 1
        WEDNESDAY = 2
        THURSDAY = 3
        FRIDAY = 4
        SATURDAY = 5
        SUNDAY = 6

        @property
        def yesterday(self):
            return Schedule.Weekdays((self.value - 1) % 7)

        @property
        def tomorrow(self):
            return Schedule.Weekdays((self.value + 1) % 7)

        def __str__(self):
            return self.label

    day = models.IntegerField(choices=Weekdays.choices)
    opens = models.TimeField()
    closes = models.TimeField()

    bar = models.ForeignKey(Bar, on_delete=models.CASCADE, related_name="daily_schedules")

    def clean(self):
        """
        Make sure the time interval is not overlapping with other days
        (because opening hours after midnight are allowed)
        """
        if not (isinstance(self.opens, datetime.time) and isinstance(self.closes, datetime.time)):
            return super(Schedule, self).clean()

        if self.opens == self.closes:
            raise ValidationError(self.SAME_TIME_OPEN_CLOSE_ERROR_MESSAGE)

        yesterday_schedule, today_schedule, tomorrow_schedule = self.yesterday_today_tomorrow_schedule()

        # if this shift is not a new shift, but a modified one (already stored in the database),
        # we need to replace it in `today_schedule`
        modified_shift_index = next((i for i in range(len(today_schedule)) if today_schedule[i].pk == self.pk), None)
        if modified_shift_index is not None:
            today_schedule[modified_shift_index] = self
        else:
            today_schedule.append(self)

        yesterday_schedule.sort(key=lambda s: s.opens)
        today_schedule.sort(key=lambda s: s.opens)

        # Check if yesterday opening hours after midnight overlap with this morning opening hours
        if yesterday_schedule and today_schedule and \
                yesterday_schedule[-1].opens >= yesterday_schedule[-1].closes:
            # check if the last shift ends after midnight
            if yesterday_schedule[-1].closes > today_schedule[0].opens:
                raise ValidationError(self.OVERLAPPING_HOURS_ERROR_MESSAGE)

        # Check if today hours overlap
        if len(today_schedule) > 1:
            for i in range(len(today_schedule) - 1):
                if today_schedule[i].closes > today_schedule[i + 1].opens:
                    raise ValidationError(self.OVERLAPPING_HOURS_ERROR_MESSAGE)

        # Check if today hours after midnight overlap with tomorrow morning hours
        if today_schedule and tomorrow_schedule and \
                today_schedule[-1].opens >= today_schedule[-1].closes:
            # today, the bar closes after midnight
            tomorrow_schedule.sort(key=lambda s: s.opens)
            if today_schedule[-1].closes > tomorrow_schedule[0].opens:
                raise ValidationError(self.OVERLAPPING_HOURS_ERROR_MESSAGE)

        super(Schedule, self).clean()

    def yesterday_today_tomorrow_schedule(self):
        """
        returns a tuple of QuerySets (opening hours for yesterday, today and tomorrow).
        QuerySets are sorted by their opening hour
        """
        return (
            list(Schedule.objects.filter(bar=self.bar, day=day)) for day in
            (
                self.Weekdays(self.day).yesterday.value,
                self.day,
                self.Weekdays(self.day).tomorrow.value
            )
        )

    def save(self, *args, **kwargs):
        self.clean()
        super(Schedule, self).save(*args, **kwargs)

    def is_open(self) -> bool:
        pass

    def __str__(self):
        return f"{self.Weekdays(self.day).label}: " \
               f"{self.opens.isoformat(self.DISPLAY_TIME_FORMATTING)} - {self.closes.isoformat(self.DISPLAY_TIME_FORMATTING)}"

    @property
    def from_to_str(self):
        return f"{self.opens.isoformat(self.DISPLAY_TIME_FORMATTING)} - {self.closes.isoformat(self.DISPLAY_TIME_FORMATTING)}"


class Event(AbstractPageModel):
    header_image = models.ImageField(upload_to="bars/images/events")

    bar = models.ForeignKey(Bar, on_delete=models.CASCADE)
    date = models.DateTimeField()
    article = RichTextField()
