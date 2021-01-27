#! /usr/bin/python
# _*_ coding:utf-8 _*_

import os
import sys
import getopt
import subprocess
import re


BASE_PATH = "/opt/omd/sites/%s/local/share/check_mk/%s"
CHECKS_PATH = "checks"
CHECKMANS_PATH = "checkman"


def get_checks_path(site_name):
    return BASE_PATH % (site_name, CHECKS_PATH)


def get_checkman_path(site_name):
    return BASE_PATH % (site_name, CHECKMANS_PATH)


def usage():
    print("""    -h  help menu
    -i sitename install check in the site
    -u sitename uninstall check from the site 
""")


def copy_file(source_dir, target_dir):
    for file in os.listdir(source_dir):
        _source_file = os.path.join(source_dir, file)
        _target_file = os.path.join(target_dir, file)
        if os.path.isfile(_source_file):
            _file = open(_source_file, 'rb')
            if _file is not None:
                readbuf = _file.read()
                _file.close()
            _file_t = open(_target_file, "wb")
            if _file_t is not None:
                _file_t.write(readbuf)
                _file_t.close()
        elif os.path.isdir(_source_file):
            copy_file(_source_file, _target_file)
        else:
            continue


def remov_file(target_dir):
    for file in os.listdir(target_dir):
        if "huawei_hmm" in file or "huawei_ibmc" in file:
            os.remove(os.path.join(target_dir, file))


def install(site_name):
    _checks_path = get_checks_path(site_name)
    _checkman_path = get_checkman_path(site_name)

    if os.path.exists(_checks_path) and os.path.exists(_checkman_path):
        copy_file("./hmm/checks/", _checks_path)
        copy_file("./hmm/checkman/", _checkman_path)
        copy_file("./ibmc/checks/", _checks_path)
        copy_file("./ibmc/checkman/", _checkman_path)
    else:
        print("do not exitsts this site")
        return
    print("install sucessed")


def uninstall(site_name):
    print("uninstall")
    _checks_path = get_checks_path(site_name)
    _checkman_path = get_checkman_path(site_name)
    if os.path.exists(_checks_path) and os.path.exists(_checkman_path):
        remov_file(_checks_path)
        remov_file(_checkman_path)
    else:
        print("do not exitsts this site")
        return
    print("uninstall sucessed")

def check_version():
    version = None
    try:
        version = subprocess.check_output(['omd', 'version'], shell=False)
    except OSError:
        version = subprocess.check_output(['cmk', '--version'], shell=False)
    if version is None:
        print("The Check_MK version information cannot be detected.")
        sys.exit()
    version = str(version)
    current_version = re.search(r"(\d)\.(\d)\..*", version).group()
    if current_version.startswith('1.6'):
        return True
    else:
        print("The current Check_MK version is", current_version)
        print("The plug-in does not adapt to this version.")
        sys.exit()
        

if __name__ == "__main__":
    check_version()
    try:
        options, args = getopt.getopt(sys.argv[1:], "hi:u:")
    except getopt.GetoptError:
        usage()
        sys.exit()

    for key, value in options:
        if key == "-h":
            usage()
            sys.exit()
        if key == "-i":
            if value is None and value == '':
                usage()
                sys.exit()
            else:
                install(value)
        if key == "-u":
            if value is None and value == '':
                usage()
                sys.exit()
            else:
                uninstall(value)
