# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# ----------------------------------------------------------------------------------------------------------------------
# this is the main application menu add/remove items as required
# ----------------------------------------------------------------------------------------------------------------------

response.menu = []

if auth.has_membership(role="Leads"):
    response.menu.extend([
        (T('Asset'), False, URL('asset', 'view', args=['all']), []),
        (T('Project'), False, URL('project', 'index'), [])
    ])
elif auth.has_membership(role="Managers"):
    response.menu.extend(
        [(T('Asset'), False, URL('asset', 'view', args=['all']), []),
         (T('Category'), False, URL('asset', 'category'), []),
         (T('Team'), False, URL('project', 'team'), []),
         (T('Users'), False, URL('project', 'users'), [])]
    )
elif auth.has_membership(role="Admin"):
    response.menu.extend([
        (T('Asset'), False, URL('asset', 'view', args=['all']), []),
        (T('Category'), False, URL('asset', 'category'), []),
        (T('Audit'), False, URL('asset', 'view_audit'), []),
        (T('History'), False, URL('asset', 'view_asset_history'), []),
        (T('Team'), False, URL('project', 'team'), []),
        (T('Users'), False, URL('project', 'users'), []),
        (T('Import'), False, URL('asset', 'import_data'), [])
    ])
elif auth.has_membership(role="Users"):
    response.menu.append(
        (T('Asset'), False, URL('asset', 'view', args=['all']), [])
    )
