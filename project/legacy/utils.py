# coding=utf-8
from __future__ import unicode_literals

# This is migration script from www.velo.lv to mans.velo.lv.
# Migration was online, so that in migration beginning participants could register in both sites - www.velo.lv and
# mans.velo.lv.
import csv

from django.core.files.base import ContentFile
import hashlib
import pytz
import requests
from StringIO import StringIO
from legacy.models import Ev68RUsers, Ev68RVeloCompetitions, Ev68RVeloDistance, Ev68RVeloPrice, Ev68RVeloInsurance, \
    Ev68RVeloApplications, Ev68RVeloParticipations, Ev68RVeloResultsSebTotal, Ev68RVeloTeams, Ev68RVeloResults, \
    Ev68RVeloPayments, Ev68RVeloCouponCodes
from core.models import User, Choices, Competition, Distance, Insurance, CustomSlug
from Crypto.Cipher import AES
from django.conf import settings
from social.apps.django_app.default.models import UserSocialAuth
from manager.models import TempDocument

from payment.models import Price, DiscountCode, Payment, DiscountCampaign
from registration.models import Application, Participant
from results.models import LegacySEBStandingsResult, LegacyResult, HelperResults
from team.models import Team, Member, MemberApplication
import os
riga_tz = pytz.timezone("Europe/Riga")
legacy_password = hashlib.md5(settings.LEGACY_KEY).hexdigest()
legacy_encrypt = AES.new(legacy_password, AES.MODE_ECB)

COUNTRY_MAP = {
    'Belgium': 'BE',
    'Bulgaria': 'BG',
    'Cambodia': 'KH',
    'Estonia': 'EE',
    'Germany': 'DE',
    'Indonesia': 'ID',
    'Iran': 'IR',
    'Latvia': 'LV',
    'Lebanon': 'LB',
    'Lithuania': 'LT',
    'Netherlands': 'NL',
    'Russian Federation': 'RU',
    'Saint Helena': 'SH',
    'United Kingdom': 'UK',
    'United States': 'US',
}


def create_choices():
    cities = ('Ādaži',
            'Ādažu novads',
            'Aglonas novads',
            'Ainaži',
            'Aizkraukle',
            'Aizkraukles novads',
            'Aizpute',
            'Aizputes novads',
            'Aknīste',
            'Aknīstes novads',
            'Aloja',
            'Alojas novads',
            'Alsungas novads',
            'Alūksne',
            'Alūksnes novads',
            'Amatas novads',
            'Ape',
            'Apes novads',
            'Auce',
            'Auces novads',
            'Babītes novads',
            'Baldone',
            'Baldones novads',
            'Baloži',
            'Baltinavas novads',
            'Balvi',
            'Balvu novads',
            'Bauska',
            'Bauskas novads',
            'Beverīnas novads',
            'Brocēni',
            'Brocēnu novads',
            'Burtnieku novads',
            'Carnikava ',
            'Carnikavas novads',
            'Cēsis',
            'Cēsu novads',
            'Cesvaine',
            'Cesvaines novads',
            'Ciblas novads',
            'Dagda',
            'Dagdas novads',
            'Daugavpils',
            'Daugavpils novads',
            'Dobele',
            'Dobeles novads',
            'Dundagas novads',
            'Durbe',
            'Durbes novads',
            'Engures novads',
            'Ērgļi',
            'Ērgļu novads',
            'Garkalnes novads',
            'Grobiņa',
            'Grobiņas novads',
            'Gulbene',
            'Gulbenes novads',
            'Iecavas novads',
            'Ikšķile',
            'Ikšķiles novads',
            'Ilūkste',
            'Ilūkstes novads',
            'Inčukalna novads',
            'Jaunjelgava',
            'Jaunjelgavas novads',
            'Jaunpiebalga',
            'Jaunpiebalgas novads',
            'Jaunpils novads',
            'Jēkabpils',
            'Jēkabpils novads',
            'Jelgava',
            'Jelgavas novads',
            'Jūrmala',
            'Kandava',
            'Kandavas novads',
            'Kārsava',
            'Kārsavas novads',
            'Ķeguma novads',
            'Ķegums',
            'Ķekavas novads',
            'Kocēnu novads',
            'Koknese',
            'Kokneses novads',
            'Krāslava',
            'Krāslavas novads',
            'Krimuldas novads',
            'Krustpils',
            'Krustpils novads',
            'Kuldīga',
            'Kuldīgas novads',
            'Lielvārde',
            'Lielvārdes novads',
            'Liepāja',
            'Līgatne',
            'Līgatnes novads',
            'Limbaži',
            'Limbažu novads',
            'Līvāni',
            'Līvānu novads',
            'Lubāna',
            'Lubānas novads',
            'Ludza',
            'Ludzas novads',
            'Madona',
            'Madonas novads',
            'Mālpils',
            'Mālpils novads',
            'Mārupes novads',
            'Mazsalaca',
            'Mazsalacas novads',
            'Mērsraga novads',
            'Naukšēnu novads',
            'Neretas novads',
            'Nīcas novads',
            'Ogre',
            'Ogres novads',
            'Olaine',
            'Olaines novads',
            'Ozolnieku novads',
            'Pārgaujas novads',
            'Pāvilosta',
            'Pāvilostas novads',
            'Pļaviņas',
            'Pļaviņu novads',
            'Preiļi',
            'Preiļu novads',
            'Priekule',
            'Priekules novads',
            'Priekuļu novads',
            'Raunas novads',
            'Rēzekne',
            'Rēzeknes novads',
            'Riebiņu novads',
            'Rīga',
            'Roja',
            'Rojas novads',
            'Ropaži',
            'Ropažu novads',
            'Rucavas novads',
            'Rugāju novads',
            'Rūjiena',
            'Rūjienas novads',
            'Rundāles novads',
            'Sabile',
            'Salacgrīva',
            'Salacgrīvas novads',
            'Salas novads',
            'Salaspils',
            'Salaspils novads',
            'Saldus',
            'Saldus novads',
            'Saulkrasti',
            'Saulkrastu novads',
            'Sējas novads',
            'Sigulda',
            'Siguldas novads',
            'Skrīveru novads',
            'Skrunda',
            'Skrundas novads',
            'Smiltene',
            'Smiltenes novads',
            'Stopiņu novads',
            'Strenču novads',
            'Talsi',
            'Talsu novads',
            'Tērvetes novads',
            'Tukuma novads',
            'Tukums',
            'Vaiņodes novads',
            'Valdemārpils',
            'Valka',
            'Valkas novads',
            'Valmiera',
            'Vangaži',
            'Varakļāni',
            'Varakļānu novads',
            'Vārkavas novads',
            'Vecpiebalga',
            'Vecpiebalgas novads',
            'Vecumnieku novads',
            'Ventspils',
            'Ventspils novads',
            'Viesīte',
            'Viesītes novads',
            'Viļaka',
            'Viļakas novads',
            'Viļāni',
            'Viļānu novads',
            'Zilupe',
            'Zilupes novads',
            )
    bikes = (
        'Author',
        'Bergamont',
        'Cannondale',
        'Corratec',
        'Cube',
        'Dema',
        'Electra',
        'Felt',
        'Flanders',
        'Focus',
        'Fuji',
        'Giant',
        'GT',
        'Hasa',
        'KHS',
        'KTM',
        'Merida',
        'Schwinn',
        'Scott',
        'Specialized',
        'Superior',
        'Trek',
        'Univega',
        'Wheeler',
        'ZZK',
        'Cits',
    )
    wheres = (
        'no TV',
        'no radio',
        'no www.velo.lv',
        'no draugiem',
        'no poligrāfijas materiāliem',
        'citur',
    )
    occupations = (
        'Cita',
        'Finanšu sektors',
        'IT / telekomunikācijas',
        'Izglītība / pētniecība',
        'Konsultācijas',
        'Kultūras joma',
        'Lauksaimniecība / amatniecība',
        'Mārketings / reklāma/ PR',
        'Pakalpojumu sniegšana',
        'Policija / bruņotie spēki',
        'Radošās profesijas',
        'Ražošana',
        'Skolnieks / students',
        'Sporta joma',
        'Valsts / publiskā pārvalde',
        'Veselības / sociālā aprūpe',
    )
    for title in cities:
        Choices.objects.get_or_create(kind=Choices.KIND_CITY, title=title)

    for title in bikes:
        Choices.objects.get_or_create(kind=Choices.KIND_BIKEBRAND, title=title)

    for title in wheres:
        Choices.objects.get_or_create(kind=Choices.KIND_HEARD, title=title)

    for title in occupations:
        Choices.objects.get_or_create(kind=Choices.KIND_OCCUPATION, title=title)


def sync_competitions():
    competitions = Competition.objects.all()
    for competition in competitions:
        old = Ev68RVeloCompetitions.objects.get(id=competition.legacy_id)
        competition.place_name = old.where
        competition.competition_date = riga_tz.normalize(old.competition_date) if old.competition_date else None
        competition.complex_payment_enddate = old.complex_enddate
        competition.complex_discount = old.complex_discount
        competition.bill_series = old.billseries
        competition.payment_channel = old.paymentchannelbig
        competition.save()

def sync_distances():
    distances = Ev68RVeloDistance.objects.all()
    for distance in distances:
        data = {
            'competition': Competition.objects.get(legacy_id=distance.competition_id),
            'name': distance.title_lv_lv,
            'distance_text': distance.km,
        }
        dist, created = Distance.objects.get_or_create(id=distance.id, defaults=data)
        if not created:
            for d in data:
                setattr(dist, d, data.get(d))
            dist.save()


def sync_prices():
    prices = Ev68RVeloPrice.objects.all()
    for obj in prices:
        data = {
            'competition': Competition.objects.get(legacy_id=obj.competition_id),
            'distance': Distance.objects.get(id=obj.distance_id),
            'from_year': obj.from_year,
            'till_year': obj.till_year,
            'price': obj.price,
            'start_registering': riga_tz.normalize(obj.start_registering),
            'end_registering': riga_tz.normalize(obj.end_registering),
        }
        price, created = Price.objects.get_or_create(id=obj.id, defaults=data)
        if not created:
            for d in data:
                setattr(price, d, data.get(d))
            price.save()

def sync_insurance():
    insurances = Ev68RVeloInsurance.objects.all()
    for obj in insurances:
        data = {
            'insurance_company_id': '1' if 'seb.png' in obj.params else '2',
            'competition': Competition.objects.get(legacy_id=obj.competition_id),
            'title': obj.title,
            'price': obj.price,
            'in_complex': obj.complex,
            'complex_discount': obj.complex_discount,
            'status': obj.state,
        }
        insurance, created = Insurance.objects.get_or_create(id=obj.id, defaults=data)
        if not created:
            for d in data:
                setattr(insurance, d, data.get(d))
            insurance.save()

def sync_applications():
    applications = Ev68RVeloApplications.objects.filter(competition_id__gte=37)

    payment_mapping = {
        -1: -10,
        0: 0,
        1: 10,
        2: 20,
    }

    for obj in applications:
        data = {
            'competition': Competition.objects.get(legacy_id=obj.competition_id),
            'payment_status': payment_mapping.get(obj.status),
            'created': riga_tz.normalize(obj.created),
            'created_by': User.objects.get(legacy_id=obj.user_id) if obj.user_id > 0 else None,
        }
        appl, created = Application.objects.get_or_create(legacy_id=obj.id, defaults=data)
        if not created:
            for d in data:
                setattr(appl, d, data.get(d))
            appl.save()


def sync_payments():
    dcampaign, created = DiscountCampaign.objects.get_or_create(id=3, title='SEB 37.5%', competition_id=25)
    payment_channel_mapping = {
        'LKDFSwedbank': 2,
        'LKDFSEB': 3,
        'LKDFcard': 4,
        'LKDFbill': 1,
        'IJSASwedbank': 6,
        'IJSASEB': 7,
        'IJSAcard': 8,
        'IJSAbill': 5,
    }

    applications = Application.objects.exclude(legacy_id=None).filter(final_price=0.00)
    for application in applications:
        legacy_payments = Ev68RVeloPayments.objects.filter(application_id=application.legacy_id).order_by('erekins_status')

        for legacy_payment in legacy_payments:
            application.final_price = legacy_payment.total_lvl
            application.total_entry_fee = legacy_payment.total_person_lvl
            application.total_insurance_fee = legacy_payment.total_insurance_lvl

            if legacy_payment.coupon_id:
                cc = Ev68RVeloCouponCodes.objects.get(id=legacy_payment.coupon_id)
                dc, created = DiscountCode.objects.get_or_create(code=cc.coupon_code, defaults={'usage_times': 1, 'campaign': dcampaign})
                dc.usage_times_left = cc.usage_times_left
                dc.save()
                application.discount_code = dc


            print legacy_payment.id
            payment_defaults = {
                'content_object': application,
                'channel_id': payment_channel_mapping.get('%s%s' % (legacy_payment.paymentchannelbig, legacy_payment.payment_channel)),
                'erekins_code': legacy_payment.code or '',
                'total': legacy_payment.total_lvl,
                'status': legacy_payment.erekins_status or Payment.STATUS_NEW,
            }
           # application.payment_status = legacy_payment.erekins_status
            print payment_defaults
            application.save()
            payment, created = Payment.objects.get_or_create(legacy_id=legacy_payment.id, defaults=payment_defaults)


def sync_participants():
    participants = Ev68RVeloParticipations.objects.filter(competition_id__in=(37, 41, ), distance_id__gt=0)  # 40,  removed complex

    for obj in participants:
        print obj.id
        data = {
            'competition': Competition.objects.get(legacy_id=obj.competition_id),
            'distance': Distance.objects.get(id=obj.distance_id),
            'price': Price.objects.get(id=obj.price_id) if obj.price_id > 0 else None,
            'created': riga_tz.normalize(obj.created),
            'created_by': User.objects.get(legacy_id=obj.user_id) if obj.user_id > 0 else None,
            'insurance': Insurance.objects.get(id=obj.insurance_id) if obj.insurance_id > 0 else None,
            'is_participating': True if obj.status == 2 else False,
            'first_name': obj.participant_first_name.strip().title(),
            'last_name': obj.participant_last_name.strip().title(),
            'birthday': obj.participant_birthday,
            'phone_number': obj.participant_phone_number,
            'email': obj.participant_email,
            'send_email': obj.participant_email_newsletter,
            'send_sms': obj.participant_phone_number_sms,
            'country': COUNTRY_MAP.get(obj.participant_country, None),
            'registrant': User.objects.get(legacy_id=obj.registerer_id) if obj.registerer_id > 0 else None,
            'gender': obj.dzimums,
            'team_name': obj.participant_team_name,
        }
        try:
            data.update({'ssn': legacy_encrypt.decrypt(obj.participant_ssn).strip('\0').replace('-', '')})
        except:
            print 'SSSSSSSSSSSN ERRROR'

        if obj.application_id > 0:
            try:
                data.update({'application': Application.objects.get(legacy_id=obj.application_id)})
            except:
                pass
                # print 'application id doesnt exist'

        if obj.participant_city:
            if obj.participant_city == 'Riga':
                obj.participant_city = 'Rīga'
            try:
                data.update({'city': Choices.objects.get(title=obj.participant_city.strip(), kind=Choices.KIND_CITY),})
            except:
                pass
        if obj.participant_velo_name:
            data.update({'bike_brand': Choices.objects.get(title=obj.participant_velo_name.strip(), kind=Choices.KIND_BIKEBRAND),})
        if obj.participant_occupation:
            try:
                data.update({'occupation': Choices.objects.get(title=obj.participant_occupation.strip(), kind=Choices.KIND_OCCUPATION),})
            except:
                pass
        if obj.participant_where:
            data.update({'where_heard': Choices.objects.get(title=obj.participant_where.strip(), kind=Choices.KIND_HEARD),})
        #
        participant, created = Participant.objects.get_or_create(legacy_id=obj.id, defaults=data)
        if not created:
            if participant.distance != data.get('distance'):
                print 'participant id %i changed distance to %s' % (participant.id, data.get('distance'))
            for d in data:
                setattr(participant, d, data.get(d))
            participant.save()


def sync_users(update=False, start=0, end=1000000):
    users = Ev68RUsers.objects.filter(id__gt=start, id__lt=end)
    if not update:
        last_user_id = User.objects.exclude(legacy_id=None).order_by('-legacy_id')[0].legacy_id
        users = users.filter(id__gt=last_user_id)
    for u in users:
        passw = u.password.split(':')

        data = {
            # 'username': u.username[:30],
            'email': u.email,
            'first_name': u.additional.velo_first_name.strip(),
            'last_name': u.additional.velo_last_name.strip(),
            'date_joined': u.registerdate,
            'ssn': legacy_encrypt.decrypt(u.additional.velo_ssn).strip('\0'),
            'country': COUNTRY_MAP.get(u.additional.velo_country, None),
            'birthday': u.additional.velo_birthday,
            'phone_number': u.additional.velo_phone_number,
            'send_email': u.additional.velo_newsletter,
            'is_active': True,
        }
        if len(passw) == 2:
            data.update({'password': 'md5_custom$%s$%s' % (passw[1], passw[0]),})
        else:
            data.update({'password': 'md5$$%s' % (passw[0]),})

        if u.lastvisitdate:
            data.update({'last_login': u.lastvisitdate,})

        if u.additional.velo_city:
            if u.additional.velo_city == 'Riga':
                u.additional.velo_city = 'Rīga'
            try:
                data.update({
                    'city': Choices.objects.get(title=u.additional.velo_city.strip(), kind=Choices.KIND_CITY),
                })
            except:
                pass
        if u.additional.velo_velo_name:
            try:
                data.update({
                    'bike_brand': Choices.objects.get(title=u.additional.velo_velo_name.strip(), kind=Choices.KIND_BIKEBRAND),
                })
            except:
                pass

        user, created = User.objects.get_or_create(legacy_id=u.id, defaults=data)
        if not created:
            for d in data:
                setattr(user, d, data.get(d))
            user.save()

        # Lets sync social:
        ids = []
        if u.additional.velo_draugiem_id > 0:
            soc, created = UserSocialAuth.objects.get_or_create(user=user, provider='draugiem', uid=u.additional.velo_draugiem_id)
            soc.extra_data = {"apikey": u.additional.velo_draugiem_token}
            soc.save()
            ids.append(soc.id)

        if u.additional.velo_twitter_id > 0:
            tokens = u.additional.velo_twitter_token.split('::')
            soc, created = UserSocialAuth.objects.get_or_create(user=user, provider='twitter', uid=u.additional.velo_twitter_id)
            try:
                soc.extra_data = {"access_token": {"oauth_token_secret": tokens[1], "oauth_token": tokens[0], "user_id": str(u.additional.velo_twitter_id), "screen_name": tokens[3]}, "id": u.additional.velo_twitter_id}
                soc.save()
            except:
                pass
            ids.append(soc.id)
        UserSocialAuth.objects.filter(user=user).exclude(id__in=ids).delete()


def sync_legacy_results(competition):
    results = Ev68RVeloResults.objects.filter(competition_id=competition.legacy_id)
    for obj in results:
        try:
            p = Ev68RVeloParticipations.objects.filter(competition_id=competition.legacy_id, alias=obj.alias, status=2)

            data = {
                'competition': competition,
                'distance': Distance.objects.get(id=obj.distance_id),
                'first_name': obj.first_name,
                'last_name': obj.last_name,
                'year': obj.year,
                'result_distance': obj.result_distance,
                'points_distance': obj.points_distance,
                'phone_number': '',
                'email': '',
            }

            if p:
                p = p[0]
                data.update({'phone_number': p.participant_phone_number, 'email': p.participant_email})

            slugs = CustomSlug.objects.filter(slug=obj.alias)
            if slugs:
                data.update({'slug': slugs.get().slug})
            else:
                data.update({'slug': ''})

            if data.get('last_name') == '?':
                data.update({'last_name': ''})
            if data.get('first_name') == '?':
                data.update({'first_name': ''})

            standing, created = LegacyResult.objects.get_or_create(id=obj.id, defaults=data)
            if not created:
                for d in data:
                    setattr(standing, d, data.get(d))
                standing.save()
        except:
            print 'exception-%i' % obj.id


def sync_legacy_seb_standings():
    sebs = Ev68RVeloResultsSebTotal.objects.all()

    for obj in sebs:

        data = {
            'competition': Competition.objects.get(legacy_id=obj.competition_id),
            'distance': Distance.objects.get(id=obj.distance_id),
            'number': obj.number,
            'group': obj.group,
            'first_name': obj.first_name,
            'last_name': obj.last_name,
            'year': obj.year,
            'team_name': obj.team_name,
            'velo': obj.velo,

            'group_points1': obj.g_p1,
            'group_points2': obj.g_p2,
            'group_points3': obj.g_p3,
            'group_points4': obj.g_p4,
            'group_points5': obj.g_p5,
            'group_points6': obj.g_p6,

            'group_total': obj.g_total,
            'group_place': obj.g_place,

            'distance_points1': obj.d_p1,
            'distance_points2': obj.d_p2,
            'distance_points3': obj.d_p3,
            'distance_points4': obj.d_p4,
            'distance_points5': obj.d_p5,
            'distance_points6': obj.d_p6,

            'distance_total': obj.d_total,
            'distance_place': obj.d_place
        }

        slugs = CustomSlug.objects.filter(slug=obj.alias)
        if slugs:
            data.update({'slug': slugs.get().slug})
        else:
            data.update({'slug': ''})

        if data.get('last_name') == '?':
            data.update({'last_name': ''})
        if data.get('first_name') == '?':
            data.update({'first_name': ''})
        standing, created = LegacySEBStandingsResult.objects.get_or_create(id=obj.id, defaults=data)
        if not created:
            for d in data:
                setattr(standing, d, data.get(d))
            standing.save()



def sync_RM_teams_and_members():
    teams = Ev68RVeloTeams.objects.filter(competition_id=46)
    for obj in teams:

        data = {
            'title': obj.title,
            'description': obj.description,
            'country': COUNTRY_MAP.get(obj.country, None),
            'contact_person': obj.person,
            'email': obj.email,
            'phone_number': obj.phone,
            'management_info': obj.management_info,
            'owner': User.objects.get(legacy_id=obj.created_by),
            'status': 1,
            'is_featured': obj.featured
        }
        if obj.type == '1':
            data.update({'distance': Distance.objects.get(id=28)})
        else:
            data.update({'distance': Distance.objects.get(id=29)})

        team, created = Team.objects.get_or_create(legacy_id=obj.id, defaults=data)
        if not created:
            for d in data:
                setattr(team, d, data.get(d))
            team.save()

        # upload images
        if obj.image:
            url = obj.image.replace('_thumb', '')
            r = requests.get('http://www.velo.lv/%s' % url, verify=False)
            attachment = StringIO(r.content)
            if team.img:
                team.img.delete()
            team.img.save(os.path.basename(url), ContentFile(attachment.read()))
        if obj.shirt_image:
            url = obj.shirt_image.replace('_thumb', '')
            r = requests.get('http://www.velo.lv/%s' % url, verify=False)
            attachment = StringIO(r.content)
            if team.shirt_image:
                team.shirt_image.delete()
            team.shirt_image.save(os.path.basename(url), ContentFile(attachment.read()))
        ids = []
        for obj2 in obj.ev68rveloteammembers_set.filter(participant=1):
            data2 = {
                'first_name': obj2.participant_first_name.title(),
                'last_name': obj2.participant_last_name.title(),
                'birthday': obj2.participant_birthday,
                'country': COUNTRY_MAP.get(obj2.participant_country, None),
                'license_nr': obj2.licence_nr,
                'team': team,
            }

            try:
                data2.update({'ssn': legacy_encrypt.decrypt(obj2.participant_ssn).strip('\0').replace('-', '')})
            except:
                print 'SSSSSSSSSSSN ERRROR'
            print data2
            member, created = Member.objects.get_or_create(legacy_id=obj2.id, defaults=data2)
            if not created:
                for d in data2:
                    setattr(member, d, data2.get(d))
                member.save()
            ids.append(member.id)
        team.member_set.exclude(id__in=ids).delete()



def sync_teams_and_members():
    teams = Ev68RVeloTeams.objects.filter(competition_id=37)
    for obj in teams:

        data = {
            'title': obj.title,
            'description': obj.description,
            'country': COUNTRY_MAP.get(obj.country, None),
            'contact_person': obj.person,
            'email': obj.email,
            'phone_number': obj.phone,
            'management_info': obj.management_info,
            'owner': User.objects.get(legacy_id=obj.created_by),
            'status': 1,
            'is_featured': obj.featured
        }
        if obj.type == '1':
            data.update({'distance': Distance.objects.get(id=24)})
        else:
            data.update({'distance': Distance.objects.get(id=25)})

        team, created = Team.objects.get_or_create(legacy_id=obj.id, defaults=data)
        if not created:
            for d in data:
                setattr(team, d, data.get(d))
            team.save()

        # upload images
        if obj.image:
            url = obj.image.replace('_thumb', '')
            r = requests.get('http://www.velo.lv/%s' % url, verify=False)
            attachment = StringIO(r.content)
            if team.img:
                team.img.delete()
            team.img.save(os.path.basename(url), ContentFile(attachment.read()))
        if obj.shirt_image:
            url = obj.shirt_image.replace('_thumb', '')
            r = requests.get('http://www.velo.lv/%s' % url, verify=False)
            attachment = StringIO(r.content)
            if team.shirt_image:
                team.shirt_image.delete()
            team.shirt_image.save(os.path.basename(url), ContentFile(attachment.read()))
        ids = []
        for obj2 in obj.ev68rveloteammembers_set.filter(participant__in=(1, -10)):
            data2 = {
                'first_name': obj2.participant_first_name.title(),
                'last_name': obj2.participant_last_name.title(),
                'birthday': obj2.participant_birthday,
                'country': COUNTRY_MAP.get(obj2.participant_country, None),
                'license_nr': obj2.licence_nr,
                'team': team,
            }
            if obj2.participant == -10:
                data2.update({'status': 0})
            else:
                data2.update({'status': 1})

            try:
                data2.update({'ssn': legacy_encrypt.decrypt(obj2.participant_ssn).strip('\0').replace('-', '')})
            except:
                print 'SSSSSSSSSSSN ERRROR'
            print data2
            member, created = Member.objects.get_or_create(legacy_id=obj2.id, defaults=data2)
            if not created:
                for d in data2:
                    setattr(member, d, data2.get(d))
                member.save()
            ids.append(member.id)
        # team.member_set.exclude(id__in=ids).delete()


        for comp_id in [41, 42, 43, 44]:
            comp = Competition.objects.get(legacy_id=comp_id)
            ids2 = []
            for obj3 in obj.ev68rveloteamscompetitions_set.filter(competition_id=comp_id):
                print obj3.member_id
                data3 = {
                    'member': Member.objects.get(legacy_id=obj3.member_id),
                    'competition': Competition.objects.get(legacy_id=obj3.competition_id),
                }
                if obj3.type == '2':
                    data3.update({'kind': 10})
                else:
                    data3.update({'kind': 20})
                memberc, created = MemberApplication.objects.get_or_create(legacy_id=obj3.id, defaults=data3)
                if not created:
                    for d in data3:
                        setattr(memberc, d, data3.get(d))
                    memberc.save()
                ids2.append(memberc.id)
            MemberApplication.objects.filter(member__team=team, competition=comp).exclude(id__in=ids2).delete()


def full_sync():
    sync_users()
    sync_applications()
    sync_distances()
    sync_prices()
    sync_insurance()
    sync_participants()
    sync_teams_and_members()



def check_previous_results():
    with open('check_previous_results.csv', 'wb') as file_obj:
        no_results = HelperResults.objects.filter(competition_id=39, calculated_total=0.0).select_related('participant')
        wrt = csv.writer(file_obj)
        wrt.writerow(['SLUG', 'YEAR', 'PLACE', 'PASSAGE'])
        for result in no_results:
            passage = None
            res = Ev68RVeloResultsSebTotal.objects.filter(alias=result.participant.slug, competition_id__in=(12, 28)).order_by('-competition_id')
            if res:
                res = res[0]
                if res.competition_id == 28:
                    year = 2013
                    if res.d_place <= 50:
                        passage = 3
                    elif res.d_place <= 100:
                        passage = 4
                    elif res.d_place <= 200:
                        passage = 4
                    elif res.d_place <= 300:
                        passage = 5
                    elif res.d_place <= 500:
                        passage = 6
                    elif res.d_place <= 700:
                        passage = 7
                    elif res.d_place <= 900:
                        passage = 8
                    elif res.d_place <= 1000:
                        passage = 9
                elif res.competition_id == 12:
                    year = 2012
                    if res.d_place <= 50:
                        passage = 4
                    elif res.d_place <= 100:
                        passage = 5
                    elif res.d_place <= 200:
                        passage = 5
                    elif res.d_place <= 300:
                        passage = 6
                    elif res.d_place <= 500:
                        passage = 7
                    elif res.d_place <= 700:
                        passage = 8
                    elif res.d_place <= 900:
                        passage = 9

                if year and passage:
                    wrt.writerow([result.participant.slug.encode('utf-8'), str(year), str(res.d_place), str(passage)])
