# dnsupdate

#### A modern and flexible dynamic DNS client

**dnsupdate** is a dynamic DNS client that has first-class support for IPv6 and
aims to be easily configurable to meet the needs of any situation. Unlike most
other dynamic DNS clients, **dnsupdate** has been designed from the start to 
support IPv6 and many different update services. It is written in Python and 
configured using YAML, making it easy to use and extend.

### Features
* Built-in support for [FreeDNS](https://freedns.afraid.org/), 
  [nsupdate.info](https://www.nsupdate.info/), as well as any service that uses
  the standard [DynDNS protocol](https://help.dyn.com/remote-access-api/)
* IPv6 support
* Simple YAML configuration file
* Obtain addresses from a web service, router or local interface
* Only submits an update if the address has changed
* Respects API return values to avoid abuse bans

### Installation

`pip install dnsupdate`

Alternatively, you can simply download and run [`dnsupdate.py`](dnsupdate.py).

It is also [available on the Arch Linux AUR](https://aur.archlinux.org/packages/dnsupdate/).

#### Dependencies
* Python &ge;3.5
* [requests](http://docs.python-requests.org/en/master/)
* [PyYAML](http://pyyaml.org/)
* [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) (optional, for scraping router pages)
* [netifaces](https://bitbucket.org/al45tair/netifaces) (optional, for getting local addresses)

### Configuration
**dnsupdate** is configured using a single [YAML file](http://yaml.org/). The
path to the file can be specified on the command line. If not, **dnsupdate**
will try to use `~/.config/dnsupdate.conf` and `/etc/dnsupdate.conf`, in that
order.

Most users will likely be satisfied with a simple configuration like this:
```
dns_services:
    - type: NSUpdate
      args:
          hostname: example.nsupdate.info
          secret_key: 26Yg7wUhxo
```

More examples are available in the `examples/` directory.

------

#### `address_provider`

Controls how **dnsupdate** obtains IP addresses. If this option is not
specified, a web service is used. When specified at the root of the file, this
option applies to all DNS services.

Internally, address providers are Python classes which are initialized using
this configuration option.

```
address_provider:
    type: ClassName;
    args:
	    arg1: value1;
	    arg2: value2;
        ...
```
`type` specifies the name of the class, while `args` is a list of constructor
arguments.

Optionally, a shorthand notation can be used, which allows you to directly call
the class's constructor:
```
address_provider: ClassName(value1, value2)
```
In this case, the option value is simply passed to `eval()`, so it is possible
to evaluate arbitrary Python code.

Address providers can be specified separately for IPv4 and IPv6 in this manner:
```
address_provider:
    ipv4:
        type: ...
        args:
    	    ...
    ipv6:
        type: ...
        args:
            ...
```

If only one of the two protocols is configured, the other protocol is disabled
(unless a specific service overrides this option).

Default: `Web()`

------

#### `dns_services`

A list of services to update. Each service is represented internally as a
Python class. The arguments specified in the configuration are directly passed
to the class's constructor.

It is also possible to override the global address provider for a specific
entry, using the same format as the global `address_provider` option. If only
one address provider protocol (IPv4 or IPv6) is specified, the other is
inherited from the global configuration. It is possible to disable a protocol
that was configured globally by assigning it the value `None`. See 
[`examples/protocol_override.conf`](examples/provider_override.conf).

```
dns_services:
    - type: ServiceClassName1
      address_provider: &lt;see above&gt;
      args:
          arg1: value1
          arg2: value2
    - type: ServiceClassName2
      args:
          arg1: value1
          arg2: value2
    ...
```

The shorthand constructor notation can also be used to initialize a DNS
service.

------

#### `cache_file`

Path to the file where **dnsupdate** will store information about the
configured DNS services, such as their addresses and whether they are enabled.
The specified file must be writable by **dnsupdate**.

Default: `~/.cache/dnsupdate.cache`

### Usage

```
dnsupdate [-h] [-f] [config]

positional arguments:
  config              the config file to use

optional arguments:
  -h, --help          show this help message and exit
  -f, --force-update  force an update to occur even if the address has not
                      changed or a service has been disabled
```



