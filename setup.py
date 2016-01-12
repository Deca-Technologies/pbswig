import setuptools

setuptools.setup(
    name='pbswig',
    version="0.1.1",
    author='Craig Bishop',
    author_email='craig.bishop@decatechnologies.com',
    description="Plugin for Google protocol buffers to Python bindings for C++"
                "protobuf objects",
    url="https://github.com/Deca-Technologies/pbswig",
    packages=['pbswig'],
    include_package_data=True,
    package_data={'pbswig': [
        'templates/**',
    ]},
    install_requires=['jinja2', 'protobuf'],
    scripts=['pbswig/pbswig_plugin'],
    entry_points={
        "distutils.commands": [
            "build_pbswig = pbswig.build:build_pbswig"
        ],
        "distutils.setup_keywords": [
            "pbswig_protocols = pbswig.build:validate_pbswig_protocols"
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Operating System :: OS Independent",
        "Programming Language :: C++",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Build Tools"
    ])
