import os.path


def get_include(pb_module):
    return os.path.join(os.path.dirname(pb_module.__file__), 'include')
