import setuptools
from distutils.core import Extension

import pbswig
# needed to workaround odd distutils behavior with SWIG
from pbswig.build import build_cmd, install_cmd

# needed to get include directory for C++ ext
import pbswig_example_model.example_pb

ext = Extension(
    'pbswig_example_pkg._pbswig_example_ext',  # must have underscore
    # source needs to be in package directory
    sources=['pbswig_example_pkg/pbswig_example_ext.cpp',
             'pbswig_example_pkg/pbswig_example_ext.i'],
    # grabs the include directory using a PBSWIG helper
    include_dirs=[pbswig.get_include(pbswig_example_model.example_pb)],
    swig_opts=['-c++'])

setuptools.setup(
    # needed to workaround odd distutils behavior with SWIG
    cmdclass={'build': build_cmd, 'install': install_cmd},
    name='pbswig_example_pkg',
    version='1.0',
    description='Example of pbswig usage in a package with extensions',
    author='Craig Bishop',
    author_email='craig.bishop@decatechnologies.com',
    packages=['pbswig_example_pkg'],
    ext_modules=[ext])
