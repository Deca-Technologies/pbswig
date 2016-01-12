import sys
import os
import errno
import os.path
from distutils.cmd import Command
from distutils.command.build import build as _build
from distutils.command.install import install as _install
from distutils.errors import DistutilsSetupError
from distutils.core import Extension
import subprocess


def which(program):
    import os

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def validate_pbswig_protocols(dist, attr, value):
    if not hasattr(value, "__getitem__") or not hasattr(value, "__iter__"):
        raise DistutilsSetupError("%r must be a list of paths" % attr)


class build_pbswig(Command):
    description = "generate Protocol Buffers extensions"

    user_options = [
        ('protobuf-compiler=', None,
         "specify protocol buffer compiler"),
        ('build-temp=', 't',
         "directory for temporary files (build by-products)"),
    ]

    def initialize_options(self):
        self.protobuf_compiler = None
        self.build_temp = None

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_temp', 'build_temp'))
        if not self.protobuf_compiler:
            self.protobuf_compiler = 'protoc'
        assert (which(self.protobuf_compiler) is not None), (
            'Protocol buffer compiler %s does not exist.'
            % self.protobuf_compiler)

    def run(self):
        print("generating pbswig protocol bindings")
        protocols = getattr(self.distribution, "pbswig_protocols", None)
        if not protocols:
            print("No protocols to build")
            return

        for protocol in protocols:
            command = [which(self.protobuf_compiler)]
            pbswig_plugin = os.path.join(os.path.dirname(sys.executable),
                                         'pbswig_plugin')
            command.append('--plugin=protoc-gen-custom=' + pbswig_plugin)
            pbout_dir = os.path.join(self.build_temp, 'pb_src')
            command.append('--custom_out=' + pbout_dir)
            command.append('--cpp_out=' + pbout_dir)
            command.append(protocol)

            try:
                os.makedirs(pbout_dir)
            except OSError as exc:
                if exc.errno == errno.EEXIST and os.path.isdir(pbout_dir):
                    pass
                else:
                    raise

            subprocess.check_call(command,
                                  stdout=sys.stdout,
                                  stderr=sys.stdout)


def register_exts(dist, build_temp):
    print("registering pbswig protocol binding extensions")
    protocols = getattr(dist, "pbswig_protocols", None)
    if not protocols:
        return
    pbout_dir = os.path.join(build_temp, 'pb_src')
    for protocol in protocols:
        proto_name = os.path.basename(protocol).strip('.proto')
        package = os.path.dirname(protocol).replace('/', '.')
        ext = Extension(
            package + '._' + proto_name + '_pb',
            [os.path.join(pbout_dir,
                          protocol.replace('.proto', '.pb.cc')),
             os.path.join(pbout_dir,
                          proto_name + '.pb.i')],
            include_dirs=[pbout_dir,
                          os.path.join(pbout_dir, os.path.dirname(protocol))],
            libraries=['protobuf'],
            swig_opts=['-c++']
        )
        if dist.ext_modules is None:
            dist.ext_modules = [ext]
        else:
            dist.ext_modules.append(ext)


def copy_swig_modules(dist, build_temp, build_lib, copy_file):
    print("copying pbswig protocol binding modules")
    protocols = getattr(dist, "pbswig_protocols", None)
    if not protocols:
        return
    pbout_dir = os.path.join(build_temp, 'pb_src')
    for protocol in protocols:
        proto_name = os.path.basename(protocol).strip('.proto')
        py_path = os.path.join(
            build_lib,
            os.path.dirname(protocol),
            proto_name + '_pb.py'
        )
        copy_file(
            os.path.join(pbout_dir, proto_name + '_pb.py'),
            py_path,
            preserve_mode=0
        )


def copy_swig_includes(dist, build_temp, build_lib, copy_file):
    print("copying pbswig protocol includes")
    protocols = getattr(dist, "pbswig_protocols", None)
    if not protocols:
        return
    pbout_dir = os.path.join(build_temp, 'pb_src')
    for protocol in protocols:
        include_dir = os.path.join(
            build_lib, os.path.dirname(protocol), 'include')
        try:
            os.makedirs(include_dir)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(include_dir):
                pass
            else:
                raise

        proto_name = os.path.basename(protocol).strip('.proto')
        copy_file(
            os.path.join(
                pbout_dir,
                os.path.dirname(protocol),
                proto_name + '.pb.h'),
            os.path.join(
                include_dir,
                proto_name + '.pb.h'),
            preserve_mode=0
        )


class build_cmd(_build):
    def run(self):
        register_exts(
            self.distribution,
            self.build_temp)
        self.run_command('build_py')
        self.run_command('build_pbswig')
        self.run_command('build_ext')
        copy_swig_modules(
            self.distribution,
            self.build_temp,
            self.build_lib,
            self.copy_file
        )
        copy_swig_includes(
            self.distribution,
            self.build_temp,
            self.build_lib,
            self.copy_file
        )
        _build.run(self)

    def has_pbswig_protocols(self):
        return hasattr(self.distribution, "pbswig_protocols")


class install_cmd(_install):
    pass
