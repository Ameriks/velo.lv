# coding=utf-8
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from pwgen import pwgen
from payment.models import DiscountCode


class Command(BaseCommand):
    def handle(self, *args, **options):
        campaign_id = args[0]
        count = args[1]

        if not campaign_id or not count:
            return 'ERROR'

        codes = pwgen(8, int(count), no_symbols=True, no_capitalize=True, no_ambiguous=True)

        for code in codes:
            code = code.upper()
            try:
                DiscountCode.objects.create(campaign_id=campaign_id, code=code)
            except:
                print 'Error creating discount code - %s' % code