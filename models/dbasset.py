# Table for entering teams in the project
from constants import asset_working_status, created, changed_assignee, changed_status

auth = Auth(db)
auth.settings.create_user_groups = None
auth.settings.everybody_group_id = 11


db.define_table('users',
                Field('user_data', db.auth_user),
                Field('user_name', 'string', requires=IS_NOT_EMPTY()),
                format='%(user_name)s')

db.define_table('team',
                Field('team_name', requires=(IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'team.team_name')), label='Team'),
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
                Field('hardware_status', requires=IS_IN_SET(asset_working_status)),
                format="%(asset_id)s %(name)s")

db.define_table('asset_history',
                Field('asset_id', 'string'),
                Field('asset_operation', 'string',
                      requires=(IS_NOT_EMPTY(), IS_IN_SET(created, changed_assignee, changed_status))),
                Field('information', 'text', requires=IS_NOT_EMPTY()),
                Field('occurred_time', 'datetime', default=request.now),
                Field('user_signature', db.users))


def add_user(id):
    user = db(db.auth_user.id == id).select().first()
    db.users.insert(user_data=user, user_name="{} {}".format(user.first_name, user.last_name))
    db.commit()


def add_asset(id):
    user = db(db.users.user_data == auth.user).select().first()
    asset = db(db.asset.id == id).select().first()
    db.asset_history.insert(asset_id=asset.asset_id, asset_operation=created,
                            information='Asset is newly added', user_signature=user)


db.auth_user._after_insert.append(lambda f, i: add_user(i))
db.asset._after_insert.append(lambda f, i: add_asset(i))
