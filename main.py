from config import Config, ConfigOption


def main():
    config = Config((
        ConfigOption('LDAP_DN', '--ldap-dn'),
        ConfigOption('LDAP_PASSWORD', '--ldap-password'),
    )).get()


if __name__ == '__main__':
    main()