import os
import sys
from distutils.cmd import Command
from setuptools import setup


class BaseBuildDocs(Command):
    user_options = [
        ("builder=", "b", "Builder to run"),
        ("sourcedir=", "s", "Source directory"),
        ("outdir=", "o", "Output directory"),
    ]

    def initialize_options(self):
        self.builder = "html"
        self.sourcedir = "docs"
        self.outdir = "build/docs"

    def finalize_options(self):
        pass

    def _get_sphinx_args(self):
        return ["-b", self.builder, self.sourcedir, os.path.join(self.outdir, self.builder)]


class BuildDocs(BaseBuildDocs):
    description = "Build documentation using Sphinx"

    def run(self):
        try:
            try:
                import sphinx.cmd.build

                sphinx.cmd.build.main(self._get_sphinx_args())
            except ImportError:
                # Compatibility with sphinx < 1.7.0
                import sphinx

                sphinx.main([""] + self._get_sphinx_args())
        except SystemExit:
            # Prevent sphinx from exiting
            pass


class AutoBuildDocs(BaseBuildDocs):
    description = "Automatically rebuild documentation when files change"

    def run(self):
        import sphinx_autobuild

        oldsysargv = sys.argv
        # sphinx-autobuild's main function does not take parameters
        sys.argv = [""] + self._get_sphinx_args()
        sys.argv.extend(
            [
                "-z",
                ".",  # Watch source directory
                "-i",
                "*.goutputstream*",  # Ignore gedit temp files
                "-i",
                ".idea/*",  # Ignore PyCharm files
                "-i",
                ".git/*",  # Ignore git directory
            ]
        )
        try:
            sphinx_autobuild.main()
        except SystemExit:
            # Prevent sphinx from exiting
            pass
        sys.argv = oldsysargv


setup(cmdclass={"build_docs": BuildDocs, "autobuild_docs": AutoBuildDocs})

# vim: ts=4:ps=4:et
