#!/usr/bin/env python
import argparse
import os
import subprocess
import sys
import tempfile
import shutil
import lsb_release


def get_codename():
    info = lsb_release.get_lsb_information()
    codename = info['CODENAME']
    return codename

def makedirp(directory):
    """Create a directory, if it does not exist"""
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as err:
            if err.errno != errno.EEXIST:
                raise err

def call_process(opts):
    """Run command with arguments and return its output as byte string"""
    try:
        return str(subprocess.check_output(opts)).rstrip()
    except subprocess.CalledProcessError as err:
       print >> sys.stderr, 'Process "%s" failed: %s' % (opts[0], err.output)
       sys.stderr.flush()
       sys.exit(err.returncode)

def cp_sharedlib_deps(prog, rootdir):
    """Collect the shared library dependencies and copy to destination dir  """
    cmd = ['ldd', prog]
    lddOut = call_process(cmd)
    lddout_lines = lddOut.splitlines()
    del lddout_lines[0]
    del lddout_lines[-1]
    for line in lddout_lines:
       arr = line.split(" => ")
       dep = arr[1].split(' (0x')[0]
       dest_dir = os.path.join(rootdir, os.path.dirname(prog))
       makedirp(dest_dir)
       shutil.copy(dep, dest_dir)

def prepare_chroot_env(rootdir):
    bin_list = ['/bin/bash', '/usr/bin/apt-get', '/usr/bin/apt', '/usr/bin/dpkg']
    full_bin_dir = os.path.join(rootdir, 'bin')

    #copy apt-get installation scripts to chroot envirionment
    ## The detail location or download method of install.sh should be discussed in real project
    ## local path is just a workaround in prototype phase, if you don't like this, bite me or show me your master piece!
    install_script = "/home/letv/bin/install.sh"
    shutil.copy(install_script, full_bin_dir)

    for binary in bin_list:
        shutil.copy(binary, full_bin_dir)
        cp_sharedlib_deps(binary, rootdir)

    apt_dir_list = ['/etc/apt/apt.conf.d', '/etc/apt/sources.list.d', '/var/lib/apt/lists/partial']
    for apt_dir in apt_dir_list:
        dest_dir = os.path.join(rootdir, apt_dir)
        shutil.copytree(apt_dir, dest_dir, symlinks=True)

    status_file = '/var/lib/dpkg/status'
    dest_dir = os.path.join(rootdir, os.path.dirname(status_file))
    makedirp(dest_dir)
    shutil.copy(status_file, dest_dir)

    repo_detail = "deb http://10.140.35.80:8081/artifactory/eswerepo trusty main\n"
    source_list = "/etc/apt/sources.list"

    makedirp(os.path.dirname(source_list))
    aptfile = open(source_list, 'w+')
    aptfile.write(repo_detail)
    aptfile.close()
    aptpinning = """Package: *
                    Pin: release a=%s,v=%s
                    Pin-Priority: 900""" % (get_codename(), args.label)

    preferencefile = "/etc/apt/preferences"
    apt_preference= open(preferencefile, 'w')
    apt_preference.write(aptpinning)
    apt_preference.close()

def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument("propkg",
                         help="Product Package Name")
    parser.add_argument("resultpkg",
                         help="Result package Name")
    parser.add_argument("varientpkg",
                         help="Varient package Name")
    parser.add_argument("-l","--label",
                        help="Software Snapshot Label in Debian Repository")
    parser.add_argument("-src", "--source-dir", default=[],action="append",
                        help="source directory of debian packages, it could be a local repostitory or formated artifactory url")
    parser.add_argument("-keep", nargs='?',
                        help="Keep original intermetient files created in the installation process")
    parser.add_argument("-wdir",nargs='?',
                        help="Custom directory if you want to keep intermetient files")
    parser.add_argument("-out",
                        help="Final images output directory")
    args = parser.parse_args()

    if args.keep:
        if args.wdir:
            chrootdir = os.path.abspath(args.wdir)
    else:
        chrootdir = tempfile.mkdtemp(prefix="tmp_img")

    if not os.path.exists(chrootdir):
        makedirp(chrootdir)

    #00 Get the product varient package from the type of varientpkg
    words = args.resultpkg.split("-")
    pvp_pkg_name = args.propkg.replace("pp-", "pvp-") + words[-1]

    # 01 - Prepare a chroot jail in a temporay directory
    prepare_chroot_env(chrootdir)

    # 02 - Run apt-get to download and install the wanted packages in the jail 
    #       and trigger the postinstal scripts from the result packages
    script= "/bin/bash -c \"su - -c /bin/install.sh " + pvp_pkg_name + " " + resultpkg + '\"'
    chroot_cmd = "chroot " + chrootdir + " " + script
    call_process(chroot_cmd)

    # 03 - Copy any files from /out in the jail to the desired output directory outside the jail
    jail_out = os.path.join(chrootdir, 'out')
    shutil.copyfile(jail_out, args.out)

    # 04 - Clean up by purging the jail directory
    shutil.rmtree(chrootdir, ignore_errors=True)

if __name__ == "__main__":
    _main()
