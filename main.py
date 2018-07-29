import secrets
import string

from gitlab import Gitlab

from config import Config, ConfigOption
from directory import Directory


def create_user(gitlab, dn, attrs):
    password = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(20))
    gitlab.users.create({
        'username': attrs['uid'][0].decode(),
        'password': password,
        'name': attrs['displayName'][0].decode(),
        'email': attrs['mail'][0].decode(),
        'skip_confirmation': 'true',
        'provider': 'ldapmain',
        'extern_uid': dn
    })
    print("Created user {} ({}) in Gitlab".format(attrs['uid'][0].decode(), attrs['displayName'][0].decode()))


def main():
    config = Config((
        ConfigOption('LDAP_URL', '--ldap-host'),
        ConfigOption('LDAP_DN', '--ldap-dn'),
        ConfigOption('LDAP_PASSWORD', '--ldap-password'),

        ConfigOption('LDAP_USERS', '--ldap-users'),
        ConfigOption('LDAP_GROUPS', '--ldap-groups'),
        ConfigOption('LDAP_USER_FILTER', '--ldap-user-filter'),

        ConfigOption('GITLAB_URL', '--gitlab-url'),
        ConfigOption('GITLAB_TOKEN', '--gitlab-token')
    )).get()

    gitlab = Gitlab(config['GITLAB_URL'], private_token=config['GITLAB_TOKEN'])
    directory = Directory(config['LDAP_URL'], config['LDAP_DN'], config['LDAP_PASSWORD'])

    ldap_users = directory.get_users(config['LDAP_USERS'], config['LDAP_USER_FILTER'])
    for dn, attrs in ldap_users:
        gitlab_user = gitlab.users.list(username=attrs['uid'])
        if not gitlab_user:
            create_user(gitlab, dn, attrs)


if __name__ == '__main__':
    main()
