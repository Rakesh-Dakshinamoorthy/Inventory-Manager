# import any files needed for development
from web_page_data import AboutPage
from helpers import UsersDB
from constants import asset_working_status, changed_status


def change_assignee_button(row):
    return A("Change Assignee", _class="button btn btn-secondary", _href="#changeassignee",
             **{'_data-toggle': "modal", '_data-rowid': row.asset_id})


def view_history_link(row):
    return A("History", _href=URL('asset', 'history', args=[row.asset_id]))


def change_status_button(row):
    return A("Change Status", _class="button btn btn-secondary",
             callback=URL('asset', 'change_status', args=[row.id]))


def change_status():
    asset = db(db.asset.id == request.args[0]).select().first()
    user = db(db.users.user_data == auth.user).select().first()
    new_status = asset_working_status[1] if asset.hardware_status == asset_working_status[0] else asset_working_status[
        0]
    db(db.asset.id == request.args[0]).update(hardware_status=new_status)
    db.asset_history.insert(asset_id=asset.asset_id, asset_operation=changed_status,
                            information='Asset hardware status changed to {}'.format(new_status), user_signature=user)
    redirect(URL('asset', 'view'), client_side=True)



@auth.requires_login()
def home():
    response.flash = T("Welcome to Inventory Manager")
    return AboutPage().body


@auth.requires_login()
def category():
    db.asset_category.id.readable = False
    delete = False
    if auth.has_membership(group_id=10):
        delete = True
    grid = SQLFORM.grid(db.asset_category, searchable=True, csv=False, editable=False, deletable=delete,
                        details=False, create=False,
                        maxtextlengths={'asset_category.category': 20, 'asset_category.description': 80})
    add_button = BUTTON("Add Category", _type="button", _class="btn btn-primary",
                        **{'_data-toggle': "modal", '_data-target': "#addcategory"})
    grid.elements(_class='web2py_console  ')[0].components[0] = add_button

    return locals()


def add_category():
    form = SQLFORM.factory(db.asset_category)
    if form.process().accepted:
        db.asset_category.insert(**form.vars)
        response.flash = "Asset category is added"
        redirect(URL('asset', 'category.html'), client_side=True)
    return form


@auth.requires_login()
def view():
    db.asset.id.readable = False
    database = UsersDB(db)
    users = list(database.user_name_map().keys())
    form = add()
    delete = False
    add_button = BUTTON("Add Asset", _type="button", _class="btn btn-primary",
                        **{'_data-toggle': "modal", '_data-target': "#addasset"})

    user = db(db.users.user_data == auth.user).select().first()

    if auth.has_membership(group_id=10):
        query = db.asset
        delete = True
    elif auth.has_membership(group_id=2):
        team = db(db.team.manager_name == user).select()
        team_id = list(map(lambda each: each.id, team))
        members = list()
        members.append(user.id)
        members.extend(list(map(lambda each: each.lead_name, team)))
        team_members = db(db.team_members.team_name.belongs(team_id)).select()
        members.extend(list(map(lambda each: each.member_name, team_members)))
        query = db(db.asset.assigned_to.belongs(set(members)))
    elif auth.has_membership(group_id=3):
        team = db(db.team.lead_name == user).select()
        team_id = list(map(lambda each: each.id, team))
        members = list()
        members.append(user.id)
        team_members = db(db.team_members.team_name.belongs(team_id)).select()
        members.extend(list(map(lambda each: each.member_name, team_members)))
        query = db(db.asset.assigned_to.belongs(set(members)))
    else:
        query = db(db.asset.assigned_to == user)

    grid = SQLFORM.grid(query, links=[view_history_link, change_assignee_button, change_status_button],
                        searchable=True, csv=False, editable=False, deletable=delete, details=False, create=False)
    grid.elements(_class='web2py_console  ')[0].components[0] = add_button

    return locals()


def add():
    db.asset.assigned_to.writable = False
    form = SQLFORM.factory(db.asset)
    if form.process().accepted:
        user = db(db.users.user_data == auth.user).select().first()
        db.asset.insert(**form.vars, **{'assigned_to': user})
        response.flash = "Asset is added"
        redirect(URL('asset', 'view.html'), client_side=True)
    return form


def update_asset():
    pass


def change_assignee():
    assign_to_form = SQLFORM.factory(Field('Asset'), Field('assigned_to',
                                                           requires=IS_IN_SET(request.vars.users)))
    if assign_to_form.process().accepted:
        user = db(db.users.user_data == auth.user).select().first()
        asset = db(db.asset.asset_id == assign_to_form.vars.Asset).select().first()
        was_assigned_to = asset.assigned_to
        going_to_be_assigned = db(db.users.user_name == assign_to_form.vars.assigned_to).select().first()
        db(db.asset.asset_id == assign_to_form.vars.Asset).update(assigned_to=going_to_be_assigned)
        db.asset_history.insert(asset_id=asset.asset_id, asset_operation='changed assignee',
                                information=str({"from":was_assigned_to.user_name,
                                                 "to": going_to_be_assigned.user_name}),
                                user_signature=user)
        redirect(URL('asset', 'view.html'), client_side=True)
    return assign_to_form


@auth.requires_login()
def index():
    redirect(URL('asset', 'home'))


@auth.requires_login()
def history():
    db.asset_history.id.readable = db.asset_history.asset_id.readable = False
    asset_id = request.args[0]
    grid = SQLFORM.grid(db(db.asset_history.asset_id == asset_id), searchable=False, csv=False, editable=False,
                        deletable=False, details=False, create=False, user_signature=False, maxtextlengths={'Information': 100}, maxtextlength=100)
    return locals()
