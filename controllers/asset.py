# import any files needed for development
from web_page_data import AboutPage
from helpers import UsersDB
from constants import asset_working_status, request_assignee_change, \
    changed_status, audited, assignee_changed, request_rejected


def change_assignee_button(row):
    return A('Change Assignee',
             _class='button btn btn-secondary',
             _href='#change_assignee',
             **{'_data-toggle': 'modal', '_data-rowid': row.asset_id}
             )


def view_history_link(row):
    return A('History', _href=URL('asset', 'history', args=[row.asset_id]))


def change_status_button(row):
    return A('Change Status',
             _class='button btn btn-secondary',
             callback=URL('asset', 'change_status', args=[row.id])
             )


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
    redirect(URL('asset', 'view'), client_side=True)



@auth.requires_login()
def home():
    response.flash = T('Welcome to Inventory Manager')
    return AboutPage().body


@auth.requires_login()
def category():
    db.asset_category.id.readable = False
    delete = False
    if auth.has_membership(group_id=1):
        delete = True
    grid = SQLFORM.grid(
        db.asset_category, searchable=True, csv=False, editable=False,
        deletable=delete, details=False, create=False,
        maxtextlengths={'asset_category.category': 20,
                        'asset_category.description': 80}
    )
    add_button = BUTTON(
        'Add Category', _type='button', _class='btn btn-primary',
        **{'_data-toggle': 'modal', '_data-target': '#addcategory'}
    )
    grid.elements(_class='web2py_console  ')[0].components[0] = add_button

    return locals()


def add_category():
    form = SQLFORM.factory(db.asset_category)
    if form.process().accepted:
        db.asset_category.insert(**form.vars)
        response.flash = 'Asset category is added'
        redirect(URL('asset', 'category.html'), client_side=True)
    return form


@auth.requires_login()
def view():
    users = list(
        map(lambda user: user.email, db(db.auth_user.id > 0).select())
    )
    form = add_asset()
    delete = False
    add_button = BUTTON(
        'Add Asset', _type='button', _class='btn btn-primary',
        **{'_data-toggle': 'modal', '_data-target': '#add_asset'}
    )
    if auth.has_membership(group_id=1):
        query = db((db.asset.id > 0) & (db.asset.transferred_to == None))
        shared_asset = db((db.asset.id > 0) & (db.asset.transferred_to != None))
        shared_asset_count = len(shared_asset.select())
        delete = True
    elif auth.has_membership(group_id=2):
        team = db(db.team.manager_name == auth.user).select()
        team_id = list(map(lambda each: each.id, team))
        members = list()
        members.append(auth.user.id)
        members.extend(list(map(lambda each: each.lead_name, team)))
        team_members = db(db.team_members.team_name.belongs(team_id)).select()
        members.extend(list(map(lambda each: each.member_name, team_members)))
        query = db((db.asset.assigned_to.belongs(set(members))) &
                   (db.asset.transferred_to == None))
    elif auth.has_membership(group_id=3):
        team = db(db.team.lead_name == auth.user).select()
        team_id = list(map(lambda each: each.id, team))
        members = list()
        members.append(auth.user.id)
        team_members = db(db.team_members.team_name.belongs(team_id)).select()
        members.extend(list(map(lambda each: each.member_name, team_members)))
        query = db((db.asset.assigned_to.belongs(set(members))) &
                   (db.asset.transferred_to == None))
    else:
        query = db((db.asset.assigned_to == auth.user) &
                   (db.asset.transferred_to == None))


    shared_asset_grid = SQLFORM.grid(
        shared_asset,
        fields=[db.asset.asset_id, db.asset.category, db.asset.name,
                db.asset.assigned_to, db.asset.transferred_to],
        links=[change_assignee_button],
        searchable=False, csv=False, editable=False, deletable=False,
        details=False, create=False
    )

    grid = SQLFORM.grid(
        query,
        fields=[db.asset.asset_id, db.asset.category, db.asset.name,
                db.asset.procurement_id, db.asset.assigned_to, db.asset.remarks,
                db.asset.hardware_status],
        links=[view_history_link, change_assignee_button, change_status_button],
        searchable=True, csv=True, editable=False, deletable=delete,
        details=False, create=False
    )
    grid.elements(_class='web2py_console  ')[0].components[0] = add_button

    return locals()


def add_asset():
    db.asset.assigned_to.writable = db.asset.transferred_to.writable = False
    form = SQLFORM.factory(db.asset)
    if form.process().accepted:
        db.asset.insert(**form.vars, **{'assigned_to': auth.user})
        response.flash = 'Asset is added'
        redirect(URL('asset', 'view.html'), client_side=True)
    return form


@auth.requires_membership(group_id=1)
def view_audit():
    db.asset.id.readable = db.asset.remarks.readable = \
        db.asset.transferred_to.readable = False
    button = [
        lambda row: A(
            'Audit', _class='button btn btn-secondary', _href='#audit',
            **{'_data-toggle': 'modal', '_data-rowid': row.asset_id}
        )
    ]
    form = SQLFORM.factory(
        Field('Asset'),
        Field('audited_on', 'datetime', requires=IS_NOT_EMPTY())
    )
    grid = SQLFORM.grid(
        db.asset, searchable=True, csv=True, editable=False,
        deletable=False, details=False, create=False, links=button
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
        redirect(URL('asset', 'view_audit.html'), client_side=True)
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
        if asset.transferred_to:
            db.asset_history.insert(
                asset_id=asset.asset_id,
                asset_operation=request_rejected,
                information="changing assignee to a new user",
                user_signature=auth.user
            )
        db(db.asset.asset_id == assign_to_form.vars.Asset).update(
            transferred_to=going_to_be_assigned
        )
        db.asset_history.insert(
            asset_id=asset.asset_id, asset_operation=request_assignee_change,
            information=str({'from': was_assigned_to.email,
                             'to': going_to_be_assigned.email}),
            user_signature=auth.user
        )
        redirect(URL('asset', 'view.html'), client_side=True)
    return assign_to_form


@auth.requires_login()
def index():
    redirect(URL('asset', 'home'))


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
    grid = SQLFORM.grid(db.asset_history, searchable=True, csv=True,
        editable=False, deletable=False, details=False, create=False,
        user_signature=False, maxtextlengths={'Information': 100},
        maxtextlength=100)
    return locals()
