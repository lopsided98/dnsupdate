=========
dnsupdate
=========
----------------------------------------
A modern and flexible dynamic DNS client
----------------------------------------
   
.. image:: https://travis-ci.org/lopsided98/dnsupdate.svg?branch=master
   :target: https://travis-ci.org/lopsided98/dnsupdate
   
.. image:: https://readthedocs.org/projects/dnsupdate/badge/?version=latest
   :target: http://dnsupdate.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
                

**dnsupdate** is a dynamic DNS client that has first-class support for IPv6 and
aims to be easily configurable to meet the needs of any situation. Unlike most
other dynamic DNS clients, **dnsupdate** has been designed from the
start to support IPv6 and many different update services. It is written in
Python and configured using YAML, making it easy to use and extend.

Features
--------

* Built-in support for FreeDNS_, nsupdate.info_, as well as any service that
  uses the standard `DynDNS protocol`_
* IPv6 support
* Simple YAML configuration file
* Obtain addresses from a web service, router or local interface
* Only submits an update if the address has changed
* Respects API return values to avoid abuse bans

.. _FreeDNS: https://freedns.afraid.org/
.. _nsupdate.info: https://nsupdate.info/
.. _DynDNS protocol: https://help.dyn.com/remote-access-api/

Installation
------------

``pip install dnsupdate``

Alternatively, you can simply download and run
``dnsupdate.py``.

It is also `available on the Arch Linux
AUR <https://aur.archlinux.org/packages/dnsupdate/>`_.

Dependencies
^^^^^^^^^^^^

- Python ≥3.5
- requests_
- PyYAML_
- `Beautiful Soup`_ (optional, for scraping router pages)
- netifaces_ (optional, for getting local addresses)

.. _requests: http://docs.python-requests.org/en/master/
.. _PyYAML: http://pyyaml.org/
.. _Beautiful Soup: https://www.crummy.com/software/BeautifulSoup/
.. _netifaces: https://bitbucket.org/al45tair/netifaces

Configuration
-------------

**dnsupdate** is configured using a single `YAML file`_.
The path to the file can be specified on the command line. If not,
**dnsupdate** will try to use ``~/.config/dnsupdate.conf`` and
``/etc/dnsupdate.conf``, in that order.

.. _YAML file: http://yaml.org/

Most users will likely be satisfied with a simple configuration like
this:

::

    dns_services:
        - type: NSUpdate
          args:
              hostname: example.nsupdate.info
              secret_key: 26Yg7wUhxo

More examples are available in the ``examples/`` directory.

Full documentation is available here: https://dnsupdate.readthedocs.io/

Usage
-----

::

    usage: dnsupdate [-h] [-f] [-V] [config]

    Dynamic DNS update client

    positional arguments:
      config              the config file to use

    optional arguments:
      -h, --help          show this help message and exit
      -f, --force-update  force an update to occur even if the address has not
                          changed or a service has been disabled
      -V, --version       show program's version number and exit
                          
Documentation
-------------

Documentation is `available online`_, but it can also be built locally by running:

``python3 setup.py build_docs``

.. _available online: https://dnsupdate.readthedocs.io/
