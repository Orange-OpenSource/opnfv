# -*- coding: utf-8 -*-
"""
:author: Pawel Chomicki
:contact: pawel.chomicki@nokia.com
"""
import argparse


def command_line():
    parser = argparse.ArgumentParser(description='This script will create config files for a VM in current folder.')
    parser.add_argument('-n', '--name', help='Set the name of the machine', metavar='')
    parser.add_argument('-i', '--ip', help='Set the ip address of the machine.', metavar='')
    parser.add_argument('-p', '--password', help='Set the ssh password. Login is ubuntu.', metavar='')
    parser.add_argument('-t', '--targetpool', help='Set the target pool to install the volume.', metavar='')
    parser.add_argument('-x', '--cloud-init', help='Set the cloud init file template.', metavar='')
    parser.add_argument('-y', '--meta-data', help='Set the meta-data file template.', metavar='')
    parser.add_argument('-k', '--kvm-config', help='Set the KVM config file template.', metavar='')
    parser.add_argument('-l', '--cpu', help='Set number of CPU for the VM.', metavar='')
    parser.add_argument('-m', '--mem', help='Set quantity of RAM for the VM.', metavar='')
    parser.add_argument('-d', '--disksize', help='Create a disk with that size instead of default one which is 5G.', metavar='')
    parser.add_argument('-f', '--force', action='store_true', help='Do not ask for confirmation before launching VM.')
    parser.add_argument('-s', '--storage', action='store_true', help='Add a network interface based on YAML config files.')
    parser.add_argument('machinename', help='The name of machine.')
    return parser.parse_args()


if __name__ == '__main__':
    command_line()
