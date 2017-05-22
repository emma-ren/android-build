#!/usr/bin/env python
import argparse
import os
import subprocess
import sys
import tempfile
import shutil

def call_process(opts):
    """Run command with arguments and return its output as byte string"""
    try:
        return str(subprocess.check_output(opts)).rstrip()
    except subprocess.CalledProcessError as err:
       print >> sys.stderr, 'Process "%s" failed: %s' % (opts[0], err.output)
       sys.stderr.flush()
       sys.exit(err.returncode)

def add_packages_to_repository(args):
    debpkg = args.debname
    if '-' in debpkg:
        deb_basename = os.path.basename(debpkg)
        deb_prefix = deb_basename.split('-')[0]
        dest_path = 'eswerepo/pool/' + deb_prefix + '/'

    #cmd = ['/usr/bin/curl', '-n','-d',debpkg, '-X', 'PUT', full_dir]
    cmd = ['/usr/bin/jfrog', 'rt', 'upload', '--deb', 'trusty/main/amd64', debpkg, dest_path]
    call_process(cmd)

def get_packages_from_repository(args):
    print 'getpackage'

def list_labels_in_repository(args):
    print 'listlabels'

def create_label_in_repository(args):
    print 'createlabel'

def _main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        title='subcommands', description='valid subcommands',
        help="The  action to take (e.g. addpackages, addpackage, list,listlabels, getpakcage, createlable, createswlabel,promotefromfile,status)")
    parser_addpackage = subparsers.add_parser('addpackage')
    parser_addpackage.add_argument("debname",
                                help="Target debian package")
    parser_addpackage.add_argument("-ru", "--repositoryuri", nargs='?',
                        help="Debian package repository url")
    parser_addpackage.add_argument("--check-if-exists", nargs='?',
                        help="check if package exists on debian repository or not?")
    parser_addpackage.add_argument("--no-promote",
                        help="Don't promote what?")
    parser_addpackage.add_argument("--label",
                        help="full label on the debian repository")
    parser_addpackage.set_defaults(action = 'addpackage')

#    parser_list = subparsers.add_parser('getpackage')
#    parser_list = subparsers.add_parser('list')
#    parser_list = subparsers.add_parser('status')
#    parser_list = subparsers.add_parser('listlabels')
#    parser_list = subparsers.add_parser('createlabels')
#    parser_list = subparsers.add_parser('createswlabels')
#    parser_list = subparsers.add_parser('promotefromfile')
    args = parser.parse_args()
    #print "-----------------------repository arguments---------------------"
    #for arg in vars(args):
    #    print arg, getattr(args, arg)
    #print "-----------------------repository arguments---------------------"
    if args.action == 'addpackage':
        add_packages_to_repository(args)

if __name__ == "__main__":
    _main()
