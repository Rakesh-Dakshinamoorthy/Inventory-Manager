# Table for entering teams in the project
auth = Auth(db)
auth.settings.create_user_groups = None
auth.settings.everybody_group_id = 11

db.define_table('users',
                Field('user_data', db.auth_user),
                Field('user_name', 'string', requires=IS_NOT_EMPTY()),
                format='%(user_name)s')

db.define_table("team",
                Field("team_name",
                      requires=(IS_NOT_EMPTY(),
                                IS_NOT_IN_DB(db, 'team.team_name')),
                      label="Team"),
                Field('manager_name', db.users, label='Manager'),
                Field('lead_name', db.users, label='Lead'),
                format="%(team_name)s"
                )

db.define_table('team_members',
                Field('team_name', requires=IS_IN_DB(db, 'team.team_name'),
                      label='Team'),
                Field('member_name', db.users, label='Member'),
                format="%(member_name)")

