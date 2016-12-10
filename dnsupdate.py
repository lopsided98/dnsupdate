#!/usr/bin/env python3

import sys

if sys.version_info[0] != 3 or sys.version_info[1] < 5:
    sys.exit("dnsupdate requires Python version 3.5 or newer")

import requests
import yaml
import ipaddress
from ipaddress import IPv4Address, IPv6Address
import os.path
import argparse

class UpdateException(Exception):
    pass
    
class UpdateClientException(UpdateException):
    pass
    
class UpdateServiceException(UpdateException):
    pass
    
class ConfigException(Exception):
    pass

class AddressProvider:
    def ipv4(self):
        return None
    def ipv6(self):
        return None

class DNSService:
    def update_ipv4(address):
        raise NotImplementedError('%s does not support IPv4' % __name__)
    def update_ipv6(address):
        raise NotImplementedError('%s does not support IPv6' % __name__)

class ComcastX1(AddressProvider):

    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password

    def ipv4(self):
        from bs4 import BeautifulSoup
    
        login = requests.post('http://%s/check.php' % self.ip, 
                             {'username': self.username, 'password' : self.password})
        auth = login.cookies

        ip_page = requests.get('http://%s/comcast_network.php' % self.ip, cookies=auth)

        ip_page = BeautifulSoup(ip_page.text, "html.parser")

        elem = ip_page.find(text="WAN IP Address (IPv4):")
        return ipaddress.IPv4Address(elem.parent.find_next("span", class_='value').text)

class Web(AddressProvider):
    def __init__(self, ipv4_url='https://ipv4.icanhazip.com/',
                       ipv6_url='https://ipv6.icanhazip.com/'):
        self.ipv4_url = ipv4_url
        self.ipv6_url = ipv6_url

    def ipv4(self):
        return IPv4Address(requests.get(self.ipv4_url).text.rstrip())

    def ipv6(self):
        return IPv6Address(requests.get(self.ipv6_url).text.rstrip())

class Local(AddressProvider):
    def __init__(self, interface):
        import netifaces
        self.interface = interface
        self.addresses = netifaces.ifaddresses(interface)

    def ipv4(self):
        import netifaces
        return next(filter(lambda a : a.is_global,
                    map(lambda aStr : IPv4Address(aStr['addr']),
                    self.addresses[netifaces.AF_INET])), None)

    def ipv6(self):
        import netifaces
        return next(filter(lambda a : a.is_global,
                    map(lambda aStr : IPv6Address(aStr['addr'].split('%', 1)[0]),
                    self.addresses[netifaces.AF_INET6])), None)

class StaticURL(DNSService):
    def __init__(self, ipv4_url, ipv6_url = None):
        self.ipv4_url = ipv4_url
        self.ipv6_url = ipv6_url

    def update_ipv4(self, address=None):
        requests.get(self.ipv4_url)

    def update_ipv6(self, address=None):
        requests.get(self.ipv6_url)

class FreeDNS(DNSService):
    def __init__(self, ipv4_key, ipv6_key = None):
        self.ipv4_key = ipv4_key
        self.ipv6_key = ipv6_key

    def __update(self, update_url, address):
        # Ask for json response
        r = requests.get(update_url, params={'content-type': 'json', 'ip': address})
        if r.status_code == requests.codes.ok:
            r = r.json()
            # Check for error
            if 'errorno' in r:
                # Throw exception using message from response
                raise UpdateException(r.get('summary', "Unknown error"))
            else:
                # List of domains that were updated
                targets = r.get('targets', None)
                if not targets is None or len(r['targets']) == 0:
                    # Return True if ip was updated (status 0). Status 100 means no change.
                    return targets[0].get('statuscode', None) == 0
                else:
                    raise UpdateException("Response did not include status.")
        else:
            r.raise_for_status()
            return False;

    def update_ipv4(self, address):
        return self.__update('https://sync.afraid.org/u/%s/' % self.ipv4_key, address)

    def update_ipv6(self, address):
        return self.__update('https://v6.sync.afraid.org/u/%s/' % self.ipv6_key, address)

class StandardService(DNSService):
    def __init__(self, service_ipv4, service_ipv6, username, password, hostname):
        self.service_ipv4 = service_ipv4
        self.service_ipv6 = service_ipv6
        self.username = username
        self.password = password
        self.hostname = hostname

    def __update(self, service_host, address):
        r = requests.get('https://%s/nic/update' % service_host,
                     auth=(self.username, self.password),
                     params={'myip': address, 'hostname': self.hostname})
        status = r.text.split(' ', 1)[0]
        if status == 'good':
            return True
        elif status == 'nochg':
            return False
        elif status == 'badauth' or r.status_code == 401:
            raise UpdateClientException('Incorrect login credentials')
        elif status == '!donator':
            raise UpdateClientException('Feature is only available to paying users')
        elif status == 'notfqdn':
            raise UpdateClientException('Incorrect hostname format')
        elif status == 'nohost':
            raise UpdateClientException('Hostname does not belong to this account')
        elif status == 'abuse':
            raise UpdateClientException('Hostname has been blocked for abuse')
        elif status == 'badagent':
            raise UpdateClientException('User agent or HTTP method was rejected')
        elif status == 'dnserr':
            raise UpdateServerException('Server DNS error encountered')
        elif status == '911':
            raise UpdateServerException('Server is not currently functioning correctly')
        else:
            raise UpdateException('Unknown response')

    def update_ipv4(self, address):
        return self.__update(self.service_ipv4, address)

    def update_ipv6(self, address):
        return self.__update(self.service_ipv6, address)

class NSUpdate(StandardService):
    def __init__(self, hostname, secret_key):
        super().__init__('ipv4.nsupdate.info', 'ipv6.nsupdate.info',
                                              hostname, secret_key, hostname)

def _load_config(arg_file):
    config_files = [arg_file, '~/.config/dnsupdate.conf', '/etc/dnsupdate.conf']
    for config_file in config_files:
        if not config_file is None:
            config_file = os.path.expanduser(config_file)
            try:
                with open(config_file, 'r') as fd:
                    return yaml.load(fd), config_file
            except:
                pass
    raise FileNotFoundError("Config file not found")

def _save_cache(cache_file, cache):
    with open(cache_file, 'w') as fd:
        yaml.dump(cache, fd)

def _load_cache(cache_file):
    try:
        with open(cache_file, 'r') as fd:
            return yaml.load(fd)
    except FileNotFoundError:
        return list()

def _parse_dns_service(service_root):
    if type(service_root) != str:
        class_name = service_root['type']
        service_class = globals()[class_name]
        if 'address_provider' in service_root:
            providers = _parse_address_provider_protos(service_root['address_provider'])
        else:
            providers = dict()
        return service_class(**service_root.get('args', {})), providers
    else:
        return eval(service_root), dict()

def _parse_address_provider(provider_root):
    if type(provider_root) != str:
        class_name = provider_root['type']
        provider_class = globals()[class_name]
        return provider_class(**provider_root.get('args', {}))
    else:
        return eval(provider_root)

def _parse_address_provider_protos(provider_root):
    providers = dict()
    for proto in ('ipv4', 'ipv6'):
        if proto in provider_root:
            providers[proto] = _parse_address_provider(provider_root[proto])
    if not ('ipv4' in providers or 'ipv6' in providers):
        providers['ipv4'] = providers['ipv6'] = _parse_address_provider(provider_root)
    return providers

def _parse_args():
    parser = argparse.ArgumentParser(description="Dynamic DNS update client")
    parser.add_argument('config', help="the config file to use", nargs='?')
    parser.add_argument('-f', '--force-update',
        help=("force an update to occur even if the address has not changed or a service has been disabled"),
        action='store_true', dest='force_update')
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = _parse_args()

    config, config_file = _load_config(args.config)
    cache_file = os.path.expanduser(config.get('cache_file', '~/.cache/dnsupdate.cache'))
    service_data_cache = _load_cache(cache_file)
    
    # Check and fix cache data format
    try:
        service_data_list = service_data_cache['dns_services']
    except:
        service_data_list = list()
        service_data_cache = dict()
        service_data_cache['dns_services'] = service_data_list
    
    # Enable all services if the config file has been updated
    new_mtime = os.path.getmtime(config_file)
    force_enable = (service_data_cache.get('mtime', None) != new_mtime or
                   args.force_update)
    service_data_cache['mtime'] = new_mtime
    
    # Read global address provider from config, and use Web by default
    global_providers = _parse_address_provider_protos(config.get('address_provider', { 'type': 'Web' }))
    
    # Cache of addresses from providers to prevent duplicate lookups
    new_addresses = dict()
    
    services = config['dns_services']
    for i, service_root in enumerate(services):
        service, providers = _parse_dns_service(service_root)
        # Merge global and local providers
        providers = {**global_providers, **providers}
        
        # Get data for service from saved data, or create it
        if i < len(service_data_list):
            service_data = service_data_list[i]
        else:
            service_data = dict()
            service_data_list.append(service_data)

        for proto, provider in providers.items():
            if not provider is None:
                try:
                    print("Updating %s address of service %d..." % (proto, i))

                    service_proto_data = service_data.setdefault(proto, dict())
                    if force_enable or service_proto_data.setdefault('enabled', True):
                        # Get updated address
                        if provider in new_addresses and proto in new_addresses[provider]:
                            new_address = new_addresses[provider][proto]
                        else:
                            # Call ipv4() or ipv6() method
                            new_address = getattr(provider, proto)()
                            if not provider in new_addresses:
                                new_addresses[provider] = {proto: new_address}
                            else:
                                new_addresses[provider][proto] = new_address
                        # Get old address
                        old_address = service_proto_data.get('address', None)
                        if str(new_address) != old_address or args.force_update:
                            try:
                                getattr(service, 'update_%s' % proto)(new_address)
                                service_proto_data['address'] = str(new_address)
                                service_proto_data['enabled'] = True
                                print("Update successful.")
                            except UpdateClientException as e:
                                print(("Error: %s") % e, file=sys.stderr)
                                print(("Update failed due to a configuration error. "
                                       "Service will be disabled until the configuration "
                                       "has been fixed."), file=sys.stderr)
                                service_proto_data['enabled'] = False
                            except UpdateException as ue:
                                print(("Error: %s") % ue, file=sys.stderr)
                        else:
                            print("Address has not changed, no update needed.")
                    else:
                        print(("Service has been disabled due to a previous client error. "
                               "Please fix your configuration and try again."),
                               file=sys.stderr)
                except Exception as e:
                    print(("Error: %s") % e, file=sys.stderr)
    
    # Delete any extra services from the cache
    del service_data_list[len(services):]
    
    _save_cache(cache_file, service_data_cache)

if __name__ == '__main__':
    main()

# vim: ts=4:ps=4:et
