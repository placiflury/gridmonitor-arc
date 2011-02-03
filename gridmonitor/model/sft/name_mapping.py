#!/usr/bin/env python
"""
Module for String mappings of database columns
"""
SFT_KEYMAP = {
    'name'              :  ['Name:'],
    'cluster_group'     :  ['Cluster group:'],
    'vo_group'          :  ['VO group:'],
    'test_suit'         :  ['Test suit:'],
    'minute'            :  ['Minute:'],
    'hour'              :  ['Hour:'],
    'day'               :  ['Day:'],
    'month'             :  ['Month:'],
    'day_of_week'       :  ['Day of Week:']
}
SFT_KEYMAP_ORDER = ['name', 'cluster_group', 'vo_group', 'test_suit', 'month', 'day_of_week', 'day', 'hour', 'minute']

CLUSTER_KEYMAP = {
    'hostname'          :  ['Hostname:'],
    'alias'             :  ['Alias:']
}
CLUSTER_KEYMAP_ORDER = ['hostname', 'alias']

CLUSTER_GR_KEYMAP = {
    'name'              :  ['Name:']
}
CLUSTER_GR_KEYMAP_ORDER = ['name']

VO_KEYMAP = {
    'name'              :  ['Name:'],
    'server'            :  ['Server:']
}
VO_KEYMAP_ORDER = ['name', 'server']

VO_GR_KEYMAP = {
    'name'              :  ['Name:']
}
VO_GR_KEYMAP_ORDER = ['name']

USER_KEYMAP = {
    'DN'                :  ['DN:'],
    'display_name'      :  ['Display Name:']
}
USER_KEYMAP_ORDER = ['display_name', 'DN']

USER_GR_KEYMAP = {
    'name'              :  ['Name:']
}
USER_GR_KEYMAP_ORDER = ['name']

TEST_KEYMAP = {
    'name'              :  ['Name:'],
    'xrsl'              :  ['XRSL:']
}
TEST_KEYMAP_ORDER = ['name', 'xrsl']

TEST_SUIT_KEYMAP = {
    'name'              :  ['Name:']
}
TEST_SUIT_KEYMAP_ORDER = ['name']
