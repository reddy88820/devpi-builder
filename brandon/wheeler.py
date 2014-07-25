"""
Functionality for building wheels
"""

import glob
import os.path as path
import shutil
import subprocess
import tempfile

import wheel.install
import wheel.util


__author__ = 'mbach'


class Builder(object):
    """
    Provides a context in which wheels can be generated. If the context goes out of scope all created files will be
    removed.
    """

    def __enter__(self):
        self.scratch_dir = tempfile.mkdtemp()
        self.wheelhouse = path.join(self.scratch_dir, 'wheels')
        self.builddir = path.join(self.scratch_dir, 'build')
        self.cachedir = path.join(self.scratch_dir, 'cache')
        return lambda *args: self.build(*args)

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.scratch_dir)

    def _find_wheel(self, name, version):
        """
        Find a wheel with the given name and version
        """
        candidates = [
            wheel.install.WheelFile(filename) for filename in glob.glob(path.join(self.wheelhouse, '*.whl'))
        ]
        matches = wheel.util.matches_requirement('{}=={}'.format(name, version), candidates)
        return str(matches[0])

    def build(self, project, version):
        """
        Build a wheel for the given version of the given project.

        :param project: The name of the project
        :param version: The version to generate the wheel for
        :return: The path of the build wheel. Valid until the context is exited.
        """
        subprocess.check_call([
            'pip', 'wheel',
            '--wheel-dir=' + self.wheelhouse,
            '--download-cache=' + self.cachedir,
            '--build=' + self.builddir,
            '{}=={}'.format(project, version)
        ])
        return self._find_wheel(project, version)