import os

from kotocore.utils.constants import DEFAULT_DOCSTRING
from kotocore.exceptions import APIVersionMismatchError, NoSuchMethod
from kotocore.exceptions import NoRelation
from kotocore.resources import ResourceJSONLoader, ResourceDetails
from kotocore.resources import Resource, ResourceFactory
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
                FakeParam('QueueName', required=True, ptype='string'),
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
            'SendMessage',
            " <p>Sends a message to a queue.</p>\n ",
            params=[
                FakeParam('QueueName', required=True, ptype='string'),
                FakeParam('MessageBody', required=True, ptype='string'),
                FakeParam('MessageType', required=False, ptype='string'),
            ],
            output=True,
            result=(None, True)
        ),
        FakeOperation(
            'ReceiveMessage',
            " something something something ",
            params=[
                FakeParam('QueueUrl', required=True, ptype='string'),
                FakeParam('AttributeNames', required=False, ptype='list'),
                FakeParam('MaxNumberOfMessages', required=False, ptype='integer'),
                FakeParam('VisibilityTimeout', required=False, ptype='integer'),
                FakeParam('WaitTimeSeconds', required=False, ptype='integer'),
            ],
            output={
                'shape_name': 'ReceiveMessageResult',
                'type': 'structure',
                'members': {
                    'Messages': {
                        'shape_name': 'MessageList',
                        'type': 'list',
                        'members': {
                            'shape_name': 'Message',
                            'type': 'structure',
                            'members': {
                                'MessageId': {
                                    'shape_name': 'String',
                                    'type': 'string',
                                    'documentation': None
                                },
                                'ReceiptHandle': {
                                    'shape_name': 'String',
                                    'type': 'string',
                                    'documentation': None
                                },
                                'MD5OfBody': {
                                    'shape_name': 'String',
                                    'type': 'string',
                                    'documentation': None
                                },
                                'Body': {
                                    'shape_name': 'String',
                                    'type': 'string',
                                    'documentation': None
                                },
                                'Attributes': {
                                    'shape_name': 'AttributeMap',
                                    'type': 'map',
                                    'keys': {
                                        'shape_name': 'QueueAttributeName',
                                        'type': 'string',
                                        'enum': [
                                            'Policy',
                                            'VisibilityTimeout',
                                            'MaximumMessageSize',
                                            'MessageRetentionPeriod',
                                            'ApproximateNumberOfMessages',
                                            'ApproximateNumberOfMessagesNotVisible',
                                            'CreatedTimestamp',
                                            'LastModifiedTimestamp',
                                            'QueueArn',
                                            'ApproximateNumberOfMessagesDelayed',
                                            'DelaySeconds',
                                            'ReceiveMessageWaitTimeSeconds'
                                        ],
                                        'documentation': '\n    <p>The name of a queue attribute.</p>\n  ',
                                        'xmlname': 'Name'
                                    },
                                    'members': {
                                        'shape_name': 'String',
                                        'type': 'string',
                                        'documentation': '\n    <p>The value of a queue attribute.</p>\n  ',
                                        'xmlname': 'Value'
                                    },
                                    'flattened': True,
                                    'xmlname': 'Attribute',
                                    'documentation': None,
                                },
                            },
                            'documentation': None,
                            'xmlname': 'Message'
                        },
                        'flattened': True,
                        'documentation': '\n    <p>A list of messages.</p>\n  '
                    }
                },
                'documentation': None
            },
            result=(None, {
                'Messages': [
                    {
                        'MessageId': 'msg-12345',
                        'ReceiptHandle': 'hndl-12345',
                        'MD5OfBody': '6cd3556deb0da54bca060b4c39479839',
                        'Body': 'Hello, world!',
                        'Attributes': {
                            'QueueArn': 'arn:aws:example:example:sqs:something',
                            'ApproximateNumberOfMessagesDelayed': '2',
                            'DelaySeconds': '10',
                            'CreatedTimestamp': '2013-10-17T21:52:46Z',
                            'LastModifiedTimestamp': '2013-10-17T21:52:46Z',
                        },
                    },
                    {
                        'MessageId': 'msg-12346',
                        'ReceiptHandle': 'hndl-12346',
                        'MD5OfBody': '6cd355',
                        'Body': 'Another message!',
                        'Attributes': {},
                    },
                ]
            })
        ),
        FakeOperation(
            'DeleteQueue',
            " <p>Deletes a queue.</p>\n ",
            params=[
                FakeParam('QueueName', required=True, ptype='string'),
            ],
            output=True,
            result=(None, True)
        ),
    ]


class ResourceDetailsTestCase(unittest.TestCase):
    def setUp(self):
        super(ResourceDetailsTestCase, self).setUp()
        self.test_dirs = [
            os.path.join(os.path.dirname(__file__), 'test_data')
        ]
        self.test_loader = ResourceJSONLoader(self.test_dirs)
        self.session = Session(FakeSession(TestCoreService()))

        self.rd = ResourceDetails(
            self.session,
            'test',
            'Preset',
            loader=self.test_loader
        )

    def test_init(self):
        self.assertEqual(self.rd.session, self.session)
        self.assertEqual(self.rd.service_name, 'test')
        self.assertEqual(self.rd.loader, self.test_loader)
        self.assertEqual(self.rd._loaded_data, None)
        self.assertEqual(self.rd._api_version, None)

    def test_service_data_uncached(self):
        self.assertEqual(self.rd._loaded_data, None)

        data = self.rd.service_data
        self.assertEqual(len(data.keys()), 4)
        self.assertTrue('api_version' in self.rd._loaded_data)

    def test_resource_data_uncached(self):
        self.assertEqual(self.rd._loaded_data, None)

        data = self.rd.resource_data
        self.assertEqual(len(data.keys()), 4)
        self.assertTrue('identifiers' in data)
        self.assertTrue('operations' in data)
        self.assertTrue('api_version' in self.rd._loaded_data)

    def test_api_version_uncached(self):
        self.assertEqual(self.rd._api_version, None)

        av = self.rd.api_version
        self.assertEqual(av, '2013-11-27')
        self.assertEqual(self.rd._api_version, '2013-11-27')

    def test_identifiers(self):
        self.assertEqual(self.rd.identifiers, [
            {
                'api_name': '$shape_name.Id',
                'var_name': 'id',
            }
        ])

    def test_result_key_for(self):
        # Non-existent
        self.assertEqual(self.rd.result_key_for('notthere'), None)

        # Now with actual data.
        self.assertEqual(self.rd.result_key_for('get'), 'Preset')

    def test_relations(self):
        # No relations.
        alt_rd = ResourceDetails(
            self.session,
            'test',
            'Job',
            loader=self.test_loader
        )
        self.assertEqual(alt_rd.relations, {})

        # With relations.
        self.assertEqual(self.rd.relations, {
            'pipelines': {
                'class': 'PipelineCollection',
                'class_type': 'collection',
                'rel_type': 'M-M',
                'required': False
            }
        })

    def test_cached(self):
        # Fake in data.
        self.rd._loaded_data = {
            'api_version': '20XX-MM-II',
            'hello': 'world',
        }

        data = self.rd.service_data
        av = self.rd.api_version
        self.assertTrue('hello' in data)
        self.assertTrue('20XX-MM-II' in av)


class FakeConn(object):
    def __init__(self, *args, **kwargs):
        super(FakeConn, self).__init__()

    def delete_pipeline(self, *args, **kwargs):
        return {
            'RequestId': '1234-1234-1234-1234',
            'Id': '1872baf45',
            'Title': 'A pipe',
        }


class OopsConn(object):
    # Used to demonstrate when no API methods are available.
    def __init__(self, *args, **kwargs):
        super(OopsConn, self).__init__()


class PipeResource(Resource):
    def update_params(self, conn_method_name, params):
        params['global'] = True
        return super(PipeResource, self).update_params(conn_method_name, params)

    def update_params_delete(self, params):
        params.update(self.get_identifiers())
        return params

    def post_process(self, conn_method_name, result):
        result = result.copy()
        self.identifier = result.pop('Id', None)
        return result

    def post_process_delete(self, result):
        self.deleted = True
        return result


class FakeJobCollection(object):
    def __init__(self, connection, **kwargs):
        self._data = kwargs

    def get_identifiers(self):
        return self._data


class ResourceTestCase(unittest.TestCase):
    def setUp(self):
        super(ResourceTestCase, self).setUp()
        self.session = Session(FakeSession(TestCoreService()))
        self.fake_details = ResourceDetails(self.session, 'test', 'Pipe')
        self.fake_details._loaded_data = {
            'api_version': 'something',
            'resources': {
                'Pipe': {
                    'identifiers': [
                        {
                            'var_name': 'id',
                            'api_name': 'Id',
                        },
                    ],
                    'operations': {
                        'delete': {
                            'api_name': 'DeletePipe'
                        }
                    },
                    'relations': {
                        'jobs': {
                            'class': 'JobCollection',
                            'class_type': 'collection',
                            'rel_type': '1-M',
                            'required': False
                        },
                        'unknown': {
                            'class': 'Something',
                            'class_type': 'unknown',
                        }
                    }
                }
            }
        }
        self.fake_conn = FakeConn()
        PipeResource._details = self.fake_details
        self.resource = PipeResource(
            connection=self.fake_conn,
            id='1872baf45'
        )

    def tearDown(self):
        del PipeResource._details
        super(ResourceTestCase, self).tearDown()

    def test_get_identifiers(self):
        self.assertEqual(self.resource.get_identifiers(), {'id': '1872baf45'})

    def test_set_identifiers(self):
        self.assertEqual(self.resource._data, {
            'id': '1872baf45',
        })

        # Only sets things found in the identifiers, not random data.
        self.resource.set_identifiers({'id': 'hello!', 'bucket': 'something'})
        self.assertEqual(self.resource._data, {
            'id': 'hello!'
        })

    def test_full_update_params(self):
        params = {
            'notify': True,
        }
        prepped = self.resource.full_update_params('delete', params)
        self.assertEqual(prepped, {
            'global': True,
            'id': '1872baf45',
            'notify': True,
        })

        params['yeah'] = 'yeahyeah'
        prepped = self.resource.full_update_params('get', params)
        self.assertEqual(prepped, {
            'global': True,
            'id': '1872baf45',
            'notify': True,
            'yeah': 'yeahyeah',
        })

    def test_full_post_process(self):
        results = {
            'Id': '1872baf45',
            'Title': 'A pipe',
        }
        processed = self.resource.full_post_process('delete', results)
        self.assertEqual(processed, {
            'Title': 'A pipe'
        })
        self.assertEqual(self.resource.deleted, True)

    def test_full_post_process_get(self):
        # Without a result key.
        results = {
            'Id': '1872baf45',
            'Title': 'A pipe',
        }
        processed = self.resource.full_post_process('get', results)
        self.assertEqual(processed, {
            'Title': 'A pipe'
        })
        # Note that what get's assigned has been snake_cased.
        self.assertEqual(self.resource.id, '1872baf45')
        self.assertEqual(self.resource.title, 'A pipe')

    def test_full_post_process_get_result_key(self):
        orig_fake_data = self.fake_details._loaded_data
        self.addCleanup(
            setattr, self.fake_details, '_loaded_data', orig_fake_data
        )

        result_key_fake_data = orig_fake_data.copy()
        result_key_fake_data['resources']['Pipe']['operations']['get'] = {
            'api_name': 'GetPipe',
            'result_key': 'Pipe',
        }

        resource = PipeResource(
            connection=self.fake_conn,
            id='92aa36e5b'
        )

        # With a result key.
        self.fake_details._loaded_data = result_key_fake_data
        results = {
            'Pipe': {
                'Id': '92aa36e5b',
                'Title': 'Another pipe',
            }
        }
        self.assertEqual(resource._data, {'id': '92aa36e5b'})
        processed = resource.full_post_process('get', results)
        self.assertEqual(processed, {
            'Pipe': {
                'Id': '92aa36e5b',
                'Title': 'Another pipe'
            }
        })
        # Despite being nested in the response, the right data is assigned.
        self.assertEqual(resource.id, '92aa36e5b')
        self.assertEqual(resource.title, 'Another pipe')

    def test_build_relation(self):
        # For testing purposes.
        self.session.cache.services['test'] = {
            'collections': {
                'JobCollection': {
                    'default': FakeJobCollection
                }
            }
        }

        # With an unknown relation name.
        with self.assertRaises(NoRelation) as cm:
            self.resource.build_relation('nopenopenope')

        self.assertTrue('No such relation' in str(cm.exception))

        # With an unknown relation type.
        with self.assertRaises(NoRelation) as cm:
            self.resource.build_relation('unknown')

        self.assertTrue('Unknown class' in str(cm.exception))

        # Introspected from the data.
        rel = self.resource.build_relation('jobs')
        self.assertTrue(isinstance(rel, FakeJobCollection))
        # Should have inherited some identifiers from the the parent
        # ``self.resource``...
        self.assertEqual(rel.get_identifiers(), {
            'id': '1872baf45',
        })

        # If given an explicit class, build with that instead.
        class Whatever(object):
            def __init__(self, *args, **kwargs):
                self._data = kwargs

        rel = self.resource.build_relation('jobs', klass=Whatever)
        self.assertTrue(isinstance(rel, Whatever))


class ResourceFactoryTestCase(unittest.TestCase):
    def setUp(self):
        super(ResourceFactoryTestCase, self).setUp()
        self.session = Session(FakeSession(TestCoreService()))
        self.test_dirs = [
            os.path.join(os.path.dirname(__file__), 'test_data')
        ]
        self.test_loader = ResourceJSONLoader(self.test_dirs)
        self.rd = ResourceDetails(
            self.session,
            'test',
            'Pipeline',
            loader=self.test_loader
        )
        self.rf = ResourceFactory(session=self.session, loader=self.test_loader)

    def test_init(self):
        self.assertEqual(self.rf.session, self.session)
        self.assertTrue(isinstance(self.rf.loader, ResourceJSONLoader))
        self.assertEqual(self.rf.base_resource_class, Resource)
        self.assertEqual(self.rf.details_class, ResourceDetails)

        # Test overrides (invalid for actual usage).
        import kotocore
        rf = ResourceFactory(
            loader=False,
            base_resource_class=PipeResource,
            details_class=True
        )
        self.assertEqual(rf.session, kotocore.session)
        self.assertEqual(rf.loader, False)
        self.assertEqual(rf.base_resource_class, PipeResource)
        self.assertEqual(rf.details_class, True)

    def test_build_class_name(self):
        self.assertEqual(
            self.rf._build_class_name('Pipeline'),
            'Pipeline'
        )
        self.assertEqual(
            self.rf._build_class_name('TestName'),
            'TestName'
        )

    def test_build_methods(self):
        attrs = self.rf._build_methods(self.rd)
        self.assertEqual(len(attrs), 5)
        self.assertTrue('delete' in attrs)
        self.assertTrue('get' in attrs)
        self.assertTrue('update' in attrs)

    def test_create_operation_method(self):
        class StubbyResource(Resource):
            pass

        op_method = self.rf._create_operation_method('delete', {
            "api_name": "DeletePipeline"
        })
        self.assertEqual(op_method.__name__, 'delete')
        self.assertEqual(op_method.__doc__, DEFAULT_DOCSTRING)

        # Assign it & call it.
        StubbyResource._details = self.rd
        StubbyResource.delete = op_method
        sr = StubbyResource(connection=FakeConn())
        self.assertEqual(sr.delete(), {
            'Id': '1872baf45',
            'RequestId': '1234-1234-1234-1234',
            'Title': 'A pipe'
        })

        # Make sure an exception is raised when the underlying connection
        # doesn't have an analogous method.
        sr = StubbyResource(connection=OopsConn())

        with self.assertRaises(NoSuchMethod):
            fake_pipe = sr.delete()

    def test_construct_for(self):
        res_class = self.rf.construct_for('test', 'Pipeline')
