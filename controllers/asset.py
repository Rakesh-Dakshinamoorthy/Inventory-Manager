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
