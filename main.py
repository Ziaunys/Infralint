from infralint import Infralint
environment = 'production'
environments_root = '/etc/puppet/environments'
repo_root = '/Users/ericzounes/Documents/werk/puppetlabs-modules'

inf = Infralint(host='puppetdb.example.com:8080',
                env_root=environments_root,
                repo_root=repo_root)

used_files, garbage = inf.manifest_use('production')

print "There are {t} total manifests.".format(t=len(inf.files))
print "You have {u} used manifests.".format(u=len(used_files))
print "You have {nu} unused files.".format(nu=len(garbage))
print garbage

