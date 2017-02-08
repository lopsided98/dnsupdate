.. py:module:: dnsupdate

==================
Configuration File
==================

**dnsupdate** is configured using a single YAML configuration file. This file
can specified on the command line, or placed at either
``~/.config/dnsupdate.conf`` or ``/etc/dnsupdate.conf``.

The available options are documented below.

``address_provider``
--------------------

Controls how **dnsupdate** obtains IP addresses. If this option is not
specified, a web service is used. When specified at the root of the file, this
option applies to all DNS services.

Internally, address providers are Python classes which are initialized using
this configuration option.

::

    address_provider:
        type: ClassName;
        args:
            arg1: value1;
            arg2: value2;
            

``type`` specifies the name of the class, while ``args`` is a list of
constructor arguments.

Optionally, a shorthand notation can be used, which allows you to directly call
the class's constructor:

::

    address_provider: ClassName(value1, value2)

In this case, the option value is simply passed to ``eval()``, so it is
possible to evaluate arbitrary Python code.

Address providers can be specified separately for IPv4 and IPv6 in this
manner:

::

    address_provider:
        ipv4:
            type: ...
            args:
                ...
        ipv6:
            type: ...
            args:
                ...

If only one of the two protocols is configured, the other protocol is disabled
(unless a specific service overrides this option).

Default: :class:`Web()`

--------------

``dns_services``
----------------

A list of services to update. Each service is represented internally as a
Python class. The arguments specified in the configuration are directly passed
to the class's constructor.

It is also possible to override the global address provider for a specific
entry, using the same format as the global ``address_provider`` option. If only
one address provider protocol (IPv4 or IPv6) is specified, the other is
inherited from the global configuration. It is possible to disable a protocol
that was configured globally by assigning it the value ``None``. See
``examples/provider_override.conf``.

::

    dns_services:
        - type: ServiceClassName1
          address_provider: <see above>
          args:
              arg1: value1
              arg2: value2
        - type: ServiceClassName2
          args:
              arg1: value1
              arg2: value2
        ...

The shorthand constructor notation can also be used to initialize a DNS
service.

--------------

``cache_file``
--------------

Path to the file where **dnsupdate** will store information about the
configured DNS services, such as their addresses and whether they are enabled.
The specified file must be writable by **dnsupdate**.

Default: ``~/.cache/dnsupdate.cache``
