# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# ----------------------------------------------------------------------------------------------------------------------
# this is the main application menu add/remove items as required
# ----------------------------------------------------------------------------------------------------------------------

response.menu = [
    (T('Home'), False, URL('default', 'index'), [])
]

if auth.has_membership(group_id=3):
    response.menu.extend([(T('Asset'), False, URL('asset', 'view'), []),
                          (T('Project'), False, URL('project', 'index'), [])])
elif auth.has_membership(group_id=2) :
    response.menu.append((T('Asset'), False, '#',
                          [(T('View'), False, URL('asset', 'view'), []),
                           (T('Category'), False, URL('asset', 'category'), [])]))
    response.menu.append((T('Project'), False, '#',
                          [(T('Team'), False, URL('project', 'team'), []),
                           (T('Members'), False, URL('project', 'users'), [])]))
elif auth.has_membership(group_id=10):
    response.menu.append((T('Asset'), False, '#',
                          [(T('View'), False, URL('asset', 'view'), []),
                           (T('Category'), False, URL('asset', 'category'), []),
                           (T('Audit'), False, URL('asset', 'view_audit'))]))
    response.menu.append((T('Project'), False, '#',
                          [(T('Team'), False, URL('project', 'team'), []),
                           (T('Members'), False, URL('project', 'users'), [])]))
elif auth.has_membership(group_id=11):
    response.menu.append((T('Asset'), False, URL('asset', 'view'), []))

response.footer = "This tool is developed using web2py framework. " \
                  "Anyone having any ideas please contact the Owners " \
                  "for implementing it."
