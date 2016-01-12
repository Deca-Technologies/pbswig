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
