#!/usr/bin/env python
"""
Module for String mappings of database columns
"""

ADMIN_KEYMAP = {
    'shib_unique_id'    :  ['Unique ID:'],
    'shib_given_name'   :  ['Given Name:'],
    'shib_surname'      :  ['Surname:'],
    'shib_email'        :  ['Email:']
}
ADMIN_KEYMAP_ORDER = ['shib_unique_id', 'shib_given_name', 'shib_surname', 'shib_email']

SITE_KEYMAP = {
    'name'              :  ['Name:'],
    'alias'             :  ['Alias:']
}
SITE_KEYMAP_ORDER = ['name', 'alias']

SERVICE_KEYMAP = {
    'name'              :  ['Name:'],
    'hostname'          :  ['Hostname:'],
    'site_name'         :  ['Site name:'],
    'type'              :  ['Type:'],
    'alias'             :  ['Alias']
}
SERVICE_KEYMAP_ORDER = ['name', 'hostname', 'site_name', 'type', 'alias']