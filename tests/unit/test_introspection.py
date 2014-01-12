from kotocore.introspection import Introspection

from tests import unittest
from tests.unit.fakes import FakeParam, FakeOperation, FakeService, FakeSession


class TestService(FakeService):
    operations = [
        FakeOperation(
            'CreateQueue',
            " <p>Creates a queue.</p>\n ",
            params=[
                FakeParam(
                    'QueueName',
                    required=True,
                    ptype='string',
                    documentation='\n    <p>The name for the queue to be created.</p>\n  '
                ),
                FakeParam('Attributes', required=False, ptype='map'),
            ],
            output={
                'shape_name': 'CreateQueueResult',
                'type': 'structure',
                'members': {
                    'QueueUrl': {
                        'shape_name': 'String',
                        'type': 'string',
                        'documentation': '\n    <p>The URL for the created SQS queue.</p>\n  ',
                    },
                },
            }
        ),
        # FIXME: More here to fully exercise things.
    ]

class IntrospectionTestCase(unittest.TestCase):
    def setUp(self):
        super(IntrospectionTestCase, self).setUp()
        self.service = TestService()
        self.session = FakeSession(self.service)
        self.introspection = Introspection(self.session)

    def test_parse_param(self):
        param = self.service.operations[0].params[0]
        param_data = self.introspection.parse_param(param)
        self.assertEqual(param_data['var_name'], 'queue_name')
        self.assertEqual(param_data['api_name'], 'QueueName')
        self.assertEqual(
            param_data['docs'],
            'The name for the queue to be created.'
        )
        self.assertEqual(param_data['required'], True)
        self.assertEqual(param_data['type'], 'string')

    def test_parse_params(self):
        params_data = self.introspection.parse_params(
            self.service.operations[0].params
        )
        self.assertEqual(len(params_data), 2)
        self.assertEqual(params_data[0]['var_name'], 'queue_name')
        self.assertEqual(params_data[0]['api_name'], 'QueueName')
        self.assertEqual(params_data[0]['required'], True)
        self.assertEqual(params_data[0]['type'], 'string')
        self.assertEqual(
            params_data[0]['docs'],
            'The name for the queue to be created.'
        )
        self.assertEqual(params_data[1]['var_name'], 'attributes')
        self.assertEqual(params_data[1]['api_name'], 'Attributes')
        self.assertEqual(params_data[1]['required'], False)
        self.assertEqual(params_data[1]['type'], 'map')
        self.assertEqual(params_data[1]['docs'], '')

    def test_get_endpoint(self):
        endpoint = self.introspection.get_endpoint(self.service)
        self.assertEqual(endpoint.region_name, 'us-east-1')

        endpoint = self.introspection.get_endpoint(
            self.service,
            region_name='us-west-2'
        )
        self.assertEqual(endpoint.region_name, 'us-west-2')

    def test_get_operation(self):
        operation = self.introspection.get_operation(
            self.service,
            'CreateQueue'
        )
        self.assertEqual(operation.py_name, 'create_queue')

    def test_introspect_operation(self):
        op_data = self.introspection.introspect_operation(
            self.service.operations[0]
        )
        self.assertEqual(sorted(list(op_data.keys())), [
            'api_name',
            'docs',
            'method_name',
            'output',
            'params'
        ])
        self.assertEqual(op_data['api_name'], 'CreateQueue')
        self.assertEqual(op_data['docs'], ' \n\nCreates a queue.\n\n ')
        self.assertEqual(op_data['method_name'], 'create_queue')
        self.assertEqual(len(op_data['params']), 2)
        self.assertEqual(op_data['params'][0]['var_name'], 'queue_name')
        self.assertEqual(op_data['params'][1]['var_name'], 'attributes')
        self.assertEqual(op_data['output']['shape_name'], 'CreateQueueResult')
        self.assertEqual(op_data['output']['type'], 'structure')
        self.assertEqual(sorted(list(op_data['output']['members'].keys())), [
            'QueueUrl'
        ])

    def test_introspect_service(self):
        service_data = self.introspection.introspect_service('test')
        self.assertEqual(list(service_data.keys()), ['create_queue'])
