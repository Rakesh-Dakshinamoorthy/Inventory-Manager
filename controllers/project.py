# import any files needed for development
import pandas as pd
from gluon.html import BUTTON
from helpers import UsersDB, AssetDB


@auth.requires_login()
def team():
    # Grid to display the teams
    db.team.id.readable = False
    manager_btn = lead_btn = member_btn = delete = False
    users = UsersDB(db)
    managers = list(map(lambda each: each.user_name, users.managers()))
    leads = list(map(lambda each: each.user_name, users.leads()))
    members = list(map(lambda each: each.user_name, users.get_users()))

    def manager_button(row):
        return A("Assign Manager", _class="button btn btn-secondary", _href="#assignmanager",
                 **{'_data-toggle': "modal", '_data-rowid': row.team_name})

    def lead_button(row):
        return A("Assign Lead", _class="button btn btn-secondary", _href="#assignlead",
                 **{'_data-toggle': "modal", '_data-rowid': row.team_name})

    def member_button(row):
        return A("Assign Member", _class="button btn btn-secondary", _href="#assignmember",
                 **{'_data-toggle': "modal", '_data-rowid': row.team_name})

    user = db(db.users.user_data == auth.user).select().first()

    if auth.has_membership(group_id=10):
        buttons = [manager_button, lead_button, member_button]
        query = db.team
        width = 'width:530px'
        manager_btn = lead_btn = member_btn = delete = True
    elif auth.has_membership(group_id=2):
        width = 'width:300px'
        query = db(db.team.manager_name == user)
        buttons = [lead_button, member_button]
        lead_btn = member_btn = True
    elif auth.has_membership(group_id=3):
        query = db(db.team.lead_name == user)
        width = 'width:300px'
        buttons = [manager_button, member_button]
        manager_button = member_btn = True

    grid = SQLFORM.grid(query, links=buttons, searchable=True, csv=False, editable=False, deletable=delete,
                        details=False, create=False)
    add_button = BUTTON("Add Team", _type="button", _class="btn btn-primary", **{'_data-toggle': "modal",
                                                                                 '_data-target': "#addteam"})
    grid.elements(_class='web2py_console  ')[0].components[0] = add_button
    for _ in grid.elements(_class='row_buttons'):
        _.attributes['_style'] = width
    return locals()


@auth.requires_signature()
def add_team():
    """
    This method creates a basic form
    :param table: table for which the form needs to be created
    :param flash_message: message to be flashed on successful form submission
    :param redirect_path: path to which page to be redirected after the form
    submission
    :return: form object
    """
    db.team.manager_name.readable = db.team.manager_name.writable = False
    db.team.lead_name.readable = db.team.lead_name.writable = False
    form = SQLFORM.factory(db.team)
    if form.process().accepted:
        user = db(db.users.user_data == auth.user).select().first()
        db.team.insert(team_name=form.vars.team_name, manager_name=user, lead_name=user)
        db.commit
        response.flash = "Team is added"
        redirect(URL('project', 'team.html'), client_side=True)
    return form


@auth.requires_signature()
def assign_manager():
    assign_manager_form = SQLFORM.factory(Field('Team'),
                                          Field('Manager', requires=IS_IN_SET(request.vars.managers)))
    if assign_manager_form.process().accepted:
        manager_name = db(db.users.user_name == assign_manager_form.vars.Manager).select().first()
        db(db.team.team_name == assign_manager_form.vars.Team).update(manager_name=manager_name)
        redirect(URL('project', 'team.html'), client_side=True)
    return assign_manager_form


@auth.requires_signature()
def assign_lead():
    assign_lead_form = SQLFORM.factory(Field('Team'),
                                       Field('Lead_name', requires=IS_IN_SET(request.vars.leads), label='Lead'))
    if assign_lead_form.process().accepted:
        lead_name = db(db.users.user_name == assign_lead_form.vars.Lead_name).select().first()
        db(db.team.team_name == assign_lead_form.vars.Team).update(lead_name=lead_name)
        redirect(URL('project', 'team.html'), client_side=True)
    return assign_lead_form


@auth.requires_signature()
def assign_member():
    assign_member_form = SQLFORM.factory(Field('Team'),
                                         Field('Member', requires=IS_IN_SET(request.vars.members)))
    if assign_member_form.process().accepted:
        team = db(db.team.team_name == assign_member_form.vars.Team).select().first()
        member_name = db(db.users.user_name == assign_member_form.vars.Member).select().first()
        db.team_members.update_or_insert(db.team_members.member_name == member_name,
                                         team_name=team, member_name=member_name)
        redirect(URL('project', 'team.html'), client_side=True)
    return assign_member_form


def users():
    if not(auth.has_membership(group_id=2) or auth.has_membership(group_id=10)):
        redirect(URL('default', 'user', args=['not_authorized']))

    db.users.id.readable = False
    db.users.user_data.readable = False
    form = permission()
    buttons = [lambda row: A("Assign Permission", _href='#permission', _class="btn btn-default btn-secondary",
                             **{'_data-rowid': row.user_name, '_data-toggle': "modal"})]
    grid = SQLFORM.grid(db.users, searchable=True, csv=False, editable=False, deletable=False, details=False,
                        create=False, maxtextlength=50, links=buttons)
    for _ in grid.elements(_class='row_buttons'):
        _.attributes['_style'] = 'width:20px'
    return locals()


def permission():
    permissions = list(map(lambda perm: perm.role, db().select(db.auth_group.role)))
    form = SQLFORM.factory(Field('user'),
                           Field('permission', requires=IS_IN_SET(permissions)))
    if form.process().accepted:
        user_id = db(db.users.user_name == form.vars.user).select().first().user_data
        group_id = db(db.auth_group.role == form.vars.permission).select().first()
        db(db.auth_membership.user_id == user_id).select().first().update_record(group_id=group_id)
        redirect(URL('project', 'users.html'), client_side=True)

    return form


@auth.requires_login()
def dashboard():
    user_id = int(request.args[0])
    users = UsersDB(db)
    membership = db(db.auth_membership.user_id == users.user_id_map()[user_id].user_data.id).select().first().group_id.id
    # dashboard_data = {2: _get_manager_dashboard,
    #                   3: _get_lead_dashboard,
    #                   11: _get_tester_dashboard,
    #                   10: _get_owner_dashboard}
    # return dashboard_data[membership](user)
    return _get_tester_dashboard(user_id)


def member():
    user_id = int(request.args[0])
    assets = AssetDB(db)
    assets_df = assets.user_assets_df(user_id)
    categories = dict(list(map(lambda category: (assets.category_name(category[0]), category[1]),
                               dict(assets_df.category.value_counts()).items())))
    data = {'categories': categories, 'assets': len(assets_df.index)}
    grid = SQLFORM.grid(db(db.asset.assigned_to == assets.user_id_map().get(user_id)), paginate=50,
                        searchable=False, csv=False, editable=False, deletable=False, details=False, create=False)
    return locals()


def _get_tester_dashboard(user_id):
    assets = AssetDB(db)
    assets_df = assets.user_assets_df(user_id)
    categories = dict(list(map(lambda category: (assets.category_name(category[0]), category[1]), dict(assets_df.category.value_counts()).items())))
    return {'categories': categories, 'assets': len(assets_df.index)}


@auth.requires_login()
def index():
    redirect(URL('project', 'team'))
