import dnsupdate
import unittest
from yaml import load

class ConfigTest(unittest.TestCase):

    def _parse_address_provider_web(self, config):
        config = load(config)
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
        """)
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
        """)
        self.assertRaises(TypeError, dnsupdate._parse_address_provider, config)
    
    def test_parse_address_provider_invalid_class(self):
        config = load("""
            type: InvalidClass
            args:
                invalid: invalid
        """)
        self.assertRaises(KeyError, dnsupdate._parse_address_provider, config)

    def _parse_dns_service_staticurl(self, config):
        config = load(config)
        service, providers = dnsupdate._parse_dns_service(config)
        self.assertIsInstance(service, dnsupdate.StaticURL)
        self.assertEqual(service.ipv4_url, 'ipv4_test_url')
        self.assertEqual(service.ipv6_url, 'ipv6_test_url')
        return service, providers

    def test_parse_dns_service_staticurl(self):
        config = """
            type: StaticURL
            args:
                ipv4_url: ipv4_test_url
                ipv6_url: ipv6_test_url
        """
        service, providers = self._parse_dns_service_staticurl(config)
        self.assertDictEqual(providers, dict())
        
    def test_parse_dns_service_staticurl_shorthand(self):
        config = """
            StaticURL("ipv4_test_url", "ipv6_test_url")
        """
        self._parse_dns_service_staticurl(config)

    def test_parse_dns_service_staticurl_ipv4_address_provider(self):
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
        service, providers = self._parse_dns_service_staticurl(config)
        self.assertIsInstance(providers['ipv4'], dnsupdate.Web)
        self.assertIsNone(providers.get('ipv6'))
        
    def test_parse_dns_service_staticurl_single_address_provider(self):
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
        service, providers = self._parse_dns_service_staticurl(config)
        self.assertIsInstance(providers['ipv4'], dnsupdate.Web)
        self.assertEqual(providers['ipv4'], providers['ipv6'])
    
class CacheTest(unittest.TestCase):
    
    def test_load_empty_cache(self):
        cache = dnsupdate._load_cache('/invalid_dir/invalid_file.cache')
        self.assertListEqual(cache, list())
        
# vim: ts=4:ps=4:et
