# import any files needed for development


class AboutPage(object):

    def __init__(self):
        pass

    @property
    def body(self):
        body = """
        This is an Inventory Management tool developed and managed 
        by the Wipro Ltd. This tool is used for tracking asset and 
        for audit purpose. There are four types of user in this project
        """
        user = ['administrator', 'managers', 'leads', 'users']
        users_manual = {
            'administrator': "They are the tool owners who has all the access "
                             "to the tool and all the delete permission",
            'managers': "They have less limited access compared to the "
                        "Administrator but they have permission to delete or "
                        "create or modify an asset or a team under him",
            'leads': "They have less access compared to the Managers but they "
                     "have permission for their team",
            'users': "Permissions only to view their assets and modify the "
                     "working status of it"
        }

        return {'body': body, 'user': user,
                'user_manual': users_manual}
