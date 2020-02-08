# import any files needed for development
from web_page_data import HomePageData


@auth.requires_login()
def home():
    users = db().select(db.auth_user.ALL)
    users_exist = list(map(lambda user: user.user_data.id,
                           db().select(db.users.user_data)))
    users_to_add = list(filter(lambda user: user.id not in users_exist, users))
    for user in users_to_add:
        db.users.insert(user_data=user, user_name="{} {}".format(
            user.first_name, user.last_name))
    db.commit()
    response.flash = T("Welcome to Inventory Manager")
    return HomePageData().body


@auth.requires_login()
def asset_category():
    db.asset_category.id.readable = db.asset_category.image.readable = False
    grid = SQLFORM.grid(db.asset_category, searchable=True, csv=False, editable=False, deletable=False,
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
        redirect(URL('asset', 'asset_category.html'), client_side=True)
        response.flash = "Asset category is added"
    return form

