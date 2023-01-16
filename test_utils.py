"""
Utility functions for tests
"""
from __future__ import absolute_import

import json
import re

from mock import patch, Mock
from requests.models import Response
from rest_framework.status import HTTP_200_OK
from webob import Request
from workbench.runtime import WorkbenchRuntime
from xblock.core import XBlock
from xblock.fields import Scope, ScopeIds, String
from xblock.runtime import DictKeyValueStore, KvsFieldData

from skill_tagging.skill_tagging_mixin import SkillTaggingMixin


class TestBlock(XBlock, SkillTaggingMixin):
    BLOCK_TYPE = "test"
    has_score = False
    display_name = String(scope=Scope.content, name='Test Block')
    fragment = None

    def student_view(self, context):
        return self.fragment


class TestSkillTaggingMixin(SkillTaggingMixin):
    pass


def get_tagging_mixin():
    return TestSkillTaggingMixin


def make_request(data, method='POST'):
    """ Make a webob JSON Request """
    request = Request.blank('/')
    request.method = 'POST'
    data = json.dumps(data).encode('utf-8') if data is not None else b''
    request.body = data
    request.method = method
    return request


def make_block(block_type="vertical"):
    """ Instantiate a test XBlock inside a WorkbenchRuntime """
    key_store = DictKeyValueStore()
    field_data = KvsFieldData(key_store)
    runtime = WorkbenchRuntime()
    runtime.course_id = "dummy_course_id"
    def_id = runtime.id_generator.create_definition(block_type)
    usage_id = Mock(block_type=block_type, block_id=def_id)
    scope_ids = ScopeIds('user', block_type, def_id, usage_id)
    return TestBlock(runtime, field_data, scope_ids=scope_ids)


class TestCaseMixin:
    """ Helpful mixins for unittest TestCase subclasses """
    maxDiff = None

    VERIFY_TAGS_HANDLER = 'verify_tags'

    def setUp(self):
        self.block = make_block(getattr(self, "block_type", "vertical"))
        self.patch_workbench()
        fake_user = Mock()
        fake_user.opt_attrs = {
            'edx-platform.user_role': 'student',
            'edx-platform.is_authenticated': True,
        }
        mock_user_service = Mock()
        mock_user_service.get_current_user.return_value = fake_user
        self.block.runtime.service = Mock(return_value=mock_user_service)

    def get_mock_api_response(self):
        """Mock fetch tags response"""
        sample_output = {
            "results": [{
                "id": 1,
                "skills": [
                    {
                        "id": 1,
                        "name": "SKILL-0"
                    },
                    {
                        "id": 6,
                        "name": "SKILL-5"
                    },
                ],
            }]
        }
        api_client = Mock(
            get=Mock(
                return_value=self._mock_response(
                    HTTP_200_OK,
                    sample_output
                )
            )
        )
        return api_client

    def patch_workbench(self):
        """
        Apply required patches to workbench
        """
        self.apply_patch(
            'workbench.runtime.WorkbenchRuntime.local_resource_url',
            lambda _, _block, path: '/expanded/url/to/test/' + path
        )
        self.apply_patch(
            'workbench.runtime.WorkbenchRuntime.replace_urls',
            lambda _, html: re.sub(
                r'"/static/([^"]*)"',
                r'"/course/test-course/assets/\1"',
                html
            ),
            create=True,
        )

    def apply_patch(self, *args, **kwargs):
        new_patch = patch(*args, **kwargs)
        mock = new_patch.start()
        self.addCleanup(new_patch.stop)
        return mock

    def call_handler(self, handler_name, data=None,
                     expect_json=True, method='POST'):
        """
        Call required XBlock handler
        """
        response = self.block.handle(
            handler_name,
            make_request(data, method=method)
        )
        if expect_json:
            self.assertEqual(response.status_code, 200)
            return json.loads(response.body.decode('utf-8'))
        return response

    def _mock_response(self, status_code, content=None):
        """
        Generates a python core response.
        """
        mock_response = Response()
        mock_response.status_code = status_code
        # pylint: disable=protected-access
        mock_response._content = json.dumps(content).encode('utf-8')
        return mock_response
