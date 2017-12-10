import os
import sys
from distutils.cmd import Command
from setuptools import setup, find_packages

import dnsupdate


class BaseBuildDocs(Command):
    user_options = [
        ('builder=', 'b', "Builder to run"),
        ('sourcedir=', 's', "Source directory"),
        ('outdir=', 'o', "Output directory")
    ]

    def initialize_options(self):
        self.builder = 'html'
        self.sourcedir = 'docs'
        self.outdir = 'build/docs'

    def finalize_options(self):
        pass

    def _get_sphinx_args(self):
        return ['', '-b', self.builder, self.sourcedir, os.path.join(self.outdir, self.builder)]


class BuildDocs(BaseBuildDocs):
    description = "Build documentation using Sphinx"

    def run(self):
        import sphinx
        try:
            sphinx.main(self._get_sphinx_args())
        except SystemExit:
            # Prevent sphinx from exiting
            pass


class AutoBuildDocs(BaseBuildDocs):
    description = "Automatically rebuild documentation when files change"

    def run(self):
        import sphinx_autobuild
        oldsysargv = sys.argv
        # sphinx-autobuild's main function does not take parameters
        sys.argv = self._get_sphinx_args()
        sys.argv.extend([
            '-z', '.',  # Watch source directory
            '-i', '*.goutputstream*',  # Ignore gedit temp files
            '-i', '.idea/*',  # Ignore PyCharm files
            '-i', '.git/*' # Ignore git directory
        ])
        try:
            sphinx_autobuild.main()
        except SystemExit:
            # Prevent sphinx from exiting
            pass
        sys.argv = oldsysargv


setup(
    name="dnsupdate",
    version=dnsupdate.__version__,
    py_modules=['dnsupdate'],
    install_requires=[
        'PyYAML',
        'requests'
    ],
    extras_require={
        "Router-Address-Scraping": ['beautifulsoup4'],
        "Local-Address-Provider": ['netifaces'],
        'Build-Docs': ['sphinx-argparse']
    },
    python_requires='>=3.5',
    entry_points={
        'console_scripts': [
            'dnsupdate=dnsupdate:main',
        ],
    },
    test_suite='tests',

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
    long_description=open('README.rst', encoding='utf-8').read(),

    cmdclass={
        'build_docs': BuildDocs,
        'autobuild_docs': AutoBuildDocs
    }
)

# vim: ts=4:ps=4:et
