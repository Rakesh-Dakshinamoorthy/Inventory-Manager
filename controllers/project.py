# import any files needed for development
from gluon.html import BUTTON
from gluon.contrib.appconfig import AppConfig
from helpers import UsersDB, AssetDB

app_config = AppConfig(reload=False)
default_password = app_config.get('password.default_password')


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


def is_team_deletable(team_name):
    if db(db.asset.assigned_to.belongs(
            list(map(lambda each: each.member_name.id,
                     db(db.team_members.team_name == team_name).select()
                     ))
    )).select():
        return False
    else:
        return True


@auth.requires_login()
def team():
    # Grid to display the teams
    db.team.id.readable = False
    manager_btn = lead_btn = member_btn = delete = False
    users = UsersDB(db)
    managers = list(map(lambda each: each.email, users.managers()))
    leads = list(map(lambda each: each.email, users.leads()))
    members = list(map(lambda each: each.email, users.get_users()))
    user = auth.user

    if auth.has_membership(group_id=1):
        buttons = [members_link, manager_button, lead_button, member_button]
        query = db.team
        width = 'width:620px'
        manager_btn = lead_btn = member_btn = True
        delete = is_team_deletable
    elif auth.has_membership(group_id=2):
        width = 'width:400px'
        query = db(db.team.manager_name == user)
        buttons = [members_link, lead_button, member_button]
        lead_btn = member_btn = True
    elif auth.has_membership(group_id=3):
        query = db(db.team.lead_name == user)
        width = 'width:400px'
        buttons = [members_link, manager_button, member_button]
        manager_btn = member_btn = True

    grid = SQLFORM.grid(
        query, links=buttons, searchable=True, csv=False, editable=False,
        deletable=delete, details=False, create=False
    )
    add_button = BUTTON(
        "Add Team", _type="button", _class="btn btn-primary",
        **{'_data-toggle': "modal", '_data-target': "#addteam"}
    )
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
        db.team.insert(team_name=form.vars.team_name,
                       manager_name=auth.user,
                       lead_name=auth.user)
        db.commit
        response.flash = "Team is added"
        redirect(URL('project', 'team.html'), client_side=True)
    return form


@auth.requires_signature()
def assign_manager():
    assign_manager_form = SQLFORM.factory(
        Field('Team'),
        Field('Manager', requires=IS_IN_SET(request.vars.managers))
    )
    if assign_manager_form.process().accepted:
        manager_name = db(
            db.auth_user.email == assign_manager_form.vars.Manager
        ).select().first()
        db(db.team.team_name == assign_manager_form.vars.Team).update(
            manager_name=manager_name
        )
        redirect(URL('project', 'team.html'), client_side=True)
    return assign_manager_form


@auth.requires_signature()
def assign_lead():
    assign_lead_form = SQLFORM.factory(
        Field('Team'),
        Field('Lead_name', requires=IS_IN_SET(request.vars.leads),
              label='Lead')
    )
    if assign_lead_form.process().accepted:
        lead_name = db(
            db.auth_user.email == assign_lead_form.vars.Lead_name
        ).select().first()
        db(db.team.team_name == assign_lead_form.vars.Team).update(
            lead_name=lead_name
        )
        redirect(URL('project', 'team.html'), client_side=True)
    return assign_lead_form


@auth.requires_signature()
def assign_member():
    assign_member_form = SQLFORM.factory(
        Field('Team'),
        Field('Member', requires=IS_IN_SET(request.vars.members))
    )
    if assign_member_form.process().accepted:
        team = db(
            db.team.team_name == assign_member_form.vars.Team
        ).select().first()
        member_name = db(
            db.auth_user.email == assign_member_form.vars.Member
        ).select().first()
        db.team_members.update_or_insert(
            db.team_members.member_name == member_name,
            team_name=team,
            member_name=member_name
        )
        redirect(URL('project', 'team.html'), client_side=True)
    return assign_member_form


def users():
    if not(auth.has_membership(role="Managers") or
           auth.has_membership(role="Administrator")):
        redirect(URL('default', 'user', args=['not_authorized']))

    db.auth_user.id.readable = db.auth_user.password.readable = \
        db.auth_user.registration_key.readable = \
        db.auth_user.reset_password_key.readable = \
        db.auth_user.registration_id.readable = False
    permission_form = permission()
    add_user_form = add_user()
    add_button = BUTTON(
        'Add User', _type='button', _class='btn btn-primary',
        **{'_data-toggle': 'modal', '_data-target': '#add_user'}
    )

    buttons = [
        lambda row: A("Assign Permission", _href='#permission',
                      _class="btn btn-default btn-secondary",
                      **{'_data-rowid': row.email, '_data-toggle': "modal"}
                      ),
        lambda row: A("Delete", _class="btn btn-default btn-secondary",
                      callback=URL('project', 'delete_user', args=[row.id])
                      )
    ]

    grid = SQLFORM.grid(
        db.auth_user, searchable=True, csv=False, editable=False,
        deletable=False, details=False, create=False, maxtextlength=50,
        links=buttons
    )
    grid.elements(_class='web2py_console  ')[0].components[0] = add_button
    for _ in grid.elements(_class='row_buttons'):
        _.attributes['_style'] = 'width:280px'
    return locals()


def add_user():
    auth = Auth(db)
    form = SQLFORM.factory(
        Field('user_name', length=128, default='',
              requires=IS_NOT_EMPTY(error_message=auth.messages.is_empty)),
        Field('email', length=128, default='', unique=True,
              requires=[
                  IS_NOT_IN_DB(
                      db, "{}.email".format(auth.settings.table_user_name)
                  ),
                  IS_MATCH('[-a-zA-Z0-9.`?{}]+@wipro.com',
                           error_message='Enter wipro mail id')
              ]),
    )

    if form.process().accepted:
        user = db.auth_user.insert(user_name=form.vars.user_name,
                                   email=form.vars.email,
                                   password=CRYPT().validate(default_password))
        auth.add_membership(4, user.id)
        db.commit()
        redirect(URL('project', 'users.html'), client_side=True)
    return form


def delete_user():
    row_id = request.args[0]
    user = db(db.auth_user.id == row_id).select().first()
    if db(db.asset.assigned_to == user).select():
        session.flash = 'Cannot delete this member. ' \
                        'Assets are tagged to the member'
    elif db(db.team.manager_name == user).select():
        session.flash = 'Cannot delete this member. ' \
                        'Member is assigned to a team as a manager'
    elif db(db.team.lead_name == user).select():
        session.flash = 'Cannot delete this member. ' \
                        'Member is assigned to a team as a lead'
    else:
        db(db.auth_user.id == row_id).delete()
        db.commit()
    redirect(URL('project', 'users'), client_side=True)


def permission():
    permissions = list(map(lambda perm: perm.role,
                           db().select(db.auth_group.role))
                       )
    form = SQLFORM.factory(
        Field('user'),
        Field('permission', requires=IS_IN_SET(permissions))
    )
    if form.process().accepted:
        user_id = \
            db(db.auth_user.email == form.vars.user).select().first()
        group_id = \
            db(db.auth_group.role == form.vars.permission).select().first()
        db(
            db.auth_membership.user_id == user_id
        ).select().first().update_record(group_id=group_id)
        redirect(URL('project', 'users.html'), client_side=True)

    return form


def delete_member():
    row_id = request.args[0]
    db(db.team_members.id == row_id).delete()
    redirect(URL('project', 'members',
                 args=[request.args[1]]), client_side=True)


@auth.requires_login()
def members():
    db.team_members.id.readable = db.team_members.team_name.readable = False
    team_id = int(request.args[0])
    team = db(db.team.id == team_id).select().first().team_name

    buttons = [
        lambda row: A(
            "Delete", _class="btn btn-default btn-secondary",
            callback=URL('project', 'delete_member', args=[row.id, team_id])
        )
    ]

    grid = SQLFORM.grid(
        db(db.team_members.team_name == team_id), searchable=False, csv=False,
        editable=False, deletable=False, details=False, create=False,
        user_signature=False, links=buttons
    )
    return locals()


# @auth.requires_login()
# def dashboard():
#     user_id = int(request.args[0])
#     users = UsersDB(db)
#     membership = db(
#         db.auth_membership.user_id == users.user_id_map()[user_id].user_data.id
#     ).select().first().group_id.id
#     dashboard_data = {2: _get_manager_dashboard,
#                       3: _get_lead_dashboard,
#                       11: _get_tester_dashboard,
#                       10: _get_owner_dashboard}
#     return dashboard_data[membership](user)
#     return _get_tester_dashboard(user_id)
#     pass


def member():
    user_id = int(request.args[0])
    assets = AssetDB(db)
    assets_df = assets.user_assets_df(user_id)
    categories = dict(list(
        map(lambda category: (assets.category_name(category[0]), category[1]),
            dict(assets_df.category.value_counts()).items())
    ))
    data = {'categories': categories, 'assets': len(assets_df.index)}
    grid = SQLFORM.grid(
        db(db.asset.assigned_to == assets.user_id_map().get(user_id)),
        paginate=50, searchable=False, csv=False, editable=False,
        deletable=False, details=False, create=False
    )
    return locals()


# def _get_tester_dashboard(user_id):
#     assets = AssetDB(db)
#     assets_df = assets.user_assets_df(user_id)
#     categories = dict(list(
#         map(lambda category: (assets.category_name(category[0]), category[1]),
#             dict(assets_df.category.value_counts()).items())
#     ))
#     return {'categories': categories, 'assets': len(assets_df.index)}


@auth.requires_login()
def index():
    redirect(URL('project', 'team'))
