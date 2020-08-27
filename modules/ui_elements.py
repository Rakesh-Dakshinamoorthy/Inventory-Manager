from gluon.html import A, URL, BUTTON


btn_add_asset = BUTTON(
    'Add Asset', _type='button', _class='btn btn-primary',
    **{'_data-toggle': 'modal', '_data-target': '#add_asset'}
)

btn_add_asset_category = BUTTON(
    'Add Category', _type='button', _class='btn btn-primary',
    **{'_data-toggle': 'modal', '_data-target': '#addcategory'}
)

btn_add_team = BUTTON(
        "Add Team", _type="button", _class="btn btn-primary",
        **{'_data-toggle': "modal", '_data-target': "#addteam"}
    )

btn_add_user = BUTTON(
        'Add User', _type='button', _class='btn btn-primary',
        **{'_data-toggle': 'modal', '_data-target': '#add_user'}
    )


def change_assignee_button(row):
    return A('Change Assignee',
             _class='button btn btn-secondary',
             _href='#change_assignee',
             **{'_data-toggle': 'modal', '_data-rowid': row.asset_id}
             )


def edit_remarks_button(row):
    return A('Edit Remarks',
             _class='button btn btn-secondary',
             _href='#edit_remarks',
             **{'_data-toggle': 'modal', '_data-rowid': row.asset_id,
                '_data-remarks': row.remarks}
             )


def view_history_link(row):
    return A('History', _href=URL('asset', 'history', args=[row.id]))


def change_status_button(row):
    return A('Change Status',
             _class='button btn btn-secondary',
             callback=URL('asset', 'change_status', args=[row.id])
             )


def cancel_assignee_button(row):
    return A(
        "Cancel",
        _class="btn btn-default btn-secondary",
        callback=URL('asset', 'cancel_assignee', args=[row.id])
    )


def reject_assignee_button(row):
    return A(
        "Reject transfer",
        _class="btn btn-default btn-secondary",
        callback=URL('asset', 'reject_assignee', args=[row.id])
    )


def accept_assignee_button(row):
    return A(
        "Accept transfer",
        _class="btn btn-default btn-secondary",
        callback=URL('asset', 'accept_assignee', args=[row.id])
    )


def audit_button(row):
    return A(
        'Audit', _class='button btn btn-secondary', _href='#audit',
        **{'_data-toggle': 'modal', '_data-rowid': row.asset_id}
    )


def manager_button(row):
    return A(
        "Assign Manager",
        _class="button btn btn-secondary",
        _href="#assignmanager",
        **{'_data-toggle': "modal", '_data-rowid': row.team_name}
    )


def lead_button(row):
    return A(
        "Assign Lead",
        _class="button btn btn-secondary",
        _href="#assignlead",
        **{'_data-toggle': "modal", '_data-rowid': row.team_name}
    )


def member_button(row):
    return A(
        "Assign Member",
        _class="button btn btn-secondary",
        _href="#assignmember",
        **{'_data-toggle': "modal", '_data-rowid': row.team_name}
    )


def members_link(row):
    return A("Members", _href=URL('project', 'members', args=[row.id]))


def assign_permission_button(row):
    return A("Assign Permission", _href='#permission',
             _class="btn btn-default btn-secondary",
             **{'_data-rowid': row.email, '_data-toggle': "modal"})


def delete_user_button(row):
    return A("Delete", _class="btn btn-default btn-secondary",
             callback=URL('project', 'delete_user', args=[row.id]))


def view_asset_cards_property(all_query, transferring_query, undeclared_query):
    return [{"header": "All assets", "count": all_query,
             "url": URL("asset", "view", args=["all"]),
             "card_style": "card text-white bg-success mb-5"},
            {"header": "Transferring assets", "count": transferring_query,
             "url": URL("asset", "view", args=["transferring"]),
             "card_style": "card text-white bg-warning mb-5"},
            {"header": "Undeclared assets", "count": undeclared_query,
             "url": URL("asset", "view", args=["undeclared"]),
             "card_style": "card text-white bg-danger mb-5"}]
