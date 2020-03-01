# import any files needed for development
from web_page_data import AboutPage
from helpers import UsersDB

@auth.requires_login()
def home():
    database = UsersDB(db)
    users_to_add = database.get_newly_added_user()
    for user in users_to_add:
        db.users.insert(user_data=user, user_name="{} {}".format(
            user.first_name, user.last_name))
    db.commit()
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
        db.commit
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

    def change_assignee(row):
        return A("Change Assignee", _class="button btn btn-secondary", _href="#changeassignee",
                 **{'_data-toggle': "modal", '_data-rowid': row.asset_id})


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

    grid = SQLFORM.grid(query, links=[change_assignee], searchable=True, csv=False, editable=False, deletable=delete,
                        details=False, create=False)
    grid.elements(_class='web2py_console  ')[0].components[0] = add_button

    return locals()


def add():
    db.asset.assigned_to.writable = False
    form = SQLFORM.factory(db.asset)
    if form.process().accepted:
        user = db(db.users.user_data == auth.user).select().first()
        asset_id = db.asset.insert(**form.vars, **{'assigned_to': user})
        db.asset_history.insert(asset_id="{}:{}".format(asset_id.id, asset_id.name), asset_operation='created',
                                information='Asset is newly added', user_signature=user.user_name)
        db.commit
        response.flash = "Asset is added"
        redirect(URL('asset', 'view.html'), client_side=True)
    return form


def change_assignee():

    assign_to_form = SQLFORM.factory(Field('Asset'), Field('assigned_to',
                                                           requires=IS_IN_SET(request.vars.users)))
    if assign_to_form.process().accepted:
        assigned_to = db(db.users.user_name == assign_to_form.vars.assigned_to).select().first()
        db(db.asset.asset_id == assign_to_form.vars.Asset).update(assigned_to=assigned_to)
        redirect(URL('asset', 'view.html'), client_side=True)
    return assign_to_form


@auth.requires_login()
def index():
    redirect(URL('asset', 'home'))



