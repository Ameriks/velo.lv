import datetime

from test_plus.test import TestCase
from velo.core.models import Competition, Distance, User
from velo.payment.models import PaymentChannel, ActivePaymentChannel, Price
import pytz


class BaseTransactionTestCase(TestCase):
    def setUp(self):
        time_now = datetime.datetime.now(pytz.timezone("Europe/Riga"))

        self.payment_ch = PaymentChannel.objects.create(is_bill=True,  title='Get Bill')

        self.competition_parent = Competition.objects.create(
            name='Test Ride',
            short_name='Test',
            bill_series='TR - 17',
            kind=0,
            place_name='',
            complex_discount=15,
            payment_channel='LKDF',
            params={},
            competition_date=time_now + datetime.timedelta(days=56),
            complex_payment_enddate=time_now + datetime.timedelta(days=28),
            id=1,
            level=1
        )
        self.competition = Competition.objects.create(
            name='Test Ride 2017',
            short_name='Test 2017',
            bill_series='TR - 17',
            kind=0,
            place_name='Riga',
            complex_discount=0,
            payment_channel='LKDF',
            params={},
            competition_date=time_now + datetime.timedelta(days=56),
            id=2,
            parent=self.competition_parent,
            parent_id=1,
            level=2
        )

        self.distance1 = Distance.objects.create(competition=self.competition, name="Test Distance", profile_price=20.00, kind='T')
        till_date = time_now + datetime.timedelta(days=1)

        self.active_payment_ch = ActivePaymentChannel.objects.create(payment_channel=self.payment_ch, competition=self.competition, from_date=time_now, till_date=till_date)

        price_start_date = time_now - datetime.timedelta(days=7)

        self.price1 = Price.objects.create(competition=self.competition, distance=self.distance1, price=20.17, start_registering=price_start_date, end_registering=till_date)


class TestApplyingToCompetition(BaseTransactionTestCase):
    def test_creation(self):
        response_initialise = self.get('application', pick=self.competition.id, follow=True)
        self.response_200(response_initialise)
        application_code = self.last_response._request.resolver_match.kwargs.get('slug')
        url_application_init = self.reverse('application', slug=application_code)
        self.assertEquals(url_application_init, response_initialise._request.path)

        post_registration_data = {
            'email': 'keriks@testmail.com',
            'email2': 'keriks@testmail.com',
            'participant_set-TOTAL_FORMS': '1',
            'participant_set-INITIAL_FORMS': '0',
            'participant_set-MIN_NUM_FORMS': '0',
            'participant_set-MAX_NUM_FORMS': '1000',
            'participant_set-0-id': '',
            'participant_set-0-DELETE': '',
            'participant_set-0-distance': self.distance1.id,
            'participant_set-0-first_name': 'User',
            'participant_set-0-last_name': 'Tester',
            'participant_set-0-gender': 'M',
            'participant_set-0-birthday_year': '2017',
            'participant_set-0-birthday_month': '2',
            'participant_set-0-birthday_day': '06',
            'participant_set-0-country': 'LV',
            'participant_set-0-email': '',
            'participant_set-0-phone_number': '',
            'participant_set-0-team_name': '',
            'participant_set-0-bike_brand2': '',
            'participant_set-0-insurance': '',
            'participant_set-0-ssn': ''
        }
        response_create = self.post('application', slug=application_code, data=post_registration_data, follow=True)
        self.response_200(response_create)
        url_application_pay = self.reverse('application_pay', slug=application_code)
        self.assertEquals(url_application_pay, response_create._request.path)

        post_payment_data = {
            'donation': 0,
            'accept_terms': 'on',
            'accept_inform_participants': 'on',
            'accept_insurance': '',
            'sport_approval': 'on',
            'payment_type': self.active_payment_ch.id,
            'company_name': 'Company+Name+required',
            'company_vat': '',
            'company_regnr': '123456789',
            'company_address': 'Address',
            'company_juridical_address': 'Juridical+Address'
        }
        response_pay = self.post('application_pay', slug=application_code, data=post_payment_data, follow=True)
        self.response_200(response_pay)
        url_application_ok = self.reverse('application_ok', slug=application_code)
        self.assertEquals(url_application_ok, response_pay._request.path)
