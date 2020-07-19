# import any files needed for development
from web_page_data import AboutPage
from constants import asset_working_status, request_assignee_change, \
    changed_status, audited, assignee_changed, request_rejected, \
    request_cancelled
from ui_elements import *


@auth.requires_login()
def index():
    redirect(URL('asset', 'home'))


@auth.requires_login()
def home():
    response.flash = T('Welcome to Inventory Manager')
    return AboutPage().body


def cancel_assignee():
    asset = db(db.asset.id == request.args[0]).select().first()
    db(db.asset.id == request.args(0)).update(transferring_to=None)
    db.asset_history.insert(
        asset_id=asset.asset_id, asset_operation=request_cancelled,
        information='Asset transfer canceled',
        user_signature=auth.user
    )
    db.commit()
    redirect(URL('asset', 'view.html', args=['transferring']),
             client_side=True)


def reject_assignee():
    asset = db(db.asset.id == request.args[0]).select().first()
    db(db.asset.id == request.args(0)).update(transferring_to=None)
    db.asset_history.insert(
        asset_id=asset.asset_id, asset_operation=request_rejected,
        information='Asset transfer request is rejected transferring back '
                    'to same user',
        user_signature=auth.user
    )
    db.commit()
    redirect(URL('asset', 'view.html', args=['undeclared']),
             client_side=True)


def accept_assignee():
    asset = db(db.asset.id == request.args(0)).select().first()
    db(db.asset.id == asset.id).update(
        assigned_to=asset.transferring_to, transferring_to=None
    )
    db.asset_history.insert(
        asset_id=asset.asset_id, asset_operation=assignee_changed,
        information="Asset transfer from {} to {}".format(
            asset.assigned_to.email, asset.transferring_to.email
        ),
        user_signature=auth.user
    )
    db.commit()
    redirect(URL('asset', 'view.html', args=['undeclared']),
             client_side=True)


def change_status():
    asset = db(db.asset.id == request.args[0]).select().first()
    new_status = (asset_working_status[1]
                  if asset.hardware_status == asset_working_status[0]
                  else asset_working_status[0])
    db(db.asset.id == request.args[0]).update(hardware_status=new_status)
    db.asset_history.insert(
        asset_id=asset.asset_id, asset_operation=changed_status,
        information='Asset hardware status changed to {}'.format(new_status),
        user_signature=auth.user
    )
    db.commit()
    redirect(URL('asset', 'view.html', args=['all']), client_side=True)


def __team_members():
    if auth.has_membership(group_id=2):
        team = db(db.team.manager_name == auth.user).select()
        team_id = list(map(lambda each: each.id, team))
        members = list()
        members.append(auth.user.id)
        members.extend(list(map(lambda each: each.lead_name, team)))
        team_members = db(db.team_members.team_name.belongs(team_id)).select()
        members.extend(list(map(lambda each: each.member_name, team_members)))
        return set(members)
    elif auth.has_membership(group_id=3):
        team = db(db.team.lead_name == auth.user).select()
        team_id = list(map(lambda each: each.id, team))
        members = list()
        members.append(auth.user.id)
        team_members = db(db.team_members.team_name.belongs(team_id)).select()
        members.extend(list(map(lambda each: each.member_name, team_members)))
        return set(members)


def __view_grids_templates(view='all'):
    if view == 'all':
        return {
            "fields": [db.asset.asset_id, db.asset.category, db.asset.name,
                       db.asset.procurement_id, db.asset.assigned_to,
                       db.asset.hardware_status],
            "links": [view_history_link, change_assignee_button,
                      change_status_button],
            "csv": True, "create": False, "editable": False, "create": False,
            "args": request.args, "searchable": True, "details": False,
            "deletable": True if auth.has_membership(group_id=1) else False
        }
    elif view == "transferring":
        return {
            "fields": [db.asset.asset_id, db.asset.category, db.asset.name,
                       db.asset.transferring_to],
            "links": [change_assignee_button, cancel_assignee_button],
            "csv": True, "create": False, "editable": False, "create": False,
            "args": request.args, "searchable": True, "details": False,
            "deletable": False
        }
    elif view == "undeclared":
        return {
            "fields": [db.asset.asset_id, db.asset.category, db.asset.name,
                       db.asset.remarks, db.asset.hardware_status,
                       db.asset.assigned_to],
            "links": [accept_assignee_button, reject_assignee_button],
            "csv": True, "create": False, "editable": False, "create": False,
            "args": request.args, "searchable": True, "details": False,
            "deletable": False
        }


@auth.requires_login()
def view():
    users = list(
        map(lambda user: user.email, db(db.auth_user.id > 0).select())
    )
    form = add_asset()
    undeclared_asset = db(db.asset.transferring_to == auth.user)

    if auth.has_membership(group_id=1):
        all_query = db(db.asset.id > 0)
        transferring_asset = db(db.asset.transferring_to != None)
    elif auth.has_membership(group_id=2):
        members = __team_members()
        all_query = db(db.asset.assigned_to.belongs(members))
        transferring_asset = db(
            (db.asset.assigned_to.belongs(members)) &
            (db.asset.transferring_to != None)
        )
    elif auth.has_membership(group_id=3):
        members = __team_members()
        all_query = db(db.asset.assigned_to.belongs(members))
        transferring_asset = db(
            (db.asset.assigned_to.belongs(members)) &
            (db.asset.transferring_to != None)
        )
    else:
        all_query = db(db.asset.assigned_to == auth.user)
        transferring_asset = db(
            (db.asset.assigned_to == auth.user) &
            (db.asset.transferring_to != None)
        )

    if request.args[0].lower() == 'all':
        query = all_query
    elif request.args[0].lower() == 'transferring':
        query = transferring_asset
    elif request.args[0].lower() == 'undeclared':
        query = undeclared_asset

    card_properties = view_asset_cards_property(
        all_query, transferring_asset, undeclared_asset
    )

    grid = SQLFORM.grid(query,
                        **__view_grids_templates(request.args[0].lower()),
                        paginate=20)

    if auth.has_membership(group_id=1) and request.args[0].lower() == 'all':
        grid.elements(_class='web2py_console  ')[0].components[0] = \
            btn_add_asset

    return locals()


def add_asset():
    db.asset.assigned_to.writable = db.asset.transferring_to.writable = False
    form = SQLFORM.factory(db.asset)
    if form.process().accepted:
        db.asset.insert(**form.vars, **{'assigned_to': auth.user})
        response.flash = 'Asset is added'
        redirect(URL('asset', 'view.html', args=['all']), client_side=True)
    return form


@auth.requires_login()
def category():
    db.asset_category.id.readable = False
    grid = SQLFORM.grid(
        db.asset_category, searchable=True, csv=False, editable=False,
        deletable=True if auth.has_membership(group_id=1) else False,
        details=False, create=False,
        maxtextlengths={'asset_category.category': 20,
                        'asset_category.description': 80}
    )
    grid.elements(_class='web2py_console  ')[0].components[0] = \
        btn_add_asset_category
    return locals()


def add_category():
    form = SQLFORM.factory(db.asset_category)
    if form.process().accepted:
        db.asset_category.insert(**form.vars)
        response.flash = 'Asset category is added'
        redirect(URL('asset', 'category.html'), client_side=True)
    return form


@auth.requires_membership(group_id=1)
def view_audit():
    db.asset.id.readable = db.asset.remarks.readable = \
        db.asset.transferring_to.readable = False

    form = SQLFORM.factory(
        Field('Asset'),
        Field('audited_on', 'datetime', requires=IS_NOT_EMPTY())
    )
    grid = SQLFORM.grid(
        db.asset, searchable=True, csv=True, editable=False,
        deletable=False, details=False, create=False, links=[audit_button]
    )
    return locals()


def audit():
    form = SQLFORM.factory(
        Field('Asset'),
        Field('audited_on', 'datetime', requires=IS_NOT_EMPTY())
    )
    if form.process().accepted:
        db(db.asset.asset_id == form.vars.Asset).update(
            last_audited_on=form.vars.audited_on)
        db.asset_history.insert(
            asset_id=form.vars.Asset, asset_operation=audited,
            information='audited on: {}'.format(form.vars.audited_on),
            user_signature=auth.user
        )
        redirect(URL('asset', 'view_audit'), client_side=True)
    return form


def change_assignee():
    assign_to_form = SQLFORM.factory(
        Field('Asset'),
        Field('assigned_to', requires=IS_IN_SET(request.vars.users))
    )
    if assign_to_form.process().accepted:
        asset = \
            db(db.asset.asset_id == assign_to_form.vars.Asset).select().first()
        was_assigned_to = asset.assigned_to
        going_to_be_assigned = db(
            db.auth_user.email == assign_to_form.vars.assigned_to
        ).select().first()
        if asset.transferring_to:
            db.asset_history.insert(
                asset_id=asset.asset_id,
                asset_operation=request_rejected,
                information="changing assignee to a new user",
                user_signature=auth.user
            )
        db(db.asset.asset_id == assign_to_form.vars.Asset).update(
            transferring_to=going_to_be_assigned
        )
        db.asset_history.insert(
            asset_id=asset.asset_id, asset_operation=request_assignee_change,
            information=str({'from': was_assigned_to.email,
                             'to': going_to_be_assigned.email}),
            user_signature=auth.user
        )
        redirect(URL('asset', 'view.html', args=['all']), client_side=True)
    return assign_to_form


@auth.requires_login()
def history():
    db.asset_history.id.readable = db.asset_history.asset_id.readable = False
    asset_id = request.args[0]
    grid = SQLFORM.grid(
        db(db.asset_history.asset_id == asset_id), searchable=False, csv=False,
        editable=False, deletable=False, details=False, create=False,
        user_signature=False, maxtextlengths={'Information': 100},
        maxtextlength=100
    )
    return locals()


@auth.requires_membership(role="Administrator")
def view_asset_history():
    db.asset_history.id.readable = False
    grid = SQLFORM.grid(
        db.asset_history, searchable=True, csv=True,
        editable=False, deletable=False, details=False, create=False,
        user_signature=False, maxtextlengths={'Information': 100},
        maxtextlength=100
    )
    return {"grid": grid}
