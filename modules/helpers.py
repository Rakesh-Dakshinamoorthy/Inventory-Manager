import time

class DBHelper(object):
    """
    This class has all the repeatedly used data base queries
    """
    manager_id = 2
    lead_id = 3
    owner_id = 10
    tester_id = 11

    def __init__(self, db):
        time.sleep(1)
        self.db = db

    def _get_users(self, group_id):
        user_ids = list(map(lambda each: each.user_id, self.db(self.db.auth_membership.group_id == group_id).select()))
        return self.db(self.db.users.user_data.belongs(user_ids)).select()

    @property
    def managers(self):
        return self._get_users(self.manager_id)

    @property
    def leads(self):
        return self._get_users(self.lead_id)

    @property
    def owners(self):
        return self._get_users(self.owner_id)

    @property
    def testers(self):
        return self._get_users(self.tester_id)

    def get_users(self):
        all_field = self.db.users.All
        return self.db().select(all_field)
