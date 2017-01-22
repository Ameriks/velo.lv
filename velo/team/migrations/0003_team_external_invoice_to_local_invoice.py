import requests
from django.contrib.contenttypes.models import ContentType

from django.core.files.base import ContentFile
from django.db import migrations

from velo.core.models import Distance
from velo.payment.models import Invoice, Payment, ActivePaymentChannel
from velo.team.models import Team


def import_erekins_invoices(apps, schema_editor):
    teams = Team.objects.exclude(external_invoice_code='')

    for team in teams:
        bill_url = 'https://www.e-rekins.lv/d/i/%s/' % team.external_invoice_code

        invoice_name = team.external_invoice_nr.split(" ")
        series = invoice_name[0]
        number = invoice_name[-1]

        request = requests.get(bill_url)
        if request.status_code != requests.codes.ok:
            raise ValueError('Wasn\'t able to download invoice from e-rekins' )

        distance = Distance.objects.filter(id=team.distance_id).get()

        try:
            active_payment_type = ActivePaymentChannel.objects.filter(competition_id=distance.competition.id, payment_channel_id=1)[0]
        except:
            continue

        content_type = ContentType.objects.get_for_model(team)
        payment, created = Payment.objects.get_or_create(
            content_type=content_type,
            object_id=team.id,
            total=team.final_price,
            defaults={"status": Payment.STATUSES.ok if team.is_featured else Payment.STATUSES.new}
        )
        invoice_object = Invoice.objects.create(
            competition=team.competition,
            company_name=team.company_name,
            company_vat=team.company_vat,
            company_regnr=team.company_regnr,
            company_address=team.company_address,
            company_juridical_address=team.company_juridical_address,
            email=team.email,
            invoice_show_names=False,
            file=ContentFile(request.content, '%s-%03d.pdf' % (series, int(number))),
            series=series,
            number=number,
            payment=payment,
            channel=active_payment_type.payment_channel,
        )

        team.invoice = invoice_object
        team.save()


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_auto_20170106_2012'),
        ('team', '0002_team_invoice'),
    ]

    operations = [
        migrations.RunPython(import_erekins_invoices),
    ]
