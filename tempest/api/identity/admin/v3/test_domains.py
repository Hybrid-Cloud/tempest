# Copyright 2013 OpenStack Foundation
# All Rights Reserved.
#
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

from tempest.api.identity import base
from tempest.common.utils import data_utils
from tempest import config
from tempest import test

CONF = config.CONF


class DomainsTestJSON(base.BaseIdentityV3AdminTest):

    def _delete_domain(self, domain_id):
        # It is necessary to disable the domain before deleting,
        # or else it would result in unauthorized error
        self.domains_client.update_domain(domain_id, enabled=False)
        self.domains_client.delete_domain(domain_id)
        # Asserting that the domain is not found in the list
        # after deletion
        body = self.domains_client.list_domains()['domains']
        domains_list = [d['id'] for d in body]
        self.assertNotIn(domain_id, domains_list)

    @test.idempotent_id('8cf516ef-2114-48f1-907b-d32726c734d4')
    def test_list_domains(self):
        # Test to list domains
        domain_ids = list()
        fetched_ids = list()
        for _ in range(3):
            domain = self.domains_client.create_domain(
                data_utils.rand_name('domain'),
                description=data_utils.rand_name('domain-desc'))['domain']
            # Delete the domain at the end of this method
            self.addCleanup(self._delete_domain, domain['id'])
            domain_ids.append(domain['id'])
        # List and Verify Domains
        body = self.domains_client.list_domains()['domains']
        for d in body:
            fetched_ids.append(d['id'])
        missing_doms = [d for d in domain_ids if d not in fetched_ids]
        self.assertEqual(0, len(missing_doms))

    @test.attr(type='smoke')
    @test.idempotent_id('f2f5b44a-82e8-4dad-8084-0661ea3b18cf')
    def test_create_update_delete_domain(self):
        d_name = data_utils.rand_name('domain')
        d_desc = data_utils.rand_name('domain-desc')
        domain = self.domains_client.create_domain(
            d_name, description=d_desc)['domain']
        self.addCleanup(self._delete_domain, domain['id'])
        self.assertIn('id', domain)
        self.assertIn('description', domain)
        self.assertIn('name', domain)
        self.assertIn('enabled', domain)
        self.assertIn('links', domain)
        self.assertIsNotNone(domain['id'])
        self.assertEqual(d_name, domain['name'])
        self.assertEqual(d_desc, domain['description'])
        self.assertEqual(True, domain['enabled'])
        new_desc = data_utils.rand_name('new-desc')
        new_name = data_utils.rand_name('new-name')

        updated_domain = self.domains_client.update_domain(
            domain['id'], name=new_name, description=new_desc)['domain']
        self.assertIn('id', updated_domain)
        self.assertIn('description', updated_domain)
        self.assertIn('name', updated_domain)
        self.assertIn('enabled', updated_domain)
        self.assertIn('links', updated_domain)
        self.assertIsNotNone(updated_domain['id'])
        self.assertEqual(new_name, updated_domain['name'])
        self.assertEqual(new_desc, updated_domain['description'])
        self.assertEqual(True, updated_domain['enabled'])

        fetched_domain = self.domains_client.show_domain(
            domain['id'])['domain']
        self.assertEqual(new_name, fetched_domain['name'])
        self.assertEqual(new_desc, fetched_domain['description'])
        self.assertEqual(True, fetched_domain['enabled'])

    @test.idempotent_id('036df86e-bb5d-42c0-a7c2-66b9db3a6046')
    def test_create_domain_with_disabled_status(self):
        # Create domain with enabled status as false
        d_name = data_utils.rand_name('domain')
        d_desc = data_utils.rand_name('domain-desc')
        domain = self.domains_client.create_domain(
            d_name, description=d_desc, enabled=False)['domain']
        self.addCleanup(self.domains_client.delete_domain, domain['id'])
        self.assertEqual(d_name, domain['name'])
        self.assertFalse(domain['enabled'])
        self.assertEqual(d_desc, domain['description'])

    @test.idempotent_id('2abf8764-309a-4fa9-bc58-201b799817ad')
    def test_create_domain_without_description(self):
        # Create domain only with name
        d_name = data_utils.rand_name('domain')
        domain = self.domains_client.create_domain(d_name)['domain']
        self.addCleanup(self._delete_domain, domain['id'])
        self.assertIn('id', domain)
        expected_data = {'name': d_name, 'enabled': True}
        self.assertIsNone(domain['description'])
        self.assertDictContainsSubset(expected_data, domain)


class DefaultDomainTestJSON(base.BaseIdentityV3AdminTest):

    @classmethod
    def resource_setup(cls):
        cls.domain_id = CONF.identity.default_domain_id
        super(DefaultDomainTestJSON, cls).resource_setup()

    @test.attr(type='smoke')
    @test.idempotent_id('17a5de24-e6a0-4e4a-a9ee-d85b6e5612b5')
    def test_default_domain_exists(self):
        domain = self.domains_client.show_domain(self.domain_id)['domain']

        self.assertTrue(domain['enabled'])
