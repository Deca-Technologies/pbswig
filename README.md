# PBSWIG
A Python wrapper generator for C++ Google Protocol Buffer specifications allowing seamless interop to python extensions.

## Introduction
Creating the data model for an application is always hard, especially if the application is split across a language barrier like Python-C++. Google Protocol Buffers provides an awesome way to specify a data schema and generate code in dozens of languages to handle it. However, it does not handle passing data across language barriers very well. The Python generated code creates Python representations when a protobuf is parsed, and the C++ code uses C++ class representations. Passing a Python object representation to a C++ extension function requires data translation or other complexity. PBSWIG makes this use case easy: it generates the C++ class hierarchy, and then wraps it for Python using SWIG. This way, when a protobuf object is passed to C++, only a pointer is passed and no translation is necessary.

The project consists of two main parts: a protobuf compiler plugin and some distutils extensions for building data model packages using it.

## License
MIT License; See LICENSE file.

## Requirements
- Google Protocol Buffers library for C++ with compiler and headers
    - On Mac OS: `brew install protobuf`
    - On Debian or Ubuntu: `apt-get install libprotobuf9 libprotobuf-dev protobuf-compiler`
- Python
- jinja2
- protobuf (Python protobuf package)

## Installation
`python setup.py install` as usual.

## Usage of the protobuf compiler plugin only
1. Create a .proto specification file (https://developers.google.com/protocol-buffers/docs/proto)
2. Make sure the Python bin directory is in the PATH so that `pbswig_plugin` is available
3. Run the protobuf compiler with the plugin: `protoc --plugin=protoc-gen-custom=$(which pbswig_plugin) --custom_out=<pbswig output dir> --cpp_out=<C++ protobuf output dir> <protocol>.proto`
4. Run SWIG to generate the C++ wrapper code: `swig -c++ -python <pbswig output dir>/<protocol>.pb.i`
5. Build C++ Python extension: `g++ -shared -lprotobuf -lpython -undefined suppress -flat_namespace -o _<protocol>_pb.so <pbswig output dir>/<protocol>.pb.cc <protocol>.pb_wrap.cxx`

## Usage of the pbswig distutil extensions
The steps below are illustrated with the two packages in the examples directory.

### For the package with the data model
This will create and install a Python package with a module created from the protobuf specification.

1. Create a .proto specification in the package directory
2. Create a setup.py file in the same directory as the package directory
3. Edit the contents of setup.py to look like (adjusted for your project):
```python
import setuptools

# needed to perform custom build steps
from pbswig.build import build_cmd, install_cmd

setuptools.setup(
    cmdclass={'build': build_cmd, 'install': install_cmd},  # unique to PBSWIG
    name='pbswig_example_model',
    version='1.0',
    description='Example of pbswig usage for data models',
    author='Craig Bishop',
    author_email='craig.bishop@decatechnologies.com',
    packages=['pbswig_example_model'],
    pbswig_protocols=[
        'pbswig_example_model/example.proto'  # unique to PBSWIG
        # list each proto file here
    ]
)
```
4. Run `python setup.py install`

### For the package with a C++ extension using the data model
This will create and install a package containing a C++ Python extension with a function that takes a protobuf object as an argument.

1. Create the C++ extension and other Python modules in the package directory
2. Create a setup.py file in the same directory as the package directory
3. Edit the contents of setup.py to look like (adjusted for your project):
```python
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
```
4. Run `python setup.py install`

### Using the packages together
Contents of example.py:
```python
# import the protobuf model
from pbswig_example_model import example_pb

# import the extension package that uses it
import pbswig_example_pkg

# create the model object in Python
say = example_pb.Say()
say.text = "Hello PBSWIG!"

# seamlessly pass it to the C++ extension
pbswig_example_pkg.say_it(say)
```

## TODO (Help Wanted)
- Make usage of distutils simpler and follow standards better
    - Eliminate need for `cmdclass={'build': build_cmd, 'install': install_cmd}` in setup call in protobuf setup.py
    - Eliminate need for `cmdclass={'build': build_cmd, 'install': install_cmd}` in extension setup.py (distutils doesn't copy the Python wrapper that SWIG generates with the native shared library to the build)
- Clean up Jinja templates
- Tests for generated wrapper code (not worried about SWIG generated wrapper or protobuf code)
    - Tests for RepeatedBasicFieldWrapper
    - Tests for RepeatedMessageFieldWrapper
- Generate Python 3 enums from protobuf enums (with a Python version switch to PBSWIG)
- Test with Python 3
