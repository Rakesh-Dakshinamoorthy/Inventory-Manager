# Table for entering teams in the project
from constants import *

auth = Auth(db)
auth.settings.create_user_groups = None
auth.settings.everybody_group_id = 4


db.define_table('team',
                Field('team_name', unique=True,
                      requires=(IS_NOT_EMPTY(),
                                IS_NOT_IN_DB(db, 'team.team_name')),
                      label='Team'),
                Field('manager_name', db.auth_user, label='Manager'),
                Field('lead_name', db.auth_user, label='Lead'),
                format="%(team_name)s")

db.define_table('team_members',
                Field('team_name', db.team, label='Team'),
                Field('member_name', db.auth_user, label='Member'),
                format=lambda r: "{}".format(r.member_name.user_name))

db.define_table('asset_category',
                Field('category', unique=True,
                      requires=(IS_NOT_IN_DB(db, 'asset_category.category'),
                                IS_NOT_EMPTY())),
                Field('description', 'text',
                      requires=(IS_LENGTH(1024), IS_NOT_EMPTY())),
                format="%(category)s")

db.define_table('asset',
                Field('asset_id', label="ID", default="NA",
                      requires=ANY_OF(
                          [IS_IN_SET(['NA']),
                           IS_NOT_IN_DB(db, 'asset.asset_id')]
                      )),
                Field('serial_no', label="Serial no/Part no", default='NA',
                      requires=ANY_OF(
                          [IS_IN_SET(['NA']),
                           IS_NOT_IN_DB(db, 'asset.serial_no')]
                      )),
                Field('category', db.asset_category),
                Field('name', requires=IS_NOT_EMPTY()),
                Field('procurement_id', requires=IS_NOT_EMPTY()),
                Field('assigned_to', db.auth_user),
                Field('remarks', 'string'),
                Field('hardware_status', label="Status",
                      requires=IS_IN_SET(asset_working_status)),
                Field('last_audited_on', 'datetime', default=None),
                Field('transferring_to', db.auth_user, default=None))

db.define_table('asset_history',
                Field('asset_id', requires=IS_IN_DB(db, 'asset.id')),
                Field('asset_operation', 'string',
                      requires=(IS_NOT_EMPTY(),
                                IS_IN_SET(created, request_assignee_change,
                                          changed_status, audited,
                                          assignee_changed))),
                Field('information', 'text', requires=IS_NOT_EMPTY()),
                Field('occurred_time', 'datetime', default=request.now),
                Field('user_signature', db.auth_user))


def add_asset_history(id):
    db.asset_history.insert(
        asset_id=id,
        asset_operation=created, information='Asset is newly added',
        user_signature=auth.user
    )


db.asset._after_insert.append(lambda f, i: add_asset_history(i))
