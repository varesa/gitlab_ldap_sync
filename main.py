import secrets
import string

from gitlab import Gitlab, DEVELOPER_ACCESS

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


def create_group(gitlab, dn, attrs, parent_id):
    group_name = attrs['cn'][0].decode()
    gitlab.groups.create({
        'name': group_name,
        'path': group_name,
        'parent_id': parent_id
    })
    print("Created group {} in Gitlab".format(group_name))


def create_group_if_missing(gitlab, dn, attrs, parent_id):
    group_name = attrs['cn'][0].decode()

    gitlab_groups = gitlab.groups.list(search=group_name)
    for group in gitlab_groups:
        if group.path == group_name:
            break  # Group exists
    else:
        create_group(gitlab, dn, attrs, parent_id)


def set_group_members(gitlab, group, target_users):
    # print("Target members for group {}: {}".format(group.name, ' '.join(target_users)))
    existing_members = group.members.list()
    existing_usernames = []
    for member in existing_members:
        existing_usernames.append(member.username)

        if member.username != 'gitlab_ldap_sync' and member.username not in target_users:
            member.delete()
            print("Deleted {} from {}".format(member.username, group.name))

    for user in target_users:
        if user not in existing_usernames:
            user_search = gitlab.users.list(username=user)
            if len(user_search) != 1:
                raise Exception("Gitlab user {} not found".format(user))
            group.members.create({
                'user_id': user_search[0].id,
                'access_level': DEVELOPER_ACCESS
            })
            print("Added {} to {}".format(user, group.name))


def sync_group_membership(gitlab, users_by_group):
    for group_name in users_by_group.keys():
        gitlab_groups = gitlab.groups.list(search=group_name)
        for group in gitlab_groups:
            if group.path == group_name:
                set_group_members(gitlab, group, users_by_group[group_name])
                break
        else:
            raise Exception("Invalid group name: {} (not found)".format(group_name))


def reverse_dict(d):
    d2 = {}
    for key in d.keys():
        for val in d[key]:
            if val not in d2.keys():
                d2[val] = []
            d2[val].append(key)
    return d2


def main():
    # Get configuration
    config = Config((
        ConfigOption('LDAP_URL', '--ldap-host'),
        ConfigOption('LDAP_DN', '--ldap-dn'),
        ConfigOption('LDAP_PASSWORD', '--ldap-password'),

        ConfigOption('LDAP_USERS', '--ldap-users'),
        ConfigOption('LDAP_GROUPS', '--ldap-groups'),
        ConfigOption('LDAP_USER_FILTER', '--ldap-user-filter'),

        ConfigOption('GITLAB_URL', '--gitlab-url'),
        ConfigOption('GITLAB_TOKEN', '--gitlab-token'),
        ConfigOption('GITLAB_PARENT', '--gitlab-parent')
    )).get()

    # Initialize Gitlab and LDAP objects
    directory = Directory(config['LDAP_URL'], config['LDAP_DN'], config['LDAP_PASSWORD'])
    gitlab = Gitlab(config['GITLAB_URL'], private_token=config['GITLAB_TOKEN'])

    users_by_group = {}

    # Create missing groups

    ldap_groups = directory.get_groups(config['LDAP_GROUPS'])
    for dn, attrs in ldap_groups:
        group_name = attrs['cn'][0].decode()
        if group_name.startswith('gitlab-') and group_name != 'gitlab-users':
            create_group_if_missing(gitlab, dn, attrs, config['GITLAB_PARENT'])

            users_by_group[group_name] = directory.get_member_uids(config['LDAP_USERS'], dn)

    # Create missing users
    ldap_users = directory.get_users(config['LDAP_USERS'], config['LDAP_USER_FILTER'])
    for dn, attrs in ldap_users:
        uid = attrs['uid'][0].decode()
        gitlab_user = gitlab.users.list(username=uid)
        if not gitlab_user:
            create_user(gitlab, dn, attrs)

    sync_group_membership(gitlab, users_by_group)


if __name__ == '__main__':
    main()
