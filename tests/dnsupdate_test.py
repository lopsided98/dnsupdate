import unittest

from yaml import load

import dnsupdate


class ConfigTest(unittest.TestCase):
    def _parse_address_provider_web(self, config):
        config = load(config, dnsupdate._ConfigLoader)
        provider = dnsupdate._parse_address_provider(config)
        self.assertIsInstance(provider, dnsupdate.Web)
        self.assertEqual(provider.ipv4_url, 'ipv4_test_url')
        self.assertEqual(provider.ipv6_url, 'ipv6_test_url')

    def test_parse_address_provider_web(self):
        config = """
            type: Web
            args:
                ipv4_url: ipv4_test_url
                ipv6_url: ipv6_test_url
        """
        self._parse_address_provider_web(config)

    def test_parse_address_provider_web_quotes(self):
        config = """
            type: Web
            args:
                ipv4_url: "ipv4_test_url"
                ipv6_url: 'ipv6_test_url'
        """
        self._parse_address_provider_web(config)

    def test_parse_address_provider_web_shorthand_no_quotes(self):
        config = load("""
            Web(ipv4_test_url, ipv6_test_url)
        """, dnsupdate._ConfigLoader)
        self.assertRaises(NameError, dnsupdate._parse_address_provider, config)

    def test_parse_address_provider_web_shorthand_quotes(self):
        config = """
            Web("ipv4_test_url", 'ipv6_test_url')
        """
        self._parse_address_provider_web(config)

    def test_parse_address_provider_web_invalid_arg(self):
        config = load("""
            type: Web
            args:
                invalid: invalid
        """, dnsupdate._ConfigLoader)
        self.assertRaises(TypeError, dnsupdate._parse_address_provider, config)

    def test_parse_address_provider_invalid_class(self):
        config = load("""
            type: InvalidClass
            args:
                invalid: invalid
        """, dnsupdate._ConfigLoader)
        self.assertRaises(KeyError, dnsupdate._parse_address_provider, config)

    def _parse_dns_service_static_url(self, config):
        config = load(config, dnsupdate._ConfigLoader)
        service, providers = dnsupdate._parse_dns_service(config)
        self.assertIsInstance(service, dnsupdate.StaticURL)
        self.assertEqual(service.ipv4_url, 'ipv4_test_url')
        self.assertEqual(service.ipv6_url, 'ipv6_test_url')
        return service, providers

    def test_parse_dns_service_static_url(self):
        config = """
            type: StaticURL
            args:
                ipv4_url: ipv4_test_url
                ipv6_url: ipv6_test_url
        """
        service, providers = self._parse_dns_service_static_url(config)
        self.assertDictEqual(providers, dict())

    def test_parse_dns_service_static_url_shorthand(self):
        config = """
            StaticURL("ipv4_test_url", "ipv6_test_url")
        """
        self._parse_dns_service_static_url(config)

    def test_parse_dns_service_static_url_ipv4_address_provider(self):
        config = """
            type: StaticURL
            address_provider:
                ipv4:
                    type: Web
                    args:
                        ipv4_url: ipv4_test_url
                        ipv6_url: ipv6_test_url
            args:
                ipv4_url: ipv4_test_url
                ipv6_url: ipv6_test_url
        """
        service, providers = self._parse_dns_service_static_url(config)
        self.assertIsInstance(providers['ipv4'], dnsupdate.Web)
        self.assertIsNone(providers.get('ipv6'))

    def test_parse_dns_service_static_url_single_address_provider(self):
        config = """
            type: StaticURL
            address_provider:
                type: Web
                args:
                    ipv4_url: ipv4_test_url
                    ipv6_url: ipv6_test_url
            args:
                ipv4_url: ipv4_test_url
                ipv6_url: ipv6_test_url
        """
        service, providers = self._parse_dns_service_static_url(config)
        self.assertIsInstance(providers['ipv4'], dnsupdate.Web)
        self.assertEqual(providers['ipv4'], providers['ipv6'])

    def test_parse_include(self):
        config = """
           test_key: !include tests/include.yml
        """
        data = load(config, dnsupdate._ConfigLoader)
        self.assertIn('test_key', data)
        self.assertIn('included_option', data['test_key'])
        self.assertEqual(data['test_key']['included_option'], 'included_value')

    def test_parse_include_text(self):
        config = """
            test_key: !include_text tests/include.txt
        """
        data = load(config, dnsupdate._ConfigLoader)
        self.assertIn('test_key', data)
        self.assertEqual(data['test_key'], 'test string\nline two')


class CacheTest(unittest.TestCase):
    def test_load_empty_cache(self):
        cache = dnsupdate._load_cache('/invalid_dir/invalid_file.cache')
        self.assertDictEqual(cache, dict())

# vim: ts=4:ps=4:et
