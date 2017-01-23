import requests
from django.contrib.contenttypes.models import ContentType

from django.core.files.base import ContentFile
from django.db import migrations
from velo.payment.models import Invoice, Payment, ActivePaymentChannel
from velo.registration.models import Application


def import_erekins_invoices(apps, schema_editor):

    applications = Application.objects.exclude(external_invoice_code='').filter(created__year__gte=2016).order_by('-id')

    for application in applications:
        bill_url = 'https://www.e-rekins.lv/d/i/%s/' % application.external_invoice_code
        if not application.external_invoice_code:
            continue
        invoice_name = application.external_invoice_nr.split(" ")
        series = invoice_name[0]
        number = invoice_name[-1]

        request = requests.get(bill_url)
        if request.status_code != requests.codes.ok:
            raise ValueError('Wasn\'t able to download invoice from e-rekins' )

        bill_params = application.params
        if bill_params:
            active_payment_type = ActivePaymentChannel.objects.filter(id=bill_params.get("payment_type")).get()
        else:
            try:
                active_payment_type = ActivePaymentChannel.objects.filter(competition_id=application.competition_id, payment_channel_id=1)[0]
            except:
                continue

        content_type = ContentType.objects.get_for_model(application)
        try:
            payment, created = Payment.objects.get_or_create(
                content_type=content_type,
                object_id=application.id,
                total=application.final_price,
                donation=application.donation,
                defaults={"status": application.payment_status}
            )
        except Payment.MultipleObjectsReturned:
            payment = Payment.objects.filter(content_type=content_type,
                object_id=application.id,
                total=application.final_price,
                donation=application.donation,)[0]

        invoice_object = Invoice.objects.create(
            competition=application.competition,
            company_name=application.company_name,
            company_vat=application.company_vat,
            company_regnr=application.company_regnr,
            company_address=application.company_address,
            company_juridical_address=application.company_juridical_address,
            email=application.email,
            invoice_show_names=application.invoice_show_names,
            file=ContentFile(request.content, '%s-%03d.pdf' % (series, int(number))),
            series=series,
            number=number,
            payment=payment,
            channel=active_payment_type.payment_channel,
        )

        application.invoice = invoice_object
        application.save()


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_auto_20161227_1441'),
        ('registration', '0004_application_invoice'),
    ]

    operations = [
        migrations.RunPython(import_erekins_invoices),
    ]
