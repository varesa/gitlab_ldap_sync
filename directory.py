import ldap


class Directory:

    def __init__(self, url, dn, password):
        self.url = url
        self.dn = dn
        self.password = password

        self.ldap = ldap.initialize(self.url)
        self.ldap.simple_bind_s(dn, password)

    def get_users(self, path, filter):
        return self.ldap.search_s(
            path, ldap.SCOPE_SUBTREE,
            filterstr=filter, attrlist=['memberOf', 'uid', 'displayName', 'mail']
        )

    def get_groups(self, path):
        groups = self.ldap.search_s(path, ldap.SCOPE_ONELEVEL, attrlist=['memberOf', 'cn'])
        return groups

    def get_member_uids(self, users_path, group):
        search_result = self.ldap.search_s(
            users_path, ldap.SCOPE_ONELEVEL,
            filterstr="memberOf={}".format(group), attrlist=['uid']
        )

        uids = []

        for dn, attrs in search_result:
            uids.append(attrs['uid'][0].decode())

        return uids
