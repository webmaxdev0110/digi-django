from __future__ import unicode_literals
import random
from django.contrib.postgres.fields import ArrayField
from django.db import models
# Create your models here.
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from accounts.models import User
from core.models import TimeStampedModel
import string


_recurrence_unit_days = {
    'D': 1.,
    'W': 7.,
    'M': 30.4368,                      # http://en.wikipedia.org/wiki/Month#Julian_and_Gregorian_calendars
    'Y': 365.2425,                     # http://en.wikipedia.org/wiki/Year#Calendar_year
    }

TIME_UNIT_CHOICES = (
    ('D', _('Day')),
    ('W', _('Week')),
    ('M', _('Month')),
    ('Y', _('Year')),
)


class Plan(models.Model):
    name = models.CharField(max_length=24)
    price_cents = models.IntegerField()
    recurring_type = models.CharField(max_length=1, choices=TIME_UNIT_CHOICES, default='M')
    feature_flags = ArrayField(models.CharField(max_length=32), blank=True)
    is_live = models.BooleanField(default=False)
    min_required_user = models.SmallIntegerField(default=0)
    max_required_user = models.SmallIntegerField(default=1, null=True)
    trial_days = models.SmallIntegerField(default=0, null=True)

    def __unicode__(self):
        return '<Plan: {0}>'.format(self.name)

COUPON_TYPES = (
    ('m', 'Money based coupon'),
    ('p', 'Percentage discount'),
)

class Coupon(TimeStampedModel):
    type = models.CharField(choices=COUPON_TYPES, max_length=1)
    code = models.CharField(
        _("Code"), max_length=30, unique=True, blank=True,
        help_text=_("Leaving this field empty will generate a random code."))
    valid_until = models.DateTimeField(
        _("Valid until"), blank=True, null=True,
        help_text=_("Leave empty for coupons that never expire"))
    single_user_reusable = models.BooleanField(models.BooleanField, default=False)
    target_plans = models.ManyToManyField(Plan, blank=True, help_text=_('Leaving empty will make this '
                                                                       'coupon valid for all plans'))
    class Meta:
        ordering = ['created']
        verbose_name = _("Coupon")
        verbose_name_plural = _("Coupons")

    def __unicode__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = Coupon.generate_code()
        super(Coupon, self).save(*args, **kwargs)

    def expired(self):
        return self.valid_until is not None and self.valid_until < timezone.now()


    @classmethod
    def generate_code(cls, prefix=""):
        CODE_LENGTH = 8
        CODE_CHARS = string.ascii_letters + string.digits
        code = "".join(random.choice(CODE_CHARS) for i in range(CODE_LENGTH))
        return prefix + code


class PlanSubscription(models.Model):
    name = models.CharField(max_length=24)
    trial_days = models.SmallIntegerField(default=0)
    user = models.ForeignKey(User)
    price_cents = models.IntegerField()
    start_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    end_date = models.DateTimeField(null=True)
    active = models.BooleanField(default=False)
    user_cancelled = models.BooleanField(default=False)
    system_cancelled = models.BooleanField(default=False)
    coupon = models.ForeignKey(Coupon)
    number_of_users = models.SmallIntegerField(default=1)
    recurring_type = models.CharField(max_length=1, choices=TIME_UNIT_CHOICES)
    recurrence_period = models.PositiveIntegerField(null=True, blank=True)
    next_payment_date = models.DateField(null=True)

    class Meta:
        ordering = ['-start_date', 'user']
        

TRANSACTION_REASON_CHOICES = (
    ('S', _('Subscription charge')),
    ('P', _('Single product purchase')),
)

class Transaction(TimeStampedModel):
    user = models.ForeignKey(User, related_name='balance_changes')
    reason = models.CharField(max_length=1, choices=TRANSACTION_REASON_CHOICES, default='')
    description = models.CharField(max_length=128, blank=True)
    amount_cents = models.DecimalField(_('Amount'), default=0, max_digits=18, decimal_places=6)

    class Meta:
        ordering = ['-created', '-amount_cents']
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")

    def __unicode__(self):
        return '<Transaction: {0} - {1}>'.format(self.user.first_name, self.amount_cents)