from setuptools import setup, find_packages

setup(
    name="dnsupdate",
    version="0.1",
    py_modules=['dnsupdate'],
    install_requires=[
        'PyYAML',
        'requests'
    ],
    extras_require={
        "Router address scraping": ['beautifulsoup4'],
        "Local address provider": ['netifaces']
    },
    python_requires='>=3.5',
    entry_points={
        'console_scripts': [
            'dnsupdate=dnsupdate:main',
        ],
    },

    # metadata for upload to PyPI
    author="Ben Wolsieffer",
    author_email="benwolsieffer@gmail.com",
    description="A modern and flexible dynamic DNS client",
    license="GPLv3",
    keywords="dns",
    url="https://github.com/lopsided98/dnsupdate",
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Topic :: System :: Networking'
    ],
    long_description = open('README.rst').read(),
)

# vim: ts=4:ps=4:et
