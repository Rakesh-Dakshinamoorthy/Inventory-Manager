# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# ----------------------------------------------------------------------------------------------------------------------
# this is the main application menu add/remove items as required
# ----------------------------------------------------------------------------------------------------------------------

response.menu = [
    (T('Home'), False, URL('default', 'index'), [])
]

if auth.has_membership(role="Leads"):
    response.menu.extend([(T('Asset'), False, URL('asset', 'view'), []),
                          (T('Project'), False, URL('project', 'index'), [])])
elif auth.has_membership(role="Managers") :
    response.menu.append((T('Asset'), False, '#',
                          [(T('View'), False, URL('asset', 'view'), []),
                           (T('Category'), False, URL('asset', 'category'), [])]))
    response.menu.append((T('Project'), False, '#',
                          [(T('Team'), False, URL('project', 'team'), []),
                           (T('Users'), False, URL('project', 'users'), [])]))
elif auth.has_membership(role="Administrator"):
    response.menu.append((T('Asset'), False, '#',
                          [(T('View'), False, URL('asset', 'view'), []),
                           (T('Category'), False, URL('asset', 'category'), []),
                           (T('Audit'), False, URL('asset', 'view_audit'), []),
                           (T('History'), False, URL('asset',
                                                     'view_asset_history'))
                           ]))
    response.menu.append((T('Project'), False, '#',
                          [(T('Team'), False, URL('project', 'team'), []),
                           (T('Users'), False, URL('project', 'users'), [])]))
elif auth.has_membership(role="users"):
    response.menu.append((T('Asset'), False, URL('asset', 'view'), []))

admin_ids = list(map(
    lambda _: _.id, db(db.auth_membership.group_id == 1).select()
))
admin_emails = list(map(
    lambda _: _.email, db(db.auth_user.id.belongs(admin_ids)).select()
))
response.footer = " ".join(admin_emails)
