# Table for entering teams in the project
auth = Auth(db)
auth.settings.create_user_groups = None
auth.settings.everybody_group_id = 11

db.define_table('users',
                Field('user_data', db.auth_user),
                Field('user_name', 'string', requires=IS_NOT_EMPTY()),
                format='%(user_name)s')

db.define_table("team",
                Field("team_name", requires=(IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'team.team_name')), label="Team"),
                Field('manager_name', db.users, label='Manager'),
                Field('lead_name', db.users, label='Lead'),
                format="%(team_name)s")

db.define_table('team_members',
                Field('team_name', db.team, label='Team'),
                Field('member_name', db.users, label='Member'),
                format=lambda r: "{} {}".format(r.member_name.user_name, r.team_name.team_name))

db.define_table('asset_category',
                Field('category', requires=(IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'asset_category.category'))),
                Field('description', 'text', requires=(IS_NOT_EMPTY(), IS_LENGTH(1024))),
                format="%(category)s")

db.define_table('asset',
                Field('asset_id', requires=(IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'asset.asset_id'))),
                Field('category', db.asset_category),
                Field('name', requires=IS_NOT_EMPTY()),
                Field('procurement_id', requires=IS_NOT_EMPTY()),
                Field('assigned_to', db.users),
                Field('remarks', 'string'),
                Field('hardware_status', requires=IS_IN_SET(('Working', 'Not Working'))),
                Field('modified_on', 'datetime', default=request.now, update=request.now),
                format="%(asset_id)s %(name)s")
