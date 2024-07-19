from github import Github
from github import Auth

class GitHandler:
    def __init__(self, token):
        auth = Auth.Token(token)
        self.git = Github(auth=auth)


    def get_service(self):
        return self.git
    
        