import pandas as pd
from gluon.tools import Auth


class UsersDB(object):
    """
    This class has all the repeatedly used user operation
    """
    manager_group_id = 2
    lead_group_id = 3
    admin_group_id = 1
    user_group_id = 4

    def __init__(self, db):
        self.db = db

    def _get_users(self, group_id):
        auth_membership = self.db.auth_membership
        users = self.db.auth_user
        user_ids = list(
            map(lambda each: each.user_id,
                self.db(auth_membership.group_id == group_id).select())
        )
        return self.db(users.id.belongs(user_ids)).select()

    def managers(self):
        return self._get_users(self.manager_group_id)

    def leads(self):
        return self._get_users(self.lead_group_id)

    def owners(self):
        return self._get_users(self.admin_group_id)

    def testers(self):
        return self._get_users(self.user_group_id)

    def get_users(self):
        users = self.db.auth_user
        return self.db(users.id > 0).select()

    def user_name_map(self):
        return dict(list(
            map(lambda user: (user.user_name, user), self.get_users())
        ))

    def user_id_map(self):
        return dict(list(
            map(lambda item: (item[1].id, item[1]),
                self.user_name_map().items())
        ))

    def user_id(self, name):
        return self.user_name_map().get(name).id

    def user_name(self, user_id):
        return self.user_id_map().get(user_id).user_name

    def get_user(self, user_info):
        if isinstance(user_info, int):
            return self.user_id_map().get(user_info)
        elif isinstance(user_info, str):
            return self.user_name_map().get(user_info)




class TeamDB(UsersDB):
    """
    This class has all the repeatedly used Team operations
    """

    def __init__(self, db):
        self.db = db
        super(TeamDB, self).__init__(self.db)

    def teams(self):
        team = self.db.Team
        return self.db(team.id > 0).select()

    def team_names(self):
        return list(map(str, self.teams()))


class MembersDB(TeamDB):
    """
    This class has all the data and method need for members table
    """

    def __init__(self, db):
        self.db = db
        super(MembersDB, self).__init__(self.db)

    def team_members(self):
        members = self.db.team_members
        return self.db(members.id > 0).select()

    def team_members_name(self):
        return list(map(str, self.team_members()))


class AssetCategoryDB(object):
    """
    This class has all the methods of asset category db
    """

    def __init__(self, db):
        self.db = db

    def category(self):
        category = self.db.asset_category
        return self.db(category.id > 0).select()

    def category_name(self, category_id):
        category = self.db.asset_category
        return self.db(category.id == category_id).select().first().category


class AssetDB(AssetCategoryDB,  MembersDB):
    """
    This class has all the method needed for the asset table
    """

    def __init__(self, db):
        self.db = db
        AssetCategoryDB.__init__(self, self.db)
        MembersDB.__init__(self, self.db)

    def assets(self):
        assets = self.db.asset
        return self.db(assets.id > 0).select()

    def user_assets(self, user_id):
        assets = self.db.asset
        return self.db(
            assets.assigned_to == self.user_id_map().get(user_id)
        ).select()

    def user_assets_df(self, user_id):
        return pd.DataFrame(self.user_assets(user_id).as_list())


class AddToDB(object):
    def __init__(self, db):
        self.db = db

    def add_new_asset(self, **kwargs):
        asset = self.db.asset
        asset.insert(**kwargs)

    def add_user(self, **kwargs):
        users = self.db.auth_user
        auth = Auth(self.db)
        user = users.insert(**kwargs)
        auth.add_membership(4, user.id)

    def add_asset_category(self, **kwargs):
        category = self.db.asset_category
        category.insert(**kwargs)
