#!/usr/bin/env python
#
# write by @snibug

import argparse
import distutils.spawn
import fnmatch
import multiprocessing
import os
import pipes
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib2

ALL = 'all'
ANDROID = 'android'
BUILD = 'build'
CHROMIUM = 'chromium'
CHROMIUM_PATH = 'chromium_path'
CLEAN = 'clean'
STELLITE_CLIENT_BINDER = 'stellite_client_binder'
CONFIGURE = 'configure'
DARWIN = 'darwin'
EXECUTABLE = 'executable'
IOS = 'ios'
LINUX = 'linux'
MAC = 'mac'
NODE_MODULE = 'node_module'
NODE_STELLITE = 'node_stellite'
QUIC_CLIENT = 'quic_client'
SHARED_LIBRARY = 'shared_library'
SIMPLE_CHUNKED_UPLOAD_CLIENT_BIN = 'simple_chunked_upload_client_bin'
STATIC_LIBRARY = 'static_library'
STELLITE_HTTP_CLIENT = 'stellite_http_client'
STELLITE_HTTP_CLIENT_BIN = 'stellite_http_client_bin'
STELLITE_HTTP_SESSION = 'stellite_http_session'
STELLITE_HTTP_SESSION_BIN = 'stellite_http_session_bin'
STELLITE_QUIC_SERVER_BIN = 'stellite_quic_server_bin'
TARGET_ARCH = 'target_arch'
UBUNTU = 'ubuntu'
UNITTEST = 'unittest'
WINDOWS = 'windows'

GIT_DEPOT = 'https://chromium.googlesource.com/chromium/tools/depot_tools.git'
NODE_MODULE_NAME = 'stellite.node'

GCLIENT_IOS = """
solutions = [
  {
    "managed": False,
    "name": "src",
    "url": "https://chromium.googlesource.com/chromium/src.git",
    "custom_deps": {},
    "deps_file": ".DEPS.git",
    "safesync_url": "",
  },
]
target_os = [\"ios\"]
target_os_only = \"True\"
"""

GCLIENT_ANDROID = """
solutions = [
  {
    "managed": False,
    "name": "src",
    "url": "https://chromium.googlesource.com/chromium/src.git",
    "custom_deps": {},
    "deps_file": ".DEPS.git",
    "safesync_url": "",
  },
]
target_os = [\"android\"]
target_os_only = \"True\"
"""

GN_ARGS_LINUX = """
disable_file_support = true
disable_ftp_support = true
is_component_build = false
target_cpu = "x64"
target_os = "linux"
"""

GN_ARGS_MAC = """
disable_file_support = true
disable_ftp_support = true
is_component_build = false
target_cpu = "x64"
target_os = "mac"
"""

GN_ARGS_IOS = """
disable_file_support = true
disable_ftp_support = true
enable_dsyms = false
enable_stripping = enable_dsyms
ios_enable_code_signing = false
is_component_build = false
is_official_build = false
target_cpu = "{target_cpu}"
target_os = "ios"
use_xcode_clang = is_official_build
use_platform_icu_alternatives = true
"""

GN_ARGS_ANDROID = """
disable_file_support = true
disable_ftp_support = true
is_clang = true
is_component_build = false
target_cpu = "{target_cpu}"
target_os = "android"
use_platform_icu_alternatives = true
"""

GN_ARGS_WINDOWS = """
is_component_build = {}
target_cpu = "x64"
target_os = "win"
"""

CHROMIUM_DEPENDENCY_DIRECTORIES = [
  'base',
  'build',
  'build_overrides',
  'buildtools',
  'components/url_matcher',
  'crypto',
  'gin',
  'net',
  'sdch',
  'testing',
  'third_party/WebKit',
  'third_party/apple_apsl',
  'third_party/binutils',
  'third_party/boringssl',
  'third_party/brotli',
  'third_party/ced',
  'third_party/closure_compiler',
  'third_party/drmemory',
  'third_party/icu',
  'third_party/instrumented_libraries',
  'third_party/jinja2',
  'third_party/libxml/',
  'third_party/llvm-build',
  'third_party/markupsafe',
  'third_party/modp_b64',
  'third_party/protobuf',
  'third_party/pyftpdlib',
  'third_party/pywebsocket',
  'third_party/re2',
  'third_party/tcmalloc',
  'third_party/tlslite',
  'third_party/yasm',
  'third_party/zlib',
  'tools',
  'url',
  'v8',
]

ANDROID_DEPENDENCY_DIRECTORIES = [
  'base',
  'build',
  'build_overrides',
  'buildtools',
  'components/url_matcher',
  'crypto',
  'gin',
  'net',
  'sdch',
  'testing',
  'third_party/WebKit',
  'third_party/accessibility_test_framework',
  'third_party/android_async_task',
  'third_party/android_crazy_linker',
  'third_party/android_data_chart',
  'third_party/android_media',
  'third_party/android_opengl',
  'third_party/android_platform',
  'third_party/android_protobuf',
  'third_party/android_support_test_runner',
  'third_party/android_swipe_refresh',
  'third_party/android_tools',
  'third_party/apache_velocity',
  'third_party/apple_apsl',
  'third_party/ashmem',
  'third_party/binutils',
  'third_party/boringssl',
  'third_party/bouncycastle',
  'third_party/brotli',
  'third_party/byte_buddy',
  'third_party/catapult',
  'third_party/ced',
  'third_party/closure_compiler',
  'third_party/colorama',
  'third_party/drmemory',
  'third_party/guava',
  'third_party/hamcrest',
  'third_party/icu',
  'third_party/icu4j',
  'third_party/ijar',
  'third_party/instrumented_libraries',
  'third_party/intellij',
  'third_party/jsr-305',
  'third_party/junit',
  'third_party/libxml/',
  'third_party/llvm-build',
  'third_party/mockito',
  'third_party/modp_b64',
  'third_party/objenesis',
  'third_party/ow2_asm',
  'third_party/protobuf',
  'third_party/pyftpdlib',
  'third_party/pywebsocket',
  'third_party/re2',
  'third_party/robolectric',
  'third_party/sqlite4java',
  'third_party/tcmalloc',
  'third_party/tlslite',
  'third_party/yasm',
  'third_party/zlib',
  'tools',
  'url',
  'v8',
]

WINDOWS_DEPENDENCY_DIRECTORIES= [
  'base',
  'build',
  'build_overrides',
  'buildtools',
  'components/url_matcher',
  'crypto',
  'gin',
  'net',
  'sdch',
  'testing',
  'third_party/apple_apsl',
  'third_party/binutils',
  'third_party/boringssl',
  'third_party/brotli',
  'third_party/ced',
  'third_party/closure_compiler',
  'third_party/drmemory',
  'third_party/icu',
  'third_party/instrumented_libraries',
  'third_party/libxml/',
  'third_party/modp_b64',
  'third_party/protobuf',
  'third_party/pyftpdlib',
  'third_party/pywebsocket',
  'third_party/re2',
  'third_party/tcmalloc',
  'third_party/tlslite',
  'third_party/yasm',
  'third_party/zlib',
  'tools',
  'url',
  'v8',
]

MAC_EXCLUDE_OBJECTS = [
  'protobuf/protobuf_full/arena.o',
  'protobuf/protobuf_full/arenastring.o',
  'protobuf/protobuf_full/coded_stream.o',
  'protobuf/protobuf_full/common.o',
  'protobuf/protobuf_full/extension_set.o',
  'protobuf/protobuf_full/generated_message_util.o',
  'protobuf/protobuf_full/message_lite.o',
  'protobuf/protobuf_full/once.o',
  'protobuf/protobuf_full/repeated_field.o',
  'protobuf/protobuf_full/stringpiece.o',
  'protobuf/protobuf_full/stringprintf.o',
  'protobuf/protobuf_full/structurally_valid.o',
  'protobuf/protobuf_full/strutil.o',
  'protobuf/protobuf_full/time.o',
  'protobuf/protobuf_full/wire_format_lite.o',
  'protobuf/protobuf_full/zero_copy_stream.o',
  'protobuf/protobuf_full/zero_copy_stream_impl_lite.o',
  'protobuf/protobuf_full/statusor.o',
  'protobuf/protobuf_full/status.o',
  'protobuf/protobuf_full/bytestream.o',
  'protobuf/protobuf_full/int128.o',
]

IOS_EXCLUDE_OBJECTS = [
  'protobuf/protobuf_full/zero_copy_stream_impl_lite.o',
  'protobuf/protobuf_full/zero_copy_stream.o',
  'protobuf/protobuf_full/wire_format_lite.o',
  'protobuf/protobuf_full/strutil.o',
  'protobuf/protobuf_full/structurally_valid.o',
  'protobuf/protobuf_full/stringpiece.o',
  'protobuf/protobuf_full/repeated_field.o',
  'protobuf/protobuf_full/once.o',
  'protobuf/protobuf_full/stringprintf.o',
  'protobuf/protobuf_full/message_lite.o',
  'protobuf/protobuf_full/generated_message_util.o',
  'protobuf/protobuf_full/extension_set.o',
  'protobuf/protobuf_full/arena.o',
  'protobuf/protobuf_full/common.o',
  'protobuf/protobuf_full/coded_stream.o',
  'protobuf/protobuf_full/arenastring.o',
]

ANDROID_EXCLUDE_OBJECTS = [
]

LINUX_EXCLUDE_OBJECTS = [
  'protobuf/protobuf_full/arena.o',
  'protobuf/protobuf_full/arenastring.o',
  'protobuf/protobuf_full/atomicops_internals_x86_gcc.o',
  'protobuf/protobuf_full/bytestream.o',
  'protobuf/protobuf_full/coded_stream.o',
  'protobuf/protobuf_full/common.o',
  'protobuf/protobuf_full/extension_set.o',
  'protobuf/protobuf_full/generated_message_util.o',
  'protobuf/protobuf_full/int128.o',
  'protobuf/protobuf_full/message_lite.o',
  'protobuf/protobuf_full/once.o',
  'protobuf/protobuf_full/repeated_field.o',
  'protobuf/protobuf_full/status.o',
  'protobuf/protobuf_full/statusor.o',
  'protobuf/protobuf_full/stringpiece.o',
  'protobuf/protobuf_full/stringprintf.o',
  'protobuf/protobuf_full/structurally_valid.o',
  'protobuf/protobuf_full/strutil.o',
  'protobuf/protobuf_full/time.o',
  'protobuf/protobuf_full/wire_format_lite.o',
  'protobuf/protobuf_full/zero_copy_stream.o',
  'protobuf/protobuf_full/zero_copy_stream_impl_lite.o',
]

NODE_VERSIONS = {
  '46': '4.2.0',
  '47': '5.3.0',
  '48': '6.9.0',
  '51': '7.4.0',
}

DEFAULT_NODE_MODULE_VERSION = '46'

def detect_host_platform():
  """detect host architecture"""
  host_platform_name = platform.system().lower()
  if host_platform_name == DARWIN:
    return MAC
  return host_platform_name


def detect_host_os():
  """detect host operating system"""
  return platform.system().lower()


def detect_host_arch():
  return platform.uname()[4]


def option_parser(args):
  """fetching tools arguments parser"""
  parser = argparse.ArgumentParser()

  host_platform = detect_host_platform()
  parser.add_argument('--target-platform',
                      choices=[LINUX, ANDROID, IOS, MAC, WINDOWS],
                      help='default platform: {}'.format(host_platform),
                      default=host_platform)

  parser.add_argument('--target',
                      choices=[STELLITE_QUIC_SERVER_BIN,
                               STELLITE_CLIENT_BINDER,
                               SIMPLE_CHUNKED_UPLOAD_CLIENT_BIN,
                               STELLITE_HTTP_CLIENT,
                               STELLITE_HTTP_CLIENT_BIN,
                               STELLITE_HTTP_SESSION,
                               STELLITE_HTTP_SESSION_BIN,
                               NODE_STELLITE],
                      default=STELLITE_HTTP_CLIENT)

  parser.add_argument('--target-type',
                      choices=[STATIC_LIBRARY, SHARED_LIBRARY, EXECUTABLE,
                               NODE_MODULE],
                      default=STATIC_LIBRARY)

  parser.add_argument('--chromium-path', default=None)

  parser.add_argument('-v', '--verbose', action='store_true', help='verbose')
  parser.add_argument('--debug', action='store_true', help='debugging mode')
  parser.add_argument('--asan', action='store_true', help='address sanitizer')

  parser.add_argument('--node-module-version', choices=NODE_VERSIONS.keys(),
                      default=DEFAULT_NODE_MODULE_VERSION)

  parser.add_argument('action', choices=[CLEAN, BUILD, UNITTEST],
                      default=BUILD)
  options = parser.parse_args(args)

  if options.target in (STELLITE_QUIC_SERVER_BIN,
                        STELLITE_HTTP_CLIENT_BIN,
                        STELLITE_HTTP_SESSION_BIN,
                        SIMPLE_CHUNKED_UPLOAD_CLIENT_BIN):
    options.target_type = EXECUTABLE

  if options.target == NODE_STELLITE:
    options.target_type = NODE_MODULE

  if options.target in (STELLITE_HTTP_CLIENT):
    if not options.target_type in (STATIC_LIBRARY, SHARED_LIBRARY):
      print('invalid target type error')
      sys.exit(1)

  host_platform = detect_host_platform()
  if options.target_platform in (IOS, MAC) and not host_platform == MAC:
    print('target must built on darwin/mac')
    sys.exit(1)

  if options.target_platform == LINUX and host_platform != LINUX:
    print('target must built on linux')
    sys.exit(1)

  host_uname = platform.uname()[3].lower()
  if options.target_platform == ANDROID and not UBUNTU in host_uname:
    print('android build must built on ubuntu/linux')
    sys.exit(1)

  if not options.node_module_version in NODE_VERSIONS.iterkeys():
    print('{} is not supported node module version')
    sys.exit(1)

  return options


def build_object(options):
  kwargs = dict(options._get_kwargs())
  if options.target_platform == ANDROID:
    return AndroidBuild(**kwargs)

  if options.target_platform == MAC:
    return MacBuild(**kwargs)

  if options.target_platform == IOS:
    return IOSBuild(**kwargs)

  if options.target_platform == LINUX:
    return LinuxBuild(**kwargs)

  if options.target_platform == WINDOWS:
    return WindowsBuild(**kwargs)

  raise Exception('unsupported target_platform: {}'.format(options.target_type))


def which_application(name):
  return distutils.spawn.find_executable(name)


def copy_tree(src, dest):
  """recursivly copy a directory from |src| to |dest|"""
  if not os.path.exists(dest):
    os.makedirs(dest)

  for dir_member in os.listdir(src):
    src_name = os.path.join(src, dir_member)
    dest_name = os.path.join(dest, dir_member)
    if os.path.isdir(src_name):
      copy_tree(src_name, dest_name)
      continue
    shutil.copy2(src_name, dest_name)


class BuildObject(object):
  """build stellite client and server"""

  def __init__(self, action=None, chromium_path=None, debug=False,
               node_module_version=None, target=None, target_arch=None,
               target_platform=None, target_type=None, verbose=False,
               asan=False):
    self._action = action
    self._chromium_path = chromium_path
    self._debug = debug
    self._node_module_version = node_module_version
    self._target = target
    self._target_arch = target_arch
    self._target_platform = target_platform
    self._target_type = target_type
    self._verbose = verbose
    self._asan = asan

    self.fetch_depot_tools()

  @property
  def kwargs(self):
    return {
      'action': self.action,
      'chromium_path': self.chromium_path,
      'debug': self.debug,
      'node_module_version': self.node_module_version,
      'target': self.target,
      'target_arch': self.target_arch,
      'target_platform': self.target_platform,
      'target_type': self.target_type,
      'verbose': self.verbose,
      'asan': self.asan,
    }

  @property
  def action(self):
    return self._action

  @property
  def verbose(self):
    return self._verbose

  @property
  def debug(self):
    return self._debug

  @property
  def target(self):
    return self._target

  @property
  def target_arch(self):
    return self._target_arch

  @property
  def target_type(self):
    return self._target_type

  @property
  def target_platform(self):
    return self._target_platform

  @property
  def asan(self):
    return self._asan

  @property
  def root_path(self):
    """reprotobuf_full/turn root absolute path"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

  @property
  def output_path(self):
    return os.path.join(self.root_path, 'output')

  @property
  def third_party_path(self):
    """return third_party path"""
    return os.path.join(self.root_path, 'third_party')

  @property
  def depot_tools_path(self):
    return os.path.join(self.third_party_path, 'depot_tools')

  @property
  def gclient_path(self):
    """return gclient path"""
    return os.path.join(self.depot_tools_path, 'gclient')

  @property
  def buildspace_path(self):
    """return source code directory for build.

    it was getter from chromium essential code and code"""
    return os.path.join(self.root_path,
                        'build_{}'.format(self.target_platform))

  @property
  def buildspace_src_path(self):
    return os.path.join(self.buildspace_path, 'src')

  @property
  def buildspace_stellite_path(self):
    return os.path.join(self.buildspace_src_path, 'stellite')

  @property
  def buildspace_node_binder_path(self):
    return os.path.join(self.buildspace_src_path, 'node_binder')

  @property
  def buildspace_node_path(self):
    return os.path.join(self.buildspace_src_path, 'node')

  @property
  def gn_path(self):
    """return gn path"""
    return os.path.join(self.depot_tools_path, 'gn')

  @property
  def build_output_path(self):
    """return object file path that store a compiled files"""
    out_dir = 'out_{}'.format(self.target_platform)
    build = 'debug' if self.debug else 'release'
    return os.path.join(self.buildspace_src_path, out_dir, build)

  @property
  def stellite_path(self):
    """return stellite code path"""
    return os.path.join(self.root_path, 'stellite')

  @property
  def node_binder_path(self):
    """return node binder code path"""
    return os.path.join(self.root_path, 'node_binder')

  @property
  def node_root_path(self):
    """return node root directory"""
    return os.path.join(self.third_party_path,
                        'node_{}'.format(detect_host_platform()))

  @property
  def node_path(self):
    """return nodejs path"""
    return os.path.join(self.node_root_path, str(self.node_module_version))

  @property
  def node_include_path(self):
    """nodejs include path"""
    return os.path.join(self.node_path, 'include', 'node')

  @property
  def modified_files_path(self):
    """return modified_files path"""
    return os.path.join(self.root_path, 'modified_files')

  @property
  def node_modified_files_path(self):
    "return node_modified_files path"""
    return os.path.join(self.root_path, 'node_modified_files')

  @property
  def chromium_path(self):
    if self._chromium_path:
      return self._chromium_path

    chromium_dir = 'chromium_{}'.format(self.target_platform)
    return os.path.join(self.third_party_path, chromium_dir)

  @property
  def chromium_src_path(self):
    return os.path.join(self.chromium_path, 'src')

  @property
  def chromium_branch(self):
    return self.read_chromium_branch()

  @property
  def chromium_tag(self):
    return self.read_chromium_tag()

  @property
  def clang_compiler_path(self):
    return os.path.join(self.chromium_src_path, 'third_party', 'llvm-build',
                        'Release+Asserts', 'bin', 'clang++')

  @property
  def iphone_sdk_path(self):
    return self.xcode_sdk_path('iphoneos')

  @property
  def simulator_sdk_path(self):
    return self.xcode_sdk_path('iphonesimulator')

  @property
  def mac_sdk_path(self):
    return self.xcode_sdk_path('macosx')

  @property
  def dependency_directories(self):
    return CHROMIUM_DEPENDENCY_DIRECTORIES

  @property
  def stellite_http_client_header_files(self):
    include_path = os.path.join(self.stellite_path, 'include')
    return map(lambda x: os.path.join(include_path, x),
               os.listdir(include_path))

  @property
  def buildspace_ycm_extra_config_path(self):
    return os.path.join(self.buildspace_src_path, 'tools', 'vim',
                        'chromium.ycm_extra_conf.py')

  @property
  def target_ycm_extra_config_path(self):
    return os.path.join(self.root_path, '.ycm_extra_conf.py')

  @property
  def node_module_version(self):
    return self._node_module_version

  def xcode_sdk_path(self, osx_target):
    """return xcode sdk path"""
    command = ['xcrun', '-sdk', osx_target, '--show-sdk-path']
    job = subprocess.Popen(command, stdout=subprocess.PIPE)
    job.wait()
    return job.stdout.read().strip()

  def execute_with_error(self, command, env=None, cwd=None):
    env = env or os.environ.copy()
    env_path = self.depot_tools_path
    if env.get('PATH'):
      env_path = '{}:{}'.format(env.get('PATH'), self.depot_tools_path)
    env['PATH'] = env_path
    print('Running: %s' % (' '.join(pipes.quote(x) for x in command)))

    job = subprocess.Popen(command, env=env, cwd=cwd)
    return job.wait() == 0


  def execute(self, command, env=None, cwd=None):
    """execute shell command"""
    res = self.execute_with_error(command, env=env, cwd=cwd)
    if bool(res) == True:
      return

    raise Exception('command execution are failed')

  def fetch_depot_tools(self):
    """get depot_tools code"""
    if os.path.exists(self.depot_tools_path):
      return

    os.makedirs(self.depot_tools_path)
    self.execute(['git', 'clone', GIT_DEPOT, self.depot_tools_path],
                 cwd=self.depot_tools_path)

  def fetch_chromium(self):
    """fetch chromium"""
    if os.path.exists(self.chromium_path):
      print('chromium is already exists: {}'.format(self.chromium_path))
      return False

    os.makedirs(self.chromium_path)

    fetch_path = os.path.join(self.depot_tools_path, 'fetch')
    fetch_command = [fetch_path, '--nohooks', 'chromium']
    self.execute(fetch_command, cwd=self.chromium_path)

    return self.fetch_toolchain()

  def fetch_node(self):
    """fetch nodejs"""
    for tag, version in NODE_VERSIONS.iteritems():
      node_path = os.path.join(self.node_root_path, str(tag))
      if os.path.exists(node_path):
        continue
      os.makedirs(node_path)

      try:
        temp_dir = tempfile.mkdtemp(dir=self.root_path)
        self.install_node(temp_dir, tag, version)
      finally:
        shutil.rmtree(temp_dir)

  def fetch_toolchain(self):
    """fetch build toolchain"""
    return True

  def install_node(self, temp_dir, node_tag, node_version):
    """install nodejs"""
    if not self.target_platform in (MAC, LINUX):
      return

    if self.target_platform == MAC:
      node_target = 'node-v{}-darwin-x64.tar.gz'.format(node_version)
    elif self.target_platform == LINUX:
      node_target = 'node-v{}-linux-x64.tar.gz'.format(node_version)

    url = 'https://nodejs.org/dist/v{}/{}'.format(node_version, node_target)
    print('fetch {}'.format(url))

    download_stream = urllib2.urlopen(url)
    temp_file = os.path.join(temp_dir, node_target)
    with open(temp_file, 'wb') as tar_stream:
      while True:
        chunk = download_stream.read(2 ** 20)
        if not chunk:
          break
        tar_stream.write(chunk)

    with tarfile.open(temp_file) as tar_interface:
      def is_within_directory(directory, target):
          
          abs_directory = os.path.abspath(directory)
          abs_target = os.path.abspath(target)
      
          prefix = os.path.commonprefix([abs_directory, abs_target])
          
          return prefix == abs_directory
      
      def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
      
          for member in tar.getmembers():
              member_path = os.path.join(path, member.name)
              if not is_within_directory(path, member_path):
                  raise Exception("Attempted Path Traversal in Tar File")
      
          tar.extractall(path, members, numeric_owner=numeric_owner) 
          
      
      safe_extract(tar_interface, path=temp_dir)

    extract_path = os.path.join(temp_dir, node_target[:-len('.tar.gz')])
    os.rename(extract_path, os.path.join(self.node_root_path, str(node_tag)))

  def install_build_deps(self):
    """execute chromium/src/build/install_build_deps.sh"""
    return True

  def remove_chromium(self):
    """remove chromium code"""
    if not os.path.exists(self.chromium_path):
      return

    print('remove chromium code: '.format(self.chromium_path))
    shutil.rmtree(self.chromium_path)

  def generate_ninja_script(self, gn_args, gn_options=None):
    """generate ninja build script using gn."""
    gn_options = gn_options or []

    gn_args += '\nis_debug = {}\n'.format('true' if self.debug else 'false')
    gn_args += '\nis_asan = {}\n'.format('true' if self.asan else 'false')
    gn_args += '\nsymbol_level = {}\n'.format('1' if self.debug else '0')

    if not os.path.exists(self.build_output_path):
      os.makedirs(self.build_output_path)

    gn_args_file_path = os.path.join(self.build_output_path, 'args.gn')
    with open(gn_args_file_path, 'w') as gn_args_file:
      gn_args_file.write(gn_args)

    print('generate ninja script ...')

    command = [self.gn_path]
    if len(gn_options) > 0:
      command.extend(gn_options)
    command.append('gen')
    command.append(self.build_output_path)

    self.execute(command, cwd=self.buildspace_src_path)

  def write_gclient(self, context):
    gclient_info_path = os.path.join(self.chromium_path, '.gclient')
    if os.path.exists(gclient_info_path):
      os.remove(gclient_info_path)

    with open(gclient_info_path, 'a') as gclient_meta_file:
      gclient_meta_file.write(context)

  def check_target_platform(self):
    """check host-platform to build a targe or not"""
    return True

  def check_chromium_repository(self):
    """check either chromium are valid or not"""
    if not os.path.exists(self.chromium_path):
      return False

    if not os.path.exists(self.chromium_src_path):
      return False

    if not os.path.isdir(self.chromium_src_path):
      return False

    if not os.path.exists(os.path.join(self.chromium_path, '.gclient')):
      return False

    if not os.path.exists(os.path.join(self.chromium_path, 'src', 'DEPS')):
      return False

    return True

  def read_chromium_branch(self):
    """read chromium git branch"""
    command = ['git', 'rev-parse', '--abbrev-ref', 'HEAD']

    try:
      job = subprocess.Popen(command, cwd=self.chromium_src_path,
                             stdout=subprocess.PIPE)
      job.wait()
      return job.stdout.read().strip()
    except Exception:
      return None

  def read_chromium_tag(self):
    """read tag string that write on file """
    chromium_tag_file_path = os.path.join(self.root_path, 'chromium.tag')
    if not os.path.exists(chromium_tag_file_path):
      raise Exception('chromium.tag is not exist error')

    with open(chromium_tag_file_path, 'r') as tag:
      return tag.read().strip()

  def synchronize_chromium_tag(self):
    """sync chromium"""
    print('check chromium ...')
    if not self.check_chromium_repository():
      raise Exception('invalid chromium repository error')

    print('check chromium tag ...')
    if self.chromium_tag in self.chromium_branch:
      return True

    cwd = self.chromium_src_path

    self.execute(['git', 'fetch', '--tags'], cwd=cwd)
    self.execute(['git', 'reset', '--hard'], cwd=cwd)

    branch = 'chromium_{}'.format(self.chromium_tag)
    if not self.execute_with_error(['git', 'checkout', branch], cwd=cwd):
      make_branch_command = ['git', 'checkout', '-b', branch, self.chromium_tag]
      self.execute(make_branch_command, cwd=cwd)

    command = [self.gclient_path, 'sync', '--with_branch_heads',
               '--jobs', str(multiprocessing.cpu_count() * 4)]
    self.execute(command, cwd=cwd)

    chromium_build_path = os.path.join(self.chromium_src_path, 'build')

    # install-build-deps.sh
    if self.target_platform == LINUX:
      self.execute(
        [os.path.join(chromium_build_path, 'install-build-deps.sh')],
        cwd=cwd
      )

    # install-build-deps-android.sh
    if self.target_platform == ANDROID:
      self.execute(
        [os.path.join(chromium_build_path, 'install-build-deps-android.sh')],
        cwd=cwd
      )

  def synchronize_buildspace(self):
    """synchronize code for building libchromium.a"""
    if not os.path.exists(self.buildspace_src_path):
      print('make {} ...'.format(self.buildspace_src_path))
      os.makedirs(self.buildspace_src_path)

    for target_dir in self.dependency_directories:
      if os.path.exists(os.path.join(self.buildspace_src_path, target_dir)):
        continue
      print('copy chromium {} ...'.format(target_dir))
      copy_tree(os.path.join(self.chromium_src_path, target_dir),
                os.path.join(self.buildspace_src_path, target_dir))

    print('copy .gclient ...')
    shutil.copy(os.path.join(self.chromium_path, '.gclient'),
                self.buildspace_path)

    print('copy modified_files ...')
    copy_tree(self.modified_files_path, self.buildspace_src_path)

    print('copy chromium/src/.gn ...')
    shutil.copy(os.path.join(self.chromium_src_path, '.gn'),
                self.buildspace_src_path)

    print('copy node_binder files ...')
    self.copy_node_binder_code()

    if self.target_type == NODE_MODULE:
      print('copy node files ...')
      self.copy_node_code()

      print('copy node_modified_files ...')
      copy_tree(self.node_modified_files_path, self.buildspace_src_path)

    print('copy stellite files...')
    self.copy_stellite_code()

    print('copya stellite build fakefiles ...')
    self.copy_ycm_config_files()

  def copy_ycm_config_files(self):
    """copy ycm config file"""
    # sync .ycm_extra_config
    if os.path.exists(self.target_ycm_extra_config_path):
      os.remove(self.target_ycm_extra_config_path)
    command = ['ln', '-s',
               self.buildspace_ycm_extra_config_path,
               self.target_ycm_extra_config_path]
    self.execute_with_error(command)

  def copy_stellite_code(self):
    """copy stellite code to buildspace"""
    if os.path.exists(self.buildspace_stellite_path):
      os.remove(self.buildspace_stellite_path)

    command = ['ln', '-s', self.stellite_path]
    self.execute_with_error(command, cwd=self.buildspace_src_path)

  def copy_node_binder_code(self):
    """copy stellite code to buildspace"""
    if os.path.exists(self.buildspace_node_binder_path):
      os.remove(self.buildspace_node_binder_path)

    command = ['ln', '-s', self.node_binder_path]
    self.execute_with_error(command, cwd=self.buildspace_src_path)

  def copy_node_code(self):
    if os.path.exists(self.buildspace_node_path):
      os.remove(self.buildspace_node_path)

    command = ['ln', '-s', self.node_include_path, 'node']
    self.execute_with_error(command, cwd=self.buildspace_src_path)

    command = ['touch', os.path.join(self.node_include_path, 'node.h')]
    self.execute_with_error(command)

  def build_target(self, target):
    if not target:
      raise ValueError('invalid target: {}'.format(target))

    command = ['ninja']
    if self.verbose:
      command.append('-v')
    command.extend(['-C', self.build_output_path, target])
    self.execute(command)

  def check_depot_tools_or_install(self):
    if os.path.exists(self.depot_tools_path):
      return
    print('fetch depot_tools ...')
    self.fetch_depot_tools()

  def gclient_sync(self):
    command = [self.gclient_path, 'sync',
               '--jobs', str(multiprocessing.cpu_count() * 4)]
    self.execute(command, cwd=self.chromium_path)

  def pattern_files(self, root, pattern, exclude_patterns=None):
    """return pattern file path list"""
    res = []
    exclude_patterns = exclude_patterns or []
    for path, _, file_list in os.walk(root):
      for matched in fnmatch.filter(file_list, pattern):
        is_exclude = False
        for exclude_filename in exclude_patterns:
          if exclude_filename in os.path.join(path, matched):
            is_exclude = True
            break
        if is_exclude:
          continue
        res.append(os.path.join(path, matched))
    return res

  def build(self):
    """build target"""
    raise NotImplementedError()

  def clean(self):
    """clean buildspace"""
    if not os.path.exists(self.build_output_path):
      return
    shutil.rmtree(self.build_output_path)

  def unittest(self):
    raise NotImplementedError()

  def copy_stellite_http_client_headers(self):
    include_dir = os.path.join(self.output_path, 'include')
    if not os.path.exists(include_dir):
      os.makedirs(include_dir)

    for header_file in self.stellite_http_client_header_files:
      shutil.copy(header_file, include_dir)

  def copy_node_stellite_javascript_deps(self):
    for javascript_file in self.pattern_files(self.node_binder_path, '*.js'):
      shutil.copy(javascript_file, self.output_path)
    for json_file in self.pattern_files(self.node_binder_path, '*.json'):
      shutil.copy(json_file, self.output_path)

  def copy_chromium_java_deps(self):
    to_lib_java_dir = os.path.join(self.output_path, 'lib.java')
    if not os.path.exists(to_lib_java_dir):
      os.makedirs(to_lib_java_dir)

    from_lib_java_dir = os.path.join(self.build_output_path, 'lib.java')
    if not os.path.exists(from_lib_java_dir):
      raise Exception(from_lib_java_dir + ' is not exist error')

    for jar_file in self.pattern_files(from_lib_java_dir, '*.jar'):
      if jar_file.endswith('interface.jar'):
        continue
      if 'android_support_' in jar_file:
        continue
      shutil.copy(jar_file, to_lib_java_dir)


class AndroidBuild(BuildObject):
  """android build"""
  def __init__(self, **kwargs):
    super(self.__class__, self).__init__(**kwargs)
    self._target_arch = kwargs.get(TARGET_ARCH, ALL)

  @property
  def build_output_path(self):
    out_dir = 'out_{}_{}'.format(self.target_platform, self.target_arch)
    return os.path.join(self.buildspace_path, 'src', out_dir, 'obj')

  @property
  def ndk_root_path(self):
    return os.path.join(self.chromium_path, 'src', 'third_party',
                        'android_tools', 'ndk')

  @property
  def android_app_abi(self):
    if self.target_arch == 'armv6':
      return 'armeabi'

    if self.target_arch == 'armv7':
      return 'armeabi-v7a'

    if self.target_arch == 'arm64':
      return 'arm64-v8a'

    if self.target_arch == 'x86':
      return 'x86'

    if self.target_arch == 'x64':
      return 'x86_64'

    raise Exception('unknown target architecture: {}'.format(self.target_arch))

  @property
  def android_toolchain_relative(self):
    if self.target_arch in ('armv6', 'armv7'):
      return 'arm-linux-androideabi-4.9'

    if self.target_arch == 'arm64':
      return 'aarch64-linux-android-4.9'

    if self.target_arch == 'x86':
      return 'x86-4.9'

    if self.target_arch == 'x64':
      return 'x86_64-4.9'

    raise Exception('unknown target architecture: {}'.format(self.target_arch))

  @property
  def android_libcpp_root(self):
    return os.path.join(self.ndk_root_path, 'sources', 'cxx-stl', 'llvm-libc++')

  @property
  def android_libcpp_libs_dir(self):
    return os.path.join(self.android_libcpp_root, 'libs', self.android_app_abi)

  @property
  def android_ndk_sysroot(self):
    ndk_platforms_path = os.path.join(self.ndk_root_path, 'platforms')
    if self.target_arch in ('armv6', 'armv7'):
      return os.path.join(ndk_platforms_path, 'android-16', 'arch-arm')

    if self.target_arch == 'arm64':
      return os.path.join(ndk_platforms_path, 'android-21', 'arch-arm64')

    if self.target_arch == 'x86':
      return os.path.join(ndk_platforms_path, 'android-16', 'arch-x86')

    if self.target_arch == 'x64':
      return os.path.join(ndk_platforms_path, 'android-21', 'arch-x86_64')

    raise Exception('unknown target error: {}'.format(self.target_arch))

  @property
  def android_ndk_lib_dir(self):
    if self.target_arch in ('armv6', 'armv7', 'arm64', 'x86'):
      return os.path.join('usr', 'lib')

    if self.target_arch == 'x64':
      return os.path.join('usr', 'lib64')

    raise Exception('unknown target architecture: {}'.format(self.target_arch))

  @property
  def android_ndk_lib(self):
    return os.path.join(self.android_ndk_sysroot, self.android_ndk_lib_dir)

  @property
  def android_toolchain_path(self):
    return os.path.join(self.ndk_root_path, 'toolchains',
                        self.android_toolchain_relative, 'prebuilt',
                        '{}-{}'.format(detect_host_os(), detect_host_arch()))

  @property
  def android_compiler_path(self):
    toolchain_path = os.path.join(self.android_toolchain_path, 'bin')
    filtered = filter(lambda x: x.endswith('g++'), os.listdir(toolchain_path))
    return os.path.join(toolchain_path, filtered[0])

  @property
  def android_ar_path(self):
    toolchain_path = os.path.join(self.android_toolchain_path, 'bin')
    filtered = filter(lambda x: x.endswith('ar'), os.listdir(toolchain_path))
    return os.path.join(toolchain_path, filtered[0])

  @property
  def android_strip_path(self):
    toolchain_path = os.path.join(self.android_toolchain_path, 'bin')
    filtered = filter(lambda x: x.endswith('strip'), os.listdir(toolchain_path))
    return os.path.join(toolchain_path, filtered[0])

  @property
  def binutils_path(self):
    return os.path.join(self.chromium_path, 'src', 'third_party', 'binutils',
                        'Linux_x64', 'Release', 'bin')

  @property
  def android_libgcc_filename(self):
    toolchain_path = os.path.join(self.android_toolchain_path, 'bin')
    filtered = filter(lambda x: x.endswith('gcc'), os.listdir(toolchain_path))
    gcc_path = os.path.join(toolchain_path, filtered[0])
    job = subprocess.Popen([gcc_path, '-print-libgcc-file-name'],
                           stdout=subprocess.PIPE)
    job.wait()
    return job.stdout.read().strip()

  @property
  def android_abi_target(self):
    if self.target_arch in ('armv6', 'armv7'):
      return 'arm-linux-androideabi'
    if self.target_arch == 'x86':
      return 'i686-linux-androideabi'
    if self.target_arch == 'arm64':
      return 'aarch64-linux-android'
    if self.target_arch == 'x64':
      return 'x86_64-linux-androideabi'
    raise Exception('unknown target architecture error')

  @property
  def dependency_directories(self):
    return ANDROID_DEPENDENCY_DIRECTORIES

  @property
  def chromium_java_lib_deps(self):
    # chromium android java library are same for different cpu architecture
    java_lib_path = os.path.join(self.buildspace_src_path, 'out_android_armv6',
                                 'obj', 'lib.java')
    return self.pattern_files(java_lib_path, '*.jar')

  def install_build_deps(self):
    """install android's build-deps-android.sh"""
    command = [
      os.path.join(self.chromium_src_path, 'build',
                   'install-build-deps-android.sh')
    ]
    self.execute(command)

  def synchronize_buildspace(self):
    super(self.__class__, self).synchronize_buildspace()
    buildspace_src = os.path.join(self.buildspace_path, 'src')
    for target_dir in ANDROID_DEPENDENCY_DIRECTORIES:
      if os.path.exists(os.path.join(buildspace_src, target_dir)):
        continue
      print('copy chromium {} ...'.format(target_dir))
      copy_tree(os.path.join(self.chromium_src_path, target_dir),
                os.path.join(buildspace_src, target_dir))

  def clang_arch(self, arch):
    if arch in ('x86', 'x64', 'arm64'):
      return arch
    if arch in ('armv6', 'armv7'):
      return 'arm'
    raise Exception('undefined android clang arch')

  def appendix_gn_args(self, arch):
    if arch == 'armv6':
      return 'arm_version = 6'
    if arch == 'armv7':
      return 'arm_version = 7'
    return ''

  def fetch_toolchain(self):
    self.write_gclient(GCLIENT_ANDROID)
    self.gclient_sync()
    return True

  def link_static_library(self, library_name, output_dir):
    library_path = os.path.join(self.build_output_path, library_name)
    command = [
      self.android_ar_path,
      'rsc', os.path.join(self.build_output_path, library_name),
    ]

    for filename in self.pattern_files(self.build_output_path, '*.o'):
      command.append(filename)
    self.execute(command)

    if not os.path.exists(output_dir):
      os.makedirs(output_dir)

    shutil.copy2(library_path, output_dir)

  def link_shared_library(self, library_name, output_dir):
    command = [
      self.clang_compiler_path,
      '-Wl,-shared',
      '-Wl,--fatal-warnings',
      '-fPIC',
      '-Wl,-z,noexecstack',
      '-Wl,-z,now',
      '-Wl,-z,relro',
      '-Wl,-z,defs',
      '-Wl,--as-needed',
      '--gcc-toolchain={}'.format(self.android_toolchain_path),
      '-fuse-ld=gold',
      '-Wl,--icf=all',
      '-Wl,--build-id=sha1',
      '-Wl,--no-undefined',
      '-Wl,--exclude-libs=libgcc.a',
      '-Wl,--exclude-libs=libc++_static.a',
      '-Wl,--exclude-libs=libvpx_assembly_arm.a',
      '-Wl,',
      '--target={}'.format(self.android_abi_target),
      '-Wl,--warn-shared-textrel',
      '-Wl,-O1',
      '-Wl,-fdata-sections',
      '-Wl,-ffunction-sections',
      '-Wl,--gc-sections',
      '-nostdlib',
      '-Wl,--warn-shared-textrel',
      '--sysroot={}'.format(self.android_ndk_sysroot),
      '-Bdynamic',
      '-Wl,-z,nocopyreloc',
      '-Wl,-wrap,calloc',
      '-Wl,-wrap,free',
      '-Wl,-wrap,malloc',
      '-Wl,-wrap,memalign',
      '-Wl,-wrap,posix_memalign',
      '-Wl,-wrap,pvalloc',
      '-Wl,-wrap,realloc',
      '-Wl,-wrap,valloc',
      '-L{}'.format(self.android_libcpp_libs_dir),
      '-Wl,-soname={}'.format(library_name),
      os.path.join(self.android_ndk_lib, 'crtbegin_so.o'),
    ]

    objs = self.pattern_files(os.path.join(self.build_output_path, 'obj'),
                              '*.o', ANDROID_EXCLUDE_OBJECTS)
    command.append('-Wl,--start-group')
    command.extend(objs)
    command.append('-Wl,--end-group')

    command.extend([
      '-lc++_static',
      '-lc++abi',
      '-landroid_support',
      '-lunwind',
      self.android_libgcc_filename,
      '-lc',
      '-ldl',
      '-lm',
      '-llog',
      '-latomic',
      os.path.join(self.android_ndk_lib, 'crtend_so.o'),
    ])

    # armv6, armv7 arch leck of stack trace symbol in stl
    if not self.target_arch in ('armv6', 'armv7'):
      command.remove('-lunwind')

    if self.debug:
      command.append('-fno-optimize-sibling-calls')
      command.append('-fno-omit-frame-pointer')

    library_path = os.path.join(self.build_output_path, library_name)
    command.extend(['-o', library_path])

    self.execute(command)

    # strip shared library
    if not self.debug:
      command = [
        self.android_strip_path,
        library_path,
      ]
      self.execute(command)

    if not os.path.exists(output_dir):
      os.makedirs(output_dir)
    shutil.copy2(library_path, output_dir)

  def build(self):
    for arch in ('armv6', 'armv7', 'arm64', 'x86', 'x64'):
      kwargs = self.kwargs
      kwargs[TARGET_ARCH] = arch
      build = AndroidBuild(**kwargs)

      gn_context = GN_ARGS_ANDROID.format(target_cpu=self.clang_arch(arch))
      gn_context += '\n' + self.appendix_gn_args(arch)
      build.generate_ninja_script(gn_args=gn_context)

      build.build_target(self.target)

  def package_target(self):
    builds = []
    for arch in ('armv6', 'armv7', 'arm64', 'x86', 'x64'):
      kwargs = self.kwargs
      kwargs[TARGET_ARCH] = arch
      builds.append(AndroidBuild(**kwargs))

    for build in builds:
      output_dir = os.path.join(build.output_path, build.target_arch)
      if build.target_type == STATIC_LIBRARY:
        build.link_static_library('lib{}.a'.format(self.target), output_dir)

      if build.target_type == SHARED_LIBRARY:
        build.link_shared_library('lib{}.so'.format(self.target), output_dir)

    self.copy_stellite_http_client_headers()
    if len(builds) > 0:
      builds[0].copy_chromium_java_deps()

  def clean(self):
    for arch in ('armv6', 'armv7', 'arm64', 'x86', 'x64'):
      kwargs = self.kwargs
      kwargs[TARGET_ARCH] = arch
      build = AndroidBuild(**kwargs)
      if not os.path.exists(build.build_output_path):
        continue
      shutil.rmtree(build.build_output_path)

  def unittest(self):
    pass


class MacBuild(BuildObject):
  """mac build"""
  def __init__(self, **kwargs):
    super(self.__class__, self).__init__(**kwargs)

  def build(self):
    gn_args = GN_ARGS_MAC
    self.generate_ninja_script(gn_args)
    self.build_target(self.target)

  def package_target(self):
    if self.target == STELLITE_HTTP_CLIENT:
      self.copy_stellite_http_client_headers()

    if self.target_type == SHARED_LIBRARY:
      self.link_shared_library('lib{}.dylib'.format(self.target))

    if self.target_type == STATIC_LIBRARY:
      self.link_static_library('lib{}.a'.format(self.target))

    if self.target_type == NODE_MODULE:
      self.link_node_module()
      self.copy_node_stellite_javascript_deps()

    if self.target_type == EXECUTABLE:
      shutil.copy2(os.path.join(self.build_output_path, self.target),
                   self.output_path)

  def link_shared_library(self, library_name):
    command = [
      self.clang_compiler_path,
      '-shared',
      '-Wl,-search_paths_first',
      '-Wl,-dead_strip',
      '-isysroot', self.mac_sdk_path,
      '-arch', 'x86_64',
    ]

    for filename in self.pattern_files(self.build_output_path, '*.o',
                                       MAC_EXCLUDE_OBJECTS):
      command.append(filename)

    library_path = os.path.join(self.build_output_path, library_name)
    command.extend([
      '-o', library_path,
      '-install_name', '@loader_path/{}'.format(library_name),
      '-stdlib=libc++',
      '-lresolv',
      '-lbsm',
      '-framework', 'AppKit',
      '-framework', 'ApplicationServices',
      '-framework', 'Carbon',
      '-framework', 'CoreFoundation',
      '-framework', 'Foundation',
      '-framework', 'IOKit',
      '-framework', 'Security',
      '-framework', 'SystemConfiguration'
    ])
    self.execute(command, cwd=self.build_output_path)

    shutil.copy2(library_path, self.output_path)

  def link_static_library(self, library_name):
    libtool_path = which_application('libtool')
    if not libtool_path:
      raise Exception('libtool is not exist error')

    command = [ libtool_path, '-static', ]
    for filename in self.pattern_files(self.build_output_path, '*.o',
                                       MAC_EXCLUDE_OBJECTS):
      command.append(os.path.join(self.build_output_path, filename))

    library_path = os.path.join(self.build_output_path, library_name)
    command.extend([
      '-arch_only', 'x86_64',
      '-o', library_path,
    ])
    self.execute(command)

    shutil.copy2(library_path, self.output_path)

  def link_node_module(self):
    command = [
      self.clang_compiler_path,
      '-bundle',
      '-undefined', 'dynamic_lookup',
      '-Wl,-search_paths_first',
      '-Wl,-dead_strip',
      '-isysroot', self.mac_sdk_path,
      '-arch', 'x86_64',
    ]
    for filename in self.pattern_files(self.build_output_path, '*.o',
                                       MAC_EXCLUDE_OBJECTS):
      command.append(filename)

    library_name = 'stellite.node'
    library_path = os.path.join(self.build_output_path, library_name)
    command.extend([
      '-o', library_path,
      '-stdlib=libc++',
      '-lresolv',
      '-lbsm',
      '-framework', 'AppKit',
      '-framework', 'ApplicationServices',
      '-framework', 'Carbon',
      '-framework', 'CoreFoundation',
      '-framework', 'Foundation',
      '-framework', 'IOKit',
      '-framework', 'Security',
      '-framework', 'SystemConfiguration'
    ])
    self.execute(command, cwd=self.build_output_path)
    shutil.copy2(library_path, self.output_path)

  def unittest(self):
    gn_arguments = '\n'.join([GN_ARGS_MAC, 'is_asan = true'])
    self.generate_ninja_script(gn_arguments)
    self.build_target('stellite_unittests')

    unittest_command = [
      os.path.join(self.build_output_path, 'stellite_unittests'),
      '--single-process-tests',
    ]
    if self.verbose:
      unittest_command.append('--v=3')
    self.execute_with_error(unittest_command)


class IOSBuild(BuildObject):
  """ios build"""
  def __init__(self, **kwargs):
    super(self.__class__, self).__init__(**kwargs)
    self._target_arch = kwargs.get(TARGET_ARCH, ALL)

  @property
  def build_output_path(self):
    out_dir = 'out_{}_{}'.format(self.target_platform, self.target_arch)
    return os.path.join(self.buildspace_path, 'src', out_dir)

  @property
  def clang_target_arch(self):
    if self.target_arch == 'arm':
      return 'armv7'
    if self.target_arch == 'arm64':
      return 'arm64'
    if self.target_arch == 'x86':
      return 'i386'
    if self.target_arch == 'x64':
      return 'x86_64'
    raise Exception('unsupported ios target architecture error')

  def fetch_toolchain(self):
    self.write_gclient(GCLIENT_IOS)
    self.gclient_sync()
    return True

  def build(self):
    kwargs = self.kwargs
    for arch in ('x86', 'x64', 'arm', 'arm64'):
      kwargs[TARGET_ARCH] = arch
      build = IOSBuild(**kwargs)
      build.generate_ninja_script(gn_args=GN_ARGS_IOS.format(target_cpu=arch),
                                  gn_options=['--check'])
      build.build_target(self.target)

  def clean(self):
    kwargs = self.kwargs
    for arch in ('arm', 'arm64', 'x86', 'x64'):
      kwargs[TARGET_ARCH] = arch
      build = IOSBuild(**kwargs)
      if not os.path.exists(build.build_output_path):
        continue
      shutil.rmtree(build.build_output_path)

  def package_target(self):
    libs = []
    kwargs = self.kwargs
    for arch in ('x86', 'x64', 'arm', 'arm64'):
      kwargs[TARGET_ARCH] = arch
      build = IOSBuild(**kwargs)
      if build.target_type == STATIC_LIBRARY:
        libs.append(build.link_static_library())

      if build.target_type == SHARED_LIBRARY:
        libs.append(build.link_shared_library())

    if build.target_type == STATIC_LIBRARY:
      self.link_fat_library('lib{}.a'.format(self.target), libs)
    elif build.target_type == SHARED_LIBRARY:
      self.link_fat_library('lib{}.so'.format(self.target), libs)

    self.copy_stellite_http_client_headers()

  def link_shared_library(self):
    library_name = 'lib{}_{}.dylib'.format(self.target, self.target_arch)

    sdk_path = self.iphone_sdk_path
    if self.target_arch in ('x86', 'x64'):
      sdk_path = self.simulator_sdk_path

    command = [
      self.clang_compiler_path,
      '-shared',
      '-Wl,-search_paths_first',
      '-Wl,-dead_strip',
      '-miphoneos-version-min=9.0',
      '-isysroot', sdk_path,
      '-arch', self.clang_target_arch,
      '-install_name', '@loader_path/{}'.format(library_name),
    ]
    for filename in self.pattern_files(self.build_output_path, '*.o',
                                       IOS_EXCLUDE_OBJECTS):
      command.append('-Wl,-force_load,{}'.format(filename))

    library_path = os.path.join(self.build_output_path, library_name)
    command.extend([
      '-o', library_path,
      '-stdlib=libc++',
      '-lresolv',
      '-framework', 'CFNetwork',
      '-framework', 'CoreFoundation',
      '-framework', 'CoreGraphics',
      '-framework', 'CoreText',
      '-framework', 'Foundation',
      '-framework', 'MobileCoreServices',
      '-framework', 'Security',
      '-framework', 'SystemConfiguration',
      '-framework', 'UIKit',
    ])
    self.execute(command)
    return library_path

  def link_static_library(self):
    library_name = 'lib{}_{}.a'.format(self.target, self.target_arch)

    libtool_path = which_application('libtool')
    if not libtool_path:
      raise Exception('libtool is not exist error')

    command = [
      libtool_path,
      '-static',
    ]
    for filename in self.pattern_files(self.build_output_path, '*.o',
                                       IOS_EXCLUDE_OBJECTS):
      command.append(os.path.join(self.build_output_path, filename))

    library_path = os.path.join(self.build_output_path, library_name)
    command.extend([
      '-arch_only', self.clang_target_arch,
      '-o', library_path
    ])
    self.execute(command)
    return library_path

  def link_fat_library(self, library_filename, from_list):
    command = ['lipo', '-create']
    command.extend(from_list)
    command.append('-output')

    fat_filepath = os.path.join(self.build_output_path, library_filename)
    command.append(fat_filepath)

    if os.path.exists(self.build_output_path):
      shutil.rmtree(self.build_output_path)
    os.makedirs(self.build_output_path)

    self.execute(command)

    shutil.copy2(fat_filepath, self.output_path)

  def unittest(self):
    pass


class LinuxBuild(BuildObject):
  """linux build"""
  def __init__(self, **kwargs):
    super(self.__class__, self).__init__(**kwargs)

  def install_build_deps(self):
    """execute chromium/src/build/install_build_deps.sh"""
    command = [
      os.path.join(self.chromium_src_path, 'build', 'install-build-deps.sh')
    ]
    self.execute(command)
    return True

  def build(self):
    self.generate_ninja_script(GN_ARGS_LINUX)
    self.build_target(self.target)

  def package_target(self):
    if self.target_type == STELLITE_HTTP_CLIENT:
      self.copy_stellite_http_client_headers()

    if self.target_type == STATIC_LIBRARY:
      self.link_static_library()

    if self.target_type == SHARED_LIBRARY:
      self.link_shared_library()

    if self.target_type == NODE_MODULE:
      self.link_node_module()
      self.copy_node_stellite_javascript_deps()

    if self.target_type == EXECUTABLE:
      shutil.copy2(os.path.join(self.build_output_path, self.target),
                   self.output_path)

  def link_static_library(self):
    library_name = 'lib{}.a'.format(self.target)
    library_path = os.path.join(self.build_output_path, library_name)

    command = [ 'ar', 'rsc', library_path, ]
    for filename in self.pattern_files(self.build_output_path, '*.a',
                                       LINUX_EXCLUDE_OBJECTS):
      command.append(filename)
    self.execute(command)

    shutil.copy2(library_path, self.output_path)

  def link_shared_library(self):
    library_name = 'lib{}.so'.format(self.target)
    library_path = os.path.join(self.build_output_path, library_name)

    command = [
      self.clang_compiler_path,
      '-shared',
      '-fPIC',
      '-fuse-ld=gold',
      '-m64',
      '-pthread',
      '-Wl,--as-needed',
      '-Wl,--export-dynamic',
      '-Wl,--fatal-warnings',
      '-Wl,--icf=all',
      '-Wl,--no-as-needed',
      '-Wl,-z,noexecstack',
      '-Wl,-z,now',
      '-Wl,-z,relro',
      '-lpthread',
      '-o', library_path,
      '-Wl,-soname="{}"'.format(library_name),
      '-Wl,--gc-sections',
      '-Wl,-whole-archive',
      '-Wl,--start-group',
    ]

    for filename in self.pattern_files(self.build_output_path, '*.o',
                                       LINUX_EXCLUDE_OBJECTS):
      command.append(filename)

    command.extend([
      '-lnssutil3',
      '-latomic',
      '-ldl',
      '-lgconf-2',
      '-lgio-2.0',
      '-lglib-2.0',
      '-lgmodule-2.0',
      '-lgobject-2.0',
      '-lgthread-2.0',
      '-lnspr4',
      '-lnss3',
      '-lplc4',
      '-lplds4',
      '-lpthread',
      '-lresolv',
      '-lrt',
      '-lsmime3',
      '-Wl,--end-group',
      '-Wl,-no-whole-archive',
    ])

    self.execute(command)

    shutil.copy2(library_path, self.output_path)

  def link_node_module(self):
    library_name = 'stellite.node'
    library_path = os.path.join(self.build_output_path, library_name)

    command = [
      self.clang_compiler_path,
      '-fPIC',
      '-fuse-ld=gold',
      '-m64',
      '-rdynamic',
      '-shared',
      '-pthread',
      '-o', library_path,
      '-Wl,--as-needed',
      '-Wl,--export-dynamic',
      '-Wl,--fatal-warnings',
      '-Wl,--icf=all',
      '-Wl,--no-as-needed',
      '-Wl,-dead_strip',
      '-Wl,-search_paths_first',
      '-Wl,-z,noexecstack',
      '-Wl,-z,now',
      '-Wl,-z,relro',
      '-Wl,-soname={}'.format(library_name),
      '-Wl,--gc-sections',
      '-Wl,-whole-archive',
      '-Wl,--start-group',
    ]
    for filename in self.pattern_files(self.build_output_path, '*.o',
                                       LINUX_EXCLUDE_OBJECTS):
      command.append(filename)

    command.extend([
      '-lnssutil3',
      '-latomic',
      '-ldl',
      '-lgconf-2',
      '-lgio-2.0',
      '-lglib-2.0',
      '-lgmodule-2.0',
      '-lgobject-2.0',
      '-lgthread-2.0',
      '-lnspr4',
      '-lnss3',
      '-lplc4',
      '-lplds4',
      '-lpthread',
      '-lresolv',
      '-lrt',
      '-lsmime3',
      '-Wl,--end-group',
      '-Wl,-no-whole-archive',
    ])

    self.execute(command)

    shutil.copy2(library_path, self.output_path)

  def fetch_toolchain(self):
    return True

  def unittest(self):
    pass


class WindowsBuild(BuildObject):
  """windows build"""
  def __init__(self, **kwargs):
    super(self.__class__, self).__init__(**kwargs)
    self._vs_path = None
    self._vs_version = None
    self._sdk_path = None
    self._sdk_dir = None
    self._runtime_dirs = None

  @property
  def python_path(self):
    return os.path.join(self.depot_tools_path, 'python276_bin', 'python.exe')

  @property
  def dependency_directories(self):
    return WINDOWS_DEPENDENCY_DIRECTORIES

  @property
  def vs_path(self):
    if hasattr(self, '_vs_path'):
      return self._vs_path

    self.get_vs_toolchain()
    return self._vs_path

  @property
  def sdk_path(self):
    if hasattr(self, '_sdk_path'):
      return self._sdk_path
    self.get_vs_toolchain()
    return self._sdk_path

  @property
  def vs_version(self):
    if hasattr(self, '_vs_version'):
      return self._vs_version
    self.get_vs_toolchain()
    return self._vs_version

  @property
  def wdk_dir(self):
    if hasattr(self, '_wdk_dir'):
      return self._wdk_dir
    self.get_vs_toolchain()
    return self._wdk_version

  @property
  def runtime_dirs(self):
    if hasattr(self, '_runtime_dirs'):
      return self._runtime_dirs
    self.get_vs_toolchain()
    return self._runtime_dirs()

  @property
  def tool_wrapper_path(self):
    return os.path.join(self.chromium_src_path, 'build', 'toolchain', 'win',
                        'tool_wrapper.py')

  @property
  def build_response_file_path(self):
    return os.path.join(self.build_output_path, 'stellite_build.rsp')

  def get_vs_toolchain(self):
    command = [
      self.python_path,
      os.path.join(self.chromium_src_path, 'build', 'vs_toolchain.py'),
      'get_toolchain_dir'
    ]

    env = os.environ.copy()
    env['DEPOT_TOOLS_WIN_TOOLCHAIN'] = '0'
    job = subprocess.Popen(command, stdout=subprocess.PIPE, env=env)
    job.wait()
    stdout = job.stdout.read().strip()

    toolchain = dict()
    for toolchain_line in stdout.split('\n'):
      unpacked = map(lambda x : x.strip().lower(), toolchain_line.split('='))
      if len(unpacked) != 2:
        continue
      toolchain[unpacked[0]] = unpacked[1]

    self._vs_path = toolchain.get('vs_path')
    self._vs_version = toolchain.get('vs_version')
    self._sdk_path = toolchain.get('sdk_path')
    self._sdk_dir = toolchain.get('wdk_dir')
    self._runtime_dirs = toolchain.get('runtime_dirs').split(';')

  def execute_with_error(self, command, cwd=None, env=None):
    print('Running: %s' % (' '.join(pipes.quote(x) for x in command)))

    env = env or os.environ.copy()
    env['DEPOT_TOOLS_WIN_TOOLCHAIN'] = '0'
    job = subprocess.Popen(command, cwd=cwd, env=env, shell=True)
    return job.wait() == 0

  def copy_stellite_code(self):
    """copy stellite code to buildspace"""
    if os.path.exists(self.buildspace_stellite_path):
      shutil.rmtree(self.buildspace_stellite_path)
    copy_tree(self.stellite_path, self.buildspace_stellite_path)

  def copy_node_code(self):
    """copy nodejs binder code to buildspace"""
    if os.path.exists(self.buildspace_node_path):
      shutil.rmtree(self.buildspace_node_path)
    copy_tree(self.node_path, self.buildspace_node_path)

  def copy_node_binder_code(self):
    """copy nodejs binder code to buildspace"""
    if os.path.exists(self.buildspace_node_binder_path):
      shutil.rmtree(self.buildspace_node_binder_path)
    copy_tree(self.node_binder_path, self.buildspace_node_binder_path)

  def package_target(self):
    output_files = []
    if self.target_type == STATIC_LIBRARY:
      output_files.extend(self.pattern_files(self.build_output_path, '*.lib'))

    if self.target_type == SHARED_LIBRARY:
      output_files.extend(self.pattern_files(self.build_output_path, '*.dll'))

    if self.target_type == EXECUTABLE:
      output_files.append(os.path.join(self.build_output_path, self.target))

    for output_file in output_files:
      shutil.copy2(output_file, self.output_path)

  def build(self):
    is_component = 'false' if self.target_type == STATIC_LIBRARY else 'true'
    gn_args = GN_ARGS_WINDOWS.format(is_component)
    self.generate_ninja_script(gn_args=gn_args)
    self.build_target(self.target)

  def unittest(self):
    pass


def main(args):
  """main entry point"""
  options = option_parser(args)

  build = build_object(options)
  if not build.check_target_platform():
    print('invalid platform error: {}'.format(options.target_platform))
    sys.exit(1)

  if options.action == CLEAN:
    build.clean()
    return 0

  build.fetch_chromium()
  build.synchronize_chromium_tag()
  build.synchronize_buildspace()

  if build.target_type == NODE_MODULE:
    build.fetch_node()

  if options.action == BUILD:
    if os.path.exists(build.output_path):
      shutil.rmtree(build.output_path)
    os.makedirs(build.output_path)

    build.build()
    build.package_target()

  if options.action == UNITTEST:
    build.unittest()
    return 0

  return 1


if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
