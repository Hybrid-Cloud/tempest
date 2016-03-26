#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from tempest.api.baremetal.admin import base
from tempest import test


class TestApiDiscovery(base.BaseBaremetalTest):
    """Tests for API discovery features."""

    @test.idempotent_id('a3c27e94-f56c-42c4-8600-d6790650b9c5')
    def test_api_versions(self):
        _, descr = self.client.get_api_description()
        expected_versions = ('v1',)
        versions = [version['id'] for version in descr['versions']]

        for v in expected_versions:
            self.assertIn(v, versions)

    @test.idempotent_id('896283a6-488e-4f31-af78-6614286cbe0d')
    def test_default_version(self):
        _, descr = self.client.get_api_description()
        default_version = descr['default_version']
        self.assertEqual(default_version['id'], 'v1')

    @test.idempotent_id('abc0b34d-e684-4546-9728-ab7a9ad9f174')
    def test_version_1_resources(self):
        _, descr = self.client.get_version_description(version='v1')
        expected_resources = ('nodes', 'chassis',
                              'ports', 'links', 'media_types')

        for res in expected_resources:
            self.assertIn(res, descr)
