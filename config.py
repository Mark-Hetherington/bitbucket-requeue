import os

config_vars = {
    'username': os.getenv('bitbucket_user'),
    'password': os.getenv('bitbucket_password'),
    'workspace': '<workspace identifier>',
    'repo_slug': '<repo slug>'
}
