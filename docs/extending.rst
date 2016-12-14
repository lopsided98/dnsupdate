.. py:module:: dnsupdate

===================
Extending dnsupdate
===================

**dnsupdate** is designed to make it easy to add new address providers and DNS
services.

If you add a new address provider, DNS service or any other feature that might
be useful to others, feel free to submit a pull request on GitHub_.

.. _GitHub: https://github.com/lopsided98/dnsupdate

Adding an address provider
---------------------------

To add support for a new address provider, add a new subclass of
:class:`AddressProvider` to the the module, and it will become available to use
in a configuration file.

.. autoclass:: AddressProvider
   :members:

Adding a DNS service
----------------------

Likewise, a new DNS service can be created by subclassing :class:`DNSService`.

.. autoclass:: DNSService
   :members:
   :special-members:
   :exclude-members: __weakref__
   
Update exceptions
^^^^^^^^^^^^^^^^^

.. autoclass:: UpdateException
   
.. autoclass:: UpdateClientException
   
.. autoclass:: UpdateServiceException
