# add imports that are needed

asset_working_status = ('Working', 'Not Working')
created = 'created'
request_assignee_change = 'change assignee request'
request_rejected = 'request rejected'
request_cancelled = 'request cancelled'
assignee_changed = 'assignee changed'
changed_status = 'changed status'
audited = 'audited'
add_user = 'add user'
add_asset_category = 'add category'
edit_remarks_value = 'changing the remarks'
add_assets = 'add assets'
import_audit = 'import audit'
import_list = [add_user, add_asset_category, add_assets, import_audit]
upload_fields = {
    add_user: ["user_name", "email"],
    add_asset_category: ["category", "description"],
    add_assets: ["asset_id", "serial_no", "category", "name", "procurement_id",
                 "assigned_to: optional", "remarks", "hardware_status"],
    import_audit: ["id", "hardware_status: optional",
                   "remarks: optional"]
}

