from infralint import Infralint
environment = 'production'
environments_root = '/etc/puppet/environments'
repo_root = 'path/to/puppet-modules'

inf = Infralint(host='puppetdb.example.net',
                env_root=environments_root,
                repo_root=repo_root,
                hiera_root="{rr}/extdata".format(rr=repo_root))

used_files, garbage = inf.manifest_use('production')

unused_hiera_data = inf.hiera_use()

print "There are {t} total manifests.".format(t=len(inf.manifests))
print "You have {u} used manifests.".format(u=len(used_files))
print "You have {nu} unused files.".format(nu=len(garbage))
print "You have {hd} unused hiera keys.".format(hd=len(unused_hiera_data))
