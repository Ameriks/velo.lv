class GetRequestTableKwargs(object):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.request_kwargs = kwargs.pop('request_kwargs', None)
        super(GetRequestTableKwargs, self).__init__(*args, **kwargs)
