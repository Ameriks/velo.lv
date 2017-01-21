import requests

from django.core.files.base import ContentFile
from django.db import migrations
from velo.payment.models import Invoice, Payment, ActivePaymentChannel
from velo.registration.models import Application


def ImportErekinsApplicationInvoices(apps, schema_editor):

    bill_payment = Application.objects.exclude(external_invoice_code='').filter(created__year=2016).order_by('-id')

    for bill in bill_payment:
        bill_url = 'https://www.e-rekins.lv/d/i/%s/' % bill.external_invoice_code
        if not bill.external_invoice_code:
            continue
        invoice_name = bill.external_invoice_nr.split(" ")
        series = invoice_name[0]
        number = invoice_name[-1]

        request = requests.get(bill_url)
        if request.status_code != requests.codes.ok:
            raise ValueError('Wasn\'t able to download invoice from e-rekins' )

        bill_params = bill.params
        if bill_params:
            active_payment_type = ActivePaymentChannel.objects.filter(id=bill_params.get("payment_type")).get()
        else:
            try:
                active_payment_type = ActivePaymentChannel.objects.filter(competition_id=bill.competition_id, payment_channel_id=1).get()
            except:
                continue

        payment_set = Payment.objects.create(
            content_object=bill,
            channel=active_payment_type,
            total=bill.final_price,
            status=bill.payment_status,
        )

        invoice_object = Invoice.objects.create(
            competition=bill.competition,
            company_name=bill.company_name,
            company_vat=bill.company_vat,
            company_regnr=bill.company_regnr,
            company_address=bill.company_address,
            company_juridical_address=bill.company_juridical_address,
            email=bill.email,
            invoice_show_names=bill.invoice_show_names,
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
        ('registration', '0004_application_invoice'),
    ]

    operations = [
        migrations.RunPython(ImportErekinsApplicationInvoices),
    ]
