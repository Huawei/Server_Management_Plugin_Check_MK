#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# check_mk is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# tails. You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.


def inventory_huawei_mezz_health(info):
    return [("blade 6 mezz status", None)]


def scan(oid):
    return (oid(".1.3.6.1.4.1.2011.2.82.1.82.4.6.6.0") == '1')


check_info["huawei_hmm_mezz6_check"] = {
    "inventory_function": inventory_huawei_mezz_health,
    "check_function": check_huawei_mezz_health,
    "service_description": "%s",
    'includes': ["huawei_hmm_util.include", ],
    "snmp_info": (".1.3.6.1.4.1.2011.2.82.1.82.4.6.2008.1", ["4", "5", "2", ]),
    'snmp_scan_function': scan,
}
