# import any files needed for development
import os
import pandas as pd
from datetime import datetime
from web_page_data import AboutPage
from constants import *
from ui_elements import *
from helpers import AddToDB

app_config = AppConfig(reload=False)
default_password = app_config.get('password.default_password')


@auth.requires_login()
def index():
    redirect(URL('asset', 'home'))


@auth.requires_login()
def home():
    response.flash = T('Welcome to Inventory Manager')
    body = AboutPage().body
    admin_ids = list(map(
        lambda _: _.user_id, db(db.auth_membership.group_id == 1).select()
    ))
    admin_emails = list(map(
        lambda _: _.email, db(db.auth_user.id.belongs(admin_ids)).select()
    ))
    body.update({"footer": " ".join(admin_emails)})
    return body


def cancel_assignee():
    asset = db(db.asset.id == request.args[0]).select().first()
    db(db.asset.id == request.args(0)).update(transferring_to=None)
    db.asset_history.insert(
        asset_id=asset.asset_id, asset_operation=request_cancelled,
        information='Asset transfer canceled',
        user_signature=auth.user
    )
    db.commit()
    redirect(URL('asset', 'view.html', args=['transferring']),
             client_side=True)


def reject_assignee():
    asset = db(db.asset.id == request.args[0]).select().first()
    db(db.asset.id == request.args(0)).update(transferring_to=None)
    db.asset_history.insert(
        asset_id=asset.asset_id, asset_operation=request_rejected,
        information='Asset transfer request is rejected transferring back '
                    'to same user',
        user_signature=auth.user
    )
    db.commit()
    redirect(URL('asset', 'view.html', args=['undeclared']),
             client_side=True)


def accept_assignee():
    asset = db(db.asset.id == request.args(0)).select().first()
    db(db.asset.id == asset.id).update(
        assigned_to=asset.transferring_to, transferring_to=None
    )
    db.asset_history.insert(
        asset_id=asset.asset_id, asset_operation=assignee_changed,
        information="Asset transfer from {} to {}".format(
            asset.assigned_to.email, asset.transferring_to.email
        ),
        user_signature=auth.user
    )
    db.commit()
    redirect(URL('asset', 'view.html', args=['undeclared']),
             client_side=True)


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
    db.commit()
    redirect(URL('asset', 'view.html', args=['all']), client_side=True)


def __team_members():
    if auth.has_membership(group_id=2):
        team = db(db.team.manager_name == auth.user).select()
        team_id = list(map(lambda each: each.id, team))
        members = list()
        members.append(auth.user.id)
        members.extend(list(map(lambda each: each.lead_name, team)))
        team_members = db(db.team_members.team_name.belongs(team_id)).select()
        members.extend(list(map(lambda each: each.member_name, team_members)))
        return set(members)
    elif auth.has_membership(group_id=3):
        team = db(db.team.lead_name == auth.user).select()
        team_id = list(map(lambda each: each.id, team))
        members = list()
        members.append(auth.user.id)
        team_members = db(db.team_members.team_name.belongs(team_id)).select()
        members.extend(list(map(lambda each: each.member_name, team_members)))
        return set(members)


def __view_grids_templates(view='all'):
    if view == 'all':
        return {
            "fields": [db.asset.asset_id, db.asset.category, db.asset.name,
                       db.asset.procurement_id, db.asset.assigned_to,
                       db.asset.hardware_status, db.asset.remarks],
            "links": [view_history_link, change_assignee_button,
                      change_status_button, edit_remarks_button],
            "csv": True, "create": False, "editable": False, "create": False,
            "args": request.args, "searchable": True, "details": True,
            "deletable": True if auth.has_membership(group_id=1) else False,
            "maxtextlengths": {"asset.remarks": 40}
        }
    elif view == "transferring":
        return {
            "fields": [db.asset.asset_id, db.asset.category, db.asset.name,
                       db.asset.transferring_to],
            "links": [change_assignee_button, cancel_assignee_button],
            "csv": True, "create": False, "editable": False, "create": False,
            "args": request.args, "searchable": True, "details": False,
            "deletable": False
        }
    elif view == "undeclared":
        return {
            "fields": [db.asset.asset_id, db.asset.category, db.asset.name,
                       db.asset.remarks, db.asset.hardware_status,
                       db.asset.assigned_to],
            "links": [accept_assignee_button, reject_assignee_button],
            "csv": True, "create": False, "editable": False, "create": False,
            "args": request.args, "searchable": True, "details": False,
            "deletable": False
        }


@auth.requires_login()
def view():
    users = list(
        map(lambda user: user.email, db(db.auth_user.id > 0).select())
    )
    form = add_asset()
    undeclared_asset = db(db.asset.transferring_to == auth.user)

    if auth.has_membership(group_id=1):
        all_query = db(db.asset.id > 0)
        transferring_asset = db(db.asset.transferring_to != None)
    elif auth.has_membership(group_id=2):
        members = __team_members()
        all_query = db(db.asset.assigned_to.belongs(members))
        transferring_asset = db(
            (db.asset.assigned_to.belongs(members)) &
            (db.asset.transferring_to != None)
        )
    elif auth.has_membership(group_id=3):
        members = __team_members()
        all_query = db(db.asset.assigned_to.belongs(members))
        transferring_asset = db(
            (db.asset.assigned_to.belongs(members)) &
            (db.asset.transferring_to != None)
        )
    else:
        all_query = db(db.asset.assigned_to == auth.user)
        transferring_asset = db(
            (db.asset.assigned_to == auth.user) &
            (db.asset.transferring_to != None)
        )

    if request.args[0].lower() == 'all':
        query = all_query
    elif request.args[0].lower() == 'transferring':
        query = transferring_asset
    elif request.args[0].lower() == 'undeclared':
        query = undeclared_asset

    card_properties = view_asset_cards_property(
        all_query, transferring_asset, undeclared_asset
    )

    grid = SQLFORM.grid(query,
                        **__view_grids_templates(request.args[0].lower()),
                        paginate=20)

    if request.args[0].lower() == 'all' and len(request.args) == 1:
        grid.elements(_class='web2py_console  ')[0].components[0] = \
            btn_add_asset

    return locals()


def add_asset():
    db.asset.assigned_to.writable = db.asset.transferring_to.writable = False
    form = SQLFORM.factory(db.asset)
    if form.process().accepted:
        AddToDB(db).add_new_asset(**form.vars, **{'assigned_to': auth.user})
        response.flash = 'Asset is added'
        redirect(URL('asset', 'view.html', args=['all']), client_side=True)
    return form


def __category_deletable(row):
    return False if db(db.asset.category == row.id).select() else True


@auth.requires_login()
def category():
    db.asset_category.id.readable = False
    if auth.has_membership(group_id=1):
        deletable = __category_deletable
    else:
        deletable = False
    grid = SQLFORM.grid(
        db.asset_category, searchable=True, csv=False, editable=False,
        deletable=deletable, details=False, create=False,
        maxtextlengths={'asset_category.category': 20,
                        'asset_category.description': 80}
    )
    grid.elements(_class='web2py_console  ')[0].components[0] = \
        btn_add_asset_category
    return locals()


def add_category():
    form = SQLFORM.factory(db.asset_category)
    if form.process().accepted:
        AddToDB(db).add_asset_category(**form.vars)
        response.flash = 'Asset category is added'
        redirect(URL('asset', 'category.html'), client_side=True)
    return form


@auth.requires_membership(group_id=1)
def view_audit():
    db.asset.id.readable = db.asset.remarks.readable = \
        db.asset.transferring_to.readable = False

    grid = SQLFORM.grid(
        db.asset, searchable=True, csv=True, editable=False,
        deletable=False, details=False, create=False, links=[audit_button]
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
        if asset.transferring_to:
            db.asset_history.insert(
                asset_id=asset.asset_id,
                asset_operation=request_rejected,
                information="changing assignee to a new user",
                user_signature=auth.user
            )
        db(db.asset.asset_id == assign_to_form.vars.Asset).update(
            transferring_to=going_to_be_assigned
        )
        db.asset_history.insert(
            asset_id=asset.asset_id, asset_operation=request_assignee_change,
            information=str({'from': was_assigned_to.email,
                             'to': going_to_be_assigned.email}),
            user_signature=auth.user
        )
        redirect(URL('asset', 'view.html', args=['all']), client_side=True)
    return assign_to_form


@auth.requires_login()
def history():
    db.asset_history.id.readable = db.asset_history.asset_id.readable = False
    asset_id = request.args[0]
    grid = SQLFORM.grid(
        db(db.asset_history.asset_id == asset_id), searchable=False, csv=False,
        editable=False, deletable=False, details=False, create=False,
        args=request.args, user_signature=False,
        maxtextlengths={'Information': 100}, maxtextlength=100
    )
    return locals()


@auth.requires_membership(role="Administrator")
def view_asset_history():
    db.asset_history.id.readable = False
    grid = SQLFORM.grid(
        db.asset_history, searchable=True, csv=True,
        editable=False, deletable=False, details=False, create=False,
        user_signature=False, maxtextlengths={'Information': 100},
        maxtextlength=100, paginate=50
    )
    return {"grid": grid}


def edit_remarks():
    remarks_to_form = SQLFORM.factory(
        Field('Asset'),
        Field('remarks')
    )

    if remarks_to_form.process().accepted:
        asset = \
            db(db.asset.asset_id == remarks_to_form.vars.Asset).select().first()
        previous_remarks = asset.remarks

        db.asset_history.insert(
            asset_id=asset.asset_id,
            asset_operation=edit_remarks_value,
            information="changing remarks from '{}'".format(previous_remarks),
            user_signature=auth.user
            )
        db(db.asset.asset_id == remarks_to_form.vars.Asset).update(
            remarks=remarks_to_form.vars.remarks
        )
        redirect(URL('asset', 'view.html', args=['all']), client_side=True)
    return remarks_to_form


def __import_new_user(data, import_to_db, fields):
    if data.columns.tolist() != fields:
        raise HTTP(400, "Required field are missing")
    error = []
    for pos, _ in data.iterrows():
        try:
            import_to_db.add_user(
                user_name=_.user_name, email=_.email,
                password=CRYPT().validate(default_password)
            )
        except Exception:
            error.append(str(pos+2))
    return error


def __import_category(data, import_to_db, fields):
    if data.columns.tolist() != fields:
        raise HTTP(400, "Required field are missing")
    error = []
    for pos, _ in data.iterrows():
        try:
            import_to_db.add_asset_category(
                category=_.category, description=_.description
            )
        except Exception:
            error.append(str(pos+2))
    return error


def __mandatory_fields(fields):
    return list(filter(lambda each: ": optional" in each, fields))


def __optional_fields(fields):
    return filter(lambda each: ": optional" in each, fields)


def __import_assets(data, import_to_db, expected_fields):
    fields = __mandatory_fields(expected_fields)
    if not all(map(lambda x: x in data.columns.tolist(), fields)):
        raise HTTP(400, "Required field are missing")
    add_assignee = "assigned_to" in data.columns.tolist()
    error = []
    for pos, _ in data.iterrows():
        try:
            if add_assignee:
                if _.assigned_to != "EMPTY":
                    assignee = db(db.auth_user.email == _.assigned_to
                                  ).select().first()
                else:
                    assignee = auth.user
            else:
                assignee = auth.user
            import_to_db.add_new_asset(
                asset_id=_.asset_id, name=_["name"],
                procurement_id=_.procurement_id, remarks=_.remarks,
                hardware_status=_.hardware_status, assigned_to=assignee,
                category=db(
                    db.asset_category.category == _.category).select().first(),
            )
        except Exception as e:
            error.append(str(pos+2))
    return error


def __import_audit(data, expected_fields):
    fields = __mandatory_fields(expected_fields)
    if not all(map(lambda x: x in data.columns.tolist(), fields)):
        raise HTTP(400, "Required field are missing")
    status = "hardware_status" in data.columns.tolist()
    remarks = "remarks" in data.columns.tolist()
    error = []
    for pos, _ in data.iterrows():
        try:
            asset = db(db.asset.asset_id == _.asset_id).select().first()
            if status:
                if _.hardware_status != "EMPTY":
                    if asset.hardware_status != _.hardware_status:
                        db(db.asset.id == _.asset_id).update(
                            hardware_status=_.hardware_status)
                        db.asset_history.insert(
                            asset_id=_.asset_id,
                            asset_operation=changed_status,
                            information='Asset hardware status changed '
                                        'to {}'.format(_.hardware_status),
                            user_signature=auth.user
                        )
            if remarks:
                if _.remarks != "EMPTY":
                    previous_remarks = asset.remarks
                    db.asset_history.insert(
                        asset_id=asset.asset_id,
                        asset_operation=edit_remarks_value,
                        information="changing remarks from "
                                    "'{}'".format(previous_remarks),
                        user_signature=auth.user
                    )
                    db(db.asset.asset_id == _.asset_id).update(
                        remarks=_.remarks
                    )
            audit_time = datetime.now()
            db(db.asset.asset_id == _.asset_id).update(
                last_audited_on=audit_time)
            db.asset_history.insert(
                asset_id=asset.asset_id, asset_operation=audited,
                information='audited on: {}'.format(audit_time),
                user_signature=auth.user
            )
        except Exception:
            error.append(str(pos+2))
    return error


def import_data():
    import_data_form = SQLFORM.factory(
        Field('import_to', requires=IS_IN_SET(import_list)),
        Field('csv_file', 'upload', length=128)
    )
    error = ""
    if import_data_form.process().accepted:
        data_to_import = pd.read_csv(
            os.path.join(request.folder, 'uploads',
                         import_data_form.vars.csv_file),
            header=0, dtype=str
        )
        data_to_import.fillna(value="EMPTY", inplace=True)
        import_to_db = AddToDB(db)
        if import_data_form.vars.import_to == add_user:
            error = __import_new_user(data_to_import, import_to_db,
                                      upload_fields[add_user])
        elif import_data_form.vars.import_to == add_asset_category:
            error = __import_category(data_to_import, import_to_db,
                                      upload_fields[add_asset_category])
        elif import_data_form.vars.import_to == add_assets:
            error = __import_assets(data_to_import, import_to_db,
                                    upload_fields[add_assets])
        elif import_data_form.vars.import_to == import_audit:
            error = __import_audit(data_to_import, upload_fields[import_audit])
        db.commit()
        os.remove(os.path.join(request.folder, 'uploads',
                               import_data_form.vars.csv_file))

    return {"form": import_data_form, "upload_fields": upload_fields,
            "error": error}

