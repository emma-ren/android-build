#!/usr/bin/env python
import argparse
import os
import subprocess
import sys
import tempfile
import shutil

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
        #return str(subprocess.check_output(opts)).rstrip()
        output = str(subprocess.check_output(opts, stderr=subprocess.STDOUT)).rstrip().split()[-1]
        debname = output.translate(None, '\'`')
        return debname[:-1]
    except subprocess.CalledProcessError as err:
        print >> sys.stderr, 'Process "%s" failed: %s' % (opts[0], err.output)
        sys.stderr.flush()
        sys.exit(err.returncode)

def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument("debname",
                        help="Name of debian package")
    parser.add_argument("swversion",
                        help="LeEco System Version")
    parser.add_argument("-df", "--data-files", default=[],action="append",
                        help="Debian data files. Can be used multiple times")
    parser.add_argument("-d", "--build-variant", nargs='?',
                        help="build variant")
    parser.add_argument("-c", "--control-file-field", default=[], action="append",
                        help="Debian Control file fields. Can be used multiple times")
    parser.add_argument("-cf", "--control-file-scripts", default=[],action="append",
                        help="scripts which are automatically run before or after a package is installed or removed")
    parser.add_argument("-cfe", "--control-field-extension", default=[], action="append",
                        help="Debian Control file fields extension. Can be used multiple times")
    parser.add_argument("-o", "--output-dir", nargs='?',
                        help="Debian output directory")
    parser.add_argument("--compressionlevel",nargs='?',default=9,
                        help="Debian compression level")
    parser.add_argument("--compressiontype",nargs='?',default='NONE',
                        help="Debian compression type")
    parser.add_argument("--jobs",nargs='?',default='',
                        help="Debian compression jobs")
    args = parser.parse_args()
#    for arg in vars(args):
#        print arg, getattr(args, arg)

    parent_dir = ''
    src_dir = ''
    deb_name = args.debname +'.deb'
    if args.swversion:
        deb_name = args.debname +  '_' + args.swversion + '.deb'

    output_root = args.output_dir
    if not output_root:
        output_root = './'
    dest_deb = os.path.join(output_root, deb_name)

    control_file_field = args.control_file_field
    data_files_list = args.data_files
    ctr_scprits = args.control_file_scripts
    tmp_path = tempfile.mkdtemp(prefix="tmp_pack_")
    deb_stage_dir = os.path.join(tmp_path, args.debname)
    debian_parent = os.path.join(deb_stage_dir,'DEBIAN')

    if  len(data_files_list) != 0 :
        for src_dir in data_files_list:
    #        parent_dir = os.path.join(topdir,os.path.dirname(src_dir))
            parent_dir = os.path.dirname(src_dir)
        shutil.copytree(parent_dir, deb_stage_dir, symlinks=True)

    # Append the control fields collected
    ctl_pkg_name = 'Package: ' + args.debname
    control_file_field.insert(0, ctl_pkg_name)

    ctl_pkg_maintainer = 'Maintainer: renyan.letv'
    ctl_pkg_version = 'Version: ' + args.swversion
    ctl_pkg_arc = 'Architecture: amd64'

    control_file_field.extend([ctl_pkg_version, ctl_pkg_maintainer, ctl_pkg_arc])

    if not any("Description" in str for str in control_file_field):
        ctl_pkg_des = 'Description: Emma is testing relax'
        control_file_field.extend([ctl_pkg_des])

    #control_file_field.extend(args.control_file_field)

    makedirp(debian_parent)
    cf_path = os.path.join(debian_parent, 'control')

    ctrfile = open(cf_path, 'a+')
    for cfield in control_file_field:
        print>>ctrfile, cfield
    ctrfile.close()

    if len(ctr_scprits) != 0:
        for script_i in ctr_scprits:
            shutil.copy(script_i, debian_parent)

    #deb_cmd = "/usr/bin/dpkg-deb -b --debug -v -Zgzip " + deb_stage_dir + ' ' + dest_deb
    #print deb_cmd
    cmd = ['/usr/bin/dpkg-deb', '-b','-Zgzip', deb_stage_dir, dest_deb]
    print call_process(cmd)

    shutil.rmtree(tmp_path, ignore_errors=True)

if __name__ == "__main__":
    _main()
