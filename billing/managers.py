from django.db import IntegrityError
from django.db import models
from django.utils import timezone
from billing.models import Coupon


class CouponManager(models.Manager):
    def create_coupon(self, type, value, user=None, valid_until=None, prefix="", campaign=None):
        coupon = self.create(
            value=value,
            code=Coupon.generate_code(prefix),
            type=type,
            user=user,
            valid_until=valid_until,
            campaign=campaign,
        )
        try:
            coupon.save()
        except IntegrityError:
            # Try again with other code
            return Coupon.objects.create_coupon(type, value, user, valid_until, prefix, campaign)
        else:
            return coupon

    def expired(self):
        return self.filter(valid_until__lt=timezone.now())