from oscar.apps.partner.abstract_models import AbstractPartner
from oscar.apps.basket.models import * 
from django.db import models


class EmptyBasket(AbstractPartner):
	def flush(self):
        """
        Remove all lines from basket.
        """
        if self.status == self.FROZEN:
            raise PermissionDenied("A frozen basket cannot be flushed")
        self.lines.all().delete()
        self._lines = None

