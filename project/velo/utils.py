import importlib
import os
import requests
import datetime
import stat


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
