from kotocore.connection import ConnectionDetails, ConnectionFactory
from kotocore.exceptions import ServerError
from kotocore.session import Session

from tests import unittest
from tests.unit.fakes import FakeParam, FakeOperation, FakeService, FakeSession


class TestCoreService(FakeService):
    api_version = '2013-08-23'
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
            },
            result=(None, {
                'QueueUrl': 'http://example.com',
            })
        ),
        FakeOperation(
            'DeleteQueue',
            " <p>Deletes a queue.</p>\n ",
            params=[
                FakeParam('QueueName', required=True, ptype='string'),
            ],
            output=True,
            result=(None, {'success': True})
        ),
    ]


class ChangedTestCoreService(TestCoreService):
    operations = TestCoreService.operations[1:2]


class ConnectionDetailsTestCase(unittest.TestCase):
    def setUp(self):
        super(ConnectionDetailsTestCase, self).setUp()
        self.session = Session(FakeSession(TestCoreService()))
        self.sd = ConnectionDetails(
            service_name='test',
            session=self.session
        )

    def test_init(self):
        self.assertEqual(self.sd.service_name, 'test')
        self.assertEqual(self.sd.session, self.session)
        self.assertEqual(self.sd._api_version, None)
        self.assertEqual(self.sd._loaded_service_data, None)

    def test_service_data(self):
        self.assertEqual(self.sd._loaded_service_data, None)

        # Access the property. It should load the data, cache it & return it.
        self.assertEqual(len(self.sd.service_data), 2)

        self.assertNotEqual(self.sd._loaded_service_data, None)
        # Ensure the API version was cleared out as well.
        self.assertEqual(self.sd._api_version, None)

    def test_api_version(self):
        self.assertEqual(self.sd._api_version, None)

        # Access the property. It should load the data, cache it & return it.
        self.assertEqual(self.sd.api_version, '2013-08-23')

        self.assertEqual(self.sd._api_version, '2013-08-23')

        # Test the cached version
        self.sd._api_version += 'a'
        self.assertEqual(self.sd.api_version, '2013-08-23a')

    def test__introspect_service(self):
        service_data = self.sd._introspect_service(
            self.session.core_session,
            'test'
        )
        # We test the introspected data elsewhere, so it's enough that we
        # just check the necessary method names are here.
        self.assertEqual(sorted(list(service_data.keys())), [
            'create_queue',
            'delete_queue'
        ])

    def test_reload_service_data(self):
        service_data = self.sd._introspect_service(
            self.session.core_session,
            'test'
        )
        self.assertEqual(sorted(list(service_data.keys())), [
            'create_queue',
            'delete_queue'
        ])

        # Now it changed.
        self.sd.session = Session(FakeSession(ChangedTestCoreService()))
        self.sd.reload_service_data()
        self.assertEqual(sorted(list(self.sd.service_data.keys())), [
            'delete_queue'
        ])


class ConnectionFactoryTestCase(unittest.TestCase):
    def setUp(self):
        super(ConnectionFactoryTestCase, self).setUp()
        self.session = Session(FakeSession(TestCoreService()))
        self.sf = ConnectionFactory(session=self.session)
        self.test_service_class = self.sf.construct_for('test')

    def test__check_method_params(self):
        _cmp = self.test_service_class()._check_method_params
        op_params = [
            {
                'var_name': 'queue_name',
                'api_name': 'QueueName',
                'required': True,
                'type': 'string',
            },
            {
                'var_name': 'attributes',
                'api_name': 'Attributes',
                'required': False,
                'type': 'map',
            },
        ]
        # Missing the required ``queue_name`` parameter.
        self.assertRaises(TypeError, _cmp, op_params)
        self.assertRaises(TypeError, _cmp, op_params, attributes=1)

        # All required params present.
        self.assertEqual(_cmp(op_params, queue_name='boo'), None)
        self.assertEqual(_cmp(op_params, queue_name='boo', attributes=1), None)

    def test__build_service_params(self):
        _bsp = self.test_service_class()._build_service_params
        op_params = [
            {
                'var_name': 'queue_name',
                'api_name': 'QueueName',
                'required': True,
                'type': 'string',
            },
            {
                'var_name': 'attributes',
                'api_name': 'Attributes',
                'required': False,
                'type': 'map',
            },
        ]
        self.assertEqual(_bsp(op_params, queue_name='boo'), {
            'queue_name': 'boo',
        })
        self.assertEqual(_bsp(op_params, queue_name='boo', attributes=1), {
            'queue_name': 'boo',
            'attributes': 1,
        })

    def test__create_operation_method(self):
        func = self.sf._create_operation_method('test', {
            'method_name': 'test',
            'api_name': 'Test',
            'docs': 'This is a test.',
            'params': [],
            'output': True,
        })
        self.assertEqual(func.__name__, 'test')
        self.assertEqual(
            func.__doc__,
            'This is a test.\n:' + \
            'returns: The response data received\n' + \
            ':rtype: dict\n'
        )

    def test__check_for_errors(self):
        cfe = self.test_service_class()._check_for_errors

        # Make sure a success call doesn't throw an exception.
        cfe((None, {'success': True}))

        # With an empty list of errors (S3-style success.
        cfe((None, {'Errors': [], 'success': True}))

        # With a list of errors.
        with self.assertRaises(ServerError) as cm:
            cfe((None, {'Errors': [{'Message': 'Not much.'}]}))

        self.assertEqual(cm.exception.code, 'ConnectionError')
        self.assertEqual(cm.exception.message, 'Not much.')
        self.assertEqual(cm.exception.full_response, {
            'Errors': [{'Message': 'Not much.'}]
        })

        # With a single, detailed error.
        with self.assertRaises(ServerError) as cm:
            cfe((None, {
                'Errors': {
                    'Code': 'FellApart',
                    'Message': 'The robot serving the request fell apart.'
                }
            }))

        self.assertEqual(cm.exception.code, 'FellApart')
        self.assertEqual(
            cm.exception.message,
            'The robot serving the request fell apart.'
        )

        # With an error string.
        with self.assertRaises(ServerError) as cm:
            cfe((None, {'Errors': 'Sadness.'}))

        self.assertEqual(cm.exception.code, 'ConnectionError')
        self.assertEqual(cm.exception.message, 'Sadness.')

    def test__post_process_results(self):
        ppr = self.test_service_class()._post_process_results
        self.assertEqual(ppr('whatever', {}, (None, True)), True)
        self.assertEqual(ppr('whatever', {}, (None, False)), False)
        self.assertEqual(ppr('whatever', {}, (None, 'abc')), 'abc')
        self.assertEqual(ppr('whatever', {}, (None, ['abc', 1])), [
            'abc',
            1
        ])
        self.assertEqual(ppr('whatever', {}, (None, {'abc': 1})), {
            'abc': 1,
        })

    def test_integration(self):
        # Essentially testing ``_build_methods``.
        # This is a painful integration test. If the other methods don't work,
        # this will certainly fail.
        self.assertTrue(hasattr(self.test_service_class, 'create_queue'))
        self.assertTrue(hasattr(self.test_service_class, 'delete_queue'))

        ts = self.test_service_class()

        # Missing required parameters.
        self.assertRaises(TypeError, ts, 'create_queue')
        self.assertRaises(TypeError, ts, 'delete_queue')

        # Successful calls.
        self.assertEqual(ts.create_queue(queue_name='boo'), {
            'QueueUrl': 'http://example.com'
        })
        self.assertEqual(ts.delete_queue(queue_name='boo'), {'success': True})

        # Test the params.
        create_queue_params = ts._get_operation_params('create_queue')
        self.assertEqual(
            [param['var_name'] for param in create_queue_params],
            ['queue_name', 'attributes']
        )

        # Check the docstring.
        self.assertTrue(
            ':param queue_name: The name' in ts.create_queue.__doc__
        )
        self.assertTrue(
            ':type queue_name: string' in ts.create_queue.__doc__
        )

    def test_late_binding(self):
        # If the ``ConnectionDetails`` data changes, it should be reflected in
        # the dynamic methods.
        ts = self.test_service_class()

        # Successful calls.
        self.assertEqual(ts.create_queue(queue_name='boo'), {
            'QueueUrl': 'http://example.com'
        })

        # Now the required params change underneath us.
        # This is ugly/fragile, but also unlikely.
        sd = ts._details._loaded_service_data
        sd['create_queue']['params'][1]['required'] = True

        # Now this call should fail, since there's a new required parameter.
        self.assertRaises(TypeError, ts, 'create_queue')


if __name__ == "__main__":
    unittest.main()
