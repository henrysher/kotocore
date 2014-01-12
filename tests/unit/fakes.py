from botocore import xform_name


class FakeParam(object):
    def __init__(self, name, required=False, ptype='string',
                 documentation=None):
        self.name = name
        self.py_name = xform_name(name)
        self.required = required
        self.type = ptype
        self.documentation = documentation


class FakeOperation(object):
    def __init__(self, name, docs='', params=None, output=None, result=None):
        self.name = name
        self.py_name = xform_name(name)
        self.documentation = docs
        self.params = params
        self.output = output
        self.result = result

        if self.params is None:
            self.params = []

        if self.params is None:
            self.params = {}

    def call(self, endpoint, **kwargs):
        return self.result


class FakeService(object):
    operations = []
    api_version = 'fake'

    def __init__(self, endpoint=None):
        self.endpoint = endpoint

        if self.endpoint is None:
            self.endpoint = FakeEndpoint()

    def get_endpoint(self, region_name=None):
        if region_name:
            self.endpoint.region_name = region_name

        return self.endpoint

    def get_operation(self, operation_name):
        for op in self.operations:
            if op.name == operation_name:
                return op

        return None


class FakeEndpoint(object):
    def __init__(self, region_name='us-west-1'):
        self.region_name = region_name


class FakeSession(object):
    def __init__(self, service):
        self.service = service

    def get_service(self, service_name):
        return self.service
