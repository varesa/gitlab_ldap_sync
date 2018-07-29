import ldap


class Directory:

    def __init__(self, url, dn, password):
        self.url = url
        self.dn = dn
        self.password = password

        self.ldap = ldap.initialize(self.url)
        self.ldap.simple_bind_s(dn, password)

    def get_users(self, path, filter):
        users = self.ldap.search_s(path, ldap.SCOPE_SUBTREE, filterstr=filter, attrlist=['memberOf'])
        return users

    def get_groups(self, path):
        groups = self.ldap.search_s(path, ldap.SCOPE_ONELEVEL, attrlist=['memberOf'])
        return groups
