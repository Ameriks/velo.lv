import importlib
import os
import requests
import datetime
import stat
import csv



def listdir(path):
    try:
        result = os.stat(path)
    except OSError:
        return []
    if stat.S_ISDIR(result.st_mode):
        return sorted(os.listdir(path))
    else:
        return []


def load_class(full_class_string):
    """
    dynamically load a class from a string
    """

    class_data = full_class_string.split(".")
    module_path = ".".join(class_data[:-1])
    class_str = class_data[-1]

    module = importlib.import_module(module_path)
    # Finally, we retrieve the Class
    return getattr(module, class_str)


def bday_from_LV_SSN(ssn):
    try:
        ssn = ssn.replace('-', '').replace(' ', '').strip()
        year = 1900 if ssn[6] == '1' else 2000
        year += int(ssn[4:6])
        return datetime.date(year, int(ssn[2:4]), int(ssn[0:2]))
    except:
        return None


class SessionWHeaders(requests.Session):
    url = None

    def __init__(self, additional_headers, url=None):
        super(SessionWHeaders, self).__init__()
        self.url = url
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36',
                        'Accept': '*/*',
                        'Accept-Encoding': 'gzip, deflate, compress',
                        'content-type': 'application/json'}
        self.headers.update(additional_headers)

    def update_url(self, url):
        if 'http://' in url or 'https://' in url:
            return url
        if self.url:
            return "%s%s" % (self.url, url)

    def get(self, url, **kwargs):
        return self.request('GET', self.update_url(url), **kwargs)

    def post(self, url, data=None, **kwargs):
        return self.request('POST', self.update_url(url), data=data, **kwargs)

    def put(self, url, data=None, **kwargs):
        return self.request('PUT', self.update_url(url), data=data, **kwargs)


def get_participants_not_raced_in_last_two_years():
    from velo.core.models import Competition
    from velo.registration.models import Participant, ChangedName
    from velo.results.models import HelperResults
    participants_not_raced = []
    all_participants = Participant.objects.order_by("slug").distinct("slug")
    index = 0
    for participant in all_participants:
        index += 1
        if index % 100 == 0:
            print(index)
        if HelperResults.objects.filter(competition__parent_id__in=(79, 67)).filter(participant__is_participating=True, participant__slug=participant.slug).exists():
            continue
        slugs = list(ChangedName.objects.filter(new_slug=participant.slug).values_list('slug')) + [participant.slug, ]
        if HelperResults.objects.filter(competition__parent__parent_id=1).filter(participant__is_participating=True, participant__slug__in=slugs).exists():
            # last_competition = Participant.objects.filter(slug__in=slugs).order_by("-competition_id")[0]
            last_competition = HelperResults.objects.filter(competition__parent__parent_id=1).filter(participant__is_participating=True, participant__slug__in=slugs).order_by("-competition_id")[0]
            if not last_competition:
                continue
            last_competition_date = Competition.objects.get(id=last_competition.competition_id).competition_date

            if not last_competition_date:
                continue
            if last_competition_date.year == 2018 or last_competition_date.year == 2017:
                continue
            full_name = participant.first_name + " " + participant.last_name
            if full_name == " ":
                full_name = "-"
            email = participant.email
            if email == "":
                email = "-"

            participants_not_raced.append([
                full_name, email, last_competition_date,
            ])

    toCSV = participants_not_raced
    with open("participants_not_reced_last_two_years", "w") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(["Full name", "e-mail", "last competition date"])
        writer.writerows(toCSV)

