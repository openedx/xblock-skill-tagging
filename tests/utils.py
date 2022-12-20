"""
Utility functions for tests
"""
from __future__ import absolute_import

import json
import re

from mock import patch
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


def make_block():
    """ Instantiate a test XBlock inside a WorkbenchRuntime """
    block_type = 'test'
    key_store = DictKeyValueStore()
    field_data = KvsFieldData(key_store)
    runtime = WorkbenchRuntime()
    runtime.course_id = "dummy_course_id"
    def_id = runtime.id_generator.create_definition(block_type)
    usage_id = runtime.id_generator.create_usage(def_id)
    scope_ids = ScopeIds('user', block_type, def_id, usage_id)
    return TestBlock(runtime, field_data, scope_ids=scope_ids)


class TestCaseMixin:
    """ Helpful mixins for unittest TestCase subclasses """
    maxDiff = None

    FETCH_TAGS_HANDLER = 'fetch_tags'
    VERIFY_TAGS_HANDLER = 'verify_tags'

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
