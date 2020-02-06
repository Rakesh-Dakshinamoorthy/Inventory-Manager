# import any files needed for development
from gluon.html import BUTTON


@auth.requires_login()
def team():
    # Grid to display the teams
    db.team.id.readable = db.team.manager_name.readable = \
        db.team.lead_name.readable = False
    manager_btn = lead_btn = member_btn = False
    manager_button = lambda row: A("Assign Manager",
                                   _class="button btn btn-secondary",
                                   _href="#assignmanager",
                                   **{'_data-toggle': "modal",
                                      '_data-rowid': row.team_name})
    lead_button = lambda row: A("Assign Lead",
                                _class="button btn btn-secondary",
                                _href="#assignlead",
                                **{'_data-toggle': "modal",
                                   '_data-rowid': row.team_name})
    member_button = lambda row: A("Assign Member",
                                  _class="button btn btn-secondary",
                                  _href="#assignmember",
                                  **{'_data-toggle': "modal",
                                     '_data-rowid': row.team_name})
    user = db(db.users.user_data == auth.user).select().first()

    if auth.has_membership(group_id=10):
        buttons = [manager_button, lead_button, member_button]
        query = db.team
        width = 'width:420px'
        manager_btn = lead_btn = member_btn = True
    elif auth.has_membership(group_id=2):
        width = 'width:280px'
        team_id = list(map(lambda row: row.team_name.id,
                           db(db.teams_map.manager == user).select()))
        query = db.team.id.belongs(team_id)
        buttons = [lead_button, member_button]
        lead_btn = member_btn = True
    elif auth.has_membership(group_id=3):
        team_id = list(map(lambda row: row.team_name.team_name.id,
                           db(db.leads.team_lead == user).select()))
        query = db.team.id.belongs(team_id)
        width = 'width:280px'
        buttons = [manager_button, member_button]
        manager_button = member_btn = True

    grid = SQLFORM.grid(query, links=buttons, searchable=True, csv=False,
                        editable=False, deletable=False, details=False,
                        create=False)
    add_button = BUTTON("Add Team", _type="button", _class="btn btn-primary",
                        **{'_data-toggle': "modal",
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
    >>> add_team()
    :return: form object
    """
    db.team.manager_name.readable = db.team.manager_name.writable = False
    db.team.lead_name.readable = db.team.lead_name.writable = False
    form = SQLFORM.factory(db.team)
    if form.process().accepted:
        user = db(db.users.user_data == auth.user).select().first()
        team_id = db.team.insert(team_name=form.vars.team_name,
                                 manager_name=user,
                                 lead_name=user)
        db.commit
        response.flash = "Team is added"
        redirect(URL('project', 'team.html'), client_side=True)
    return form


@auth.requires_signature()
def assign_manager():
    managers = list(
        map(lambda man: man.user_name,
            db(db.users.user_data.belongs(
                list(map(lambda each: each.user_id,
                         db(db.auth_membership.group_id == 2).select()))
            )).select()))

    assign_manager_form = SQLFORM.factory(Field('Team'),
                                          Field('Manager',
                                                requires=IS_IN_SET(managers)))

    if assign_manager_form.process().accepted:
        manager_name = db(
            db.users.user_name == assign_manager_form.vars.Manager
        ).select().first()
        db(db.team.team_name == assign_manager_form.vars.Team).update(
            manager_name=manager_name)
        redirect(URL('project', 'team.html'), client_side=True)
    return assign_manager_form


@auth.requires_signature()
def assign_lead():
    leads = list(
        map(lambda man: man.user_name,
            db(db.users.user_data.belongs(
                list(map(lambda each: each.user_id,
                         db(db.auth_membership.group_id == 3).select()))
            )).select()))
    assign_lead_form = SQLFORM.factory(Field('Team'),
                                       Field('Lead_name',
                                             requires=IS_IN_SET(leads),
                                             label='Lead'))

    if assign_lead_form.process().accepted:
        lead_name = db(
            db.users.user_name == assign_lead_form.vars.Lead_name
        ).select().first()
        db(db.team.team_name == assign_lead_form.vars.Team).update(
            lead_name=lead_name)
        redirect(URL('project', 'team.html'), client_side=True)
    return assign_lead_form


@auth.requires_signature()
def assign_member():
    members = list(
        map(lambda man: man.user_name,
            db(db.users.user_data.belongs(
                list(map(lambda each: each.user_id,
                         db(db.auth_membership.group_id == 11).select()))
            )).select()))

    assign_member_form = SQLFORM.factory(Field('Team'),
                                         Field('Member',
                                               requires=IS_IN_SET(members)))
    if assign_member_form.process().accepted:
        member_name = db(
            db.users.user_name == assign_member_form.vars.Member
        ).select().first()
        if db(db.team_members.team_name == assign_member_form.vars.Team and
              db.team_members.member_name == member_name).select().first() is\
                None:
            db.team_members.insert(team_name=assign_member_form.vars.Team,
                                   member_name=member_name)
        redirect(URL('project', 'team.html'), client_side=True)
    return assign_member_form


@auth.requires_membership(group_id=10)
def managers():
    managers = db(db.auth_membership.group_id == 2).select(
        db.auth_membership.user_id)
    managers = list(map(lambda man: "{} {}".format(man.user_id.first_name,
                                                   man.user_id.last_name),
                        managers))
    managers_updated = list(map(lambda man: man.Manager, db().select(
        db.managers.Manager)))
    managers_to_update = list(
        filter(lambda man: man not in managers_updated, managers))
    for manager in managers_to_update:
        db.managers.insert(Manager=manager)
    db.commit()
    db.managers.id.readable = False
    db.managers.Lead_name.readable = False
    buttons = [lambda row: BUTTON("Add Lead", _type="button",
                                  _class="btn btn-default btn-secondary",
                                  **{'_data-toggle': "modal",
                                     '_data-target': "#addlead",
                                     '_data-rowid': row.Manager})]
    grid = SQLFORM.grid(db.managers, searchable=False, csv=False,
                        editable=False, deletable=False, details=False,
                        create=False, maxtextlength=70, links=buttons)
    return locals()


@auth.requires_membership(group_id=10)
def users():
    db.users.id.readable = False
    db.users.user_data.readable = False
    form = permission()
    buttons = [lambda row: A("Assign Permission", _href='#permission',
                             _class="btn btn-default btn-secondary",
                             **{'_data-rowid': row.user_name,
                                '_data-toggle': "modal"})]
    grid = SQLFORM.grid(db.users, searchable=True, csv=False,
                        editable=False, deletable=False, details=False,
                        create=False, maxtextlength=50, links=buttons)
    for _ in grid.elements(_class='row_buttons'):
        _.attributes['_style'] = 'width:20px'
    return locals()


@auth.requires_signature()
def permission():
    permissions = list(map(lambda perm: perm.role,
                           db().select(db.auth_group.role)))
    form = SQLFORM.factory(Field('user'),
                           Field('permission',
                                 requires=IS_IN_SET(permissions)))
    if form.process().accepted:
        user_id = db(
            db.users.user_name == form.vars.user).select().first().user_data
        group_id = db(
            db.auth_group.role == form.vars.permission).select().first()
        db(
            db.auth_membership.user_id == user_id
        ).select().first().update_record(group_id=group_id)
        redirect(URL('project', 'users.html'), client_side=True)

    return form
