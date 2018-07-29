from config import Config, ConfigOption
from directory import Directory


def main():
    config = Config((
        ConfigOption('LDAP_URL', '--ldap-host'),
        ConfigOption('LDAP_DN', '--ldap-dn'),
        ConfigOption('LDAP_PASSWORD', '--ldap-password'),

        ConfigOption('LDAP_USERS', '--ldap-users'),
        ConfigOption('LDAP_GROUPS', '--ldap-groups'),
        ConfigOption('LDAP_USER_FILTER', '--ldap-user-filter')
    )).get()

    directory = Directory(config['LDAP_URL'], config['LDAP_DN'], config['LDAP_PASSWORD'])
    ldap_users = directory.get_users(config['LDAP_USERS'], config['LDAP_USER_FILTER'])
    print(ldap_users)
    for user in ldap_users:
        print("User: {}, groups: {}".format(user[0], ' '.join([x.decode() for x in user[1]['memberOf']])))
    #print(directory.get_groups(config['LDAP_GROUPS']))


if __name__ == '__main__':
    main()