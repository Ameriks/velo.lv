import requests

from django.core.files.base import ContentFile
from django.db import migrations

from velo.core.models import Distance
from velo.payment.models import Invoice, Payment, ActivePaymentChannel
from velo.team.models import Team

def ImportErekinsTeamInvoices(apps, schema_editor):
    bill_payment = Team.objects.exclude(external_invoice_code='')

    for bill in bill_payment:
        bill_url = 'https://www.e-rekins.lv/d/i/%s/' % bill.external_invoice_code

        invoice_name = bill.external_invoice_nr.split(" ")
        series = invoice_name[0]
        number = invoice_name[-1]

        request = requests.get(bill_url)
        if request.status_code != requests.codes.ok:
            raise ValueError('Wasn\'t able to download invoice from e-rekins' )

        distance = Distance.objects.filter(id=bill.distance_id).get()

        try:
            active_payment_type = ActivePaymentChannel.objects.filter(competition_id=distance.competition.id, payment_channel_id=1).get()
        except:
            continue

        payment_set = Payment.objects.create(
            content_object=bill,
            channel=active_payment_type,
            total=bill.final_price,
            status=30 if bill.is_featured else 10,
        )

        invoice_object = Invoice.objects.create(
            competition=bill.competition,
            company_name=bill.company_name,
            company_vat=bill.company_vat,
            company_regnr=bill.company_regnr,
            company_address=bill.company_address,
            company_juridical_address=bill.company_juridical_address,
            email=bill.email,
            invoice_show_names=False,
            file=ContentFile(request.content, '%s-%03d.pdf' % (series, int(number))),
            series=series,
            number=number,
            payment_set=payment_set
        )

        bill.invoice = invoice_object
        bill.save()

class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_auto_20161227_1441'),
        ('team', '0002_team_invoice'),
    ]

    operations = [
        migrations.RunPython(ImportErekinsTeamInvoices),
    ]
