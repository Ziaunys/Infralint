from sets import Set
from itertools import chain
import yaml
import os
import re
import requests

class Infralint(object):


    def __init__(self,
                 host='localhost',
                 env_root=os.getcwd(),
                 repo_root='/etc/puppet/environments',
                 hiera_root=None):
        self.host = host
        self.env_root = env_root
        self.repo_root = repo_root
        self.hiera_root = hiera_root
        self.manifests = self._manifest_files()
        self.hiera_files = self._hiera_files()

    def _manifest_files(self):

        puppet_files = Set()
        for root, dirs, files in os.walk(self.repo_root):
            for name in files:
                if re.match('^.*.pp$', name):
                    puppet_files.add(os.path.join(root.replace(self.repo_root, ''), name))
        return puppet_files

    def _hiera_files(self):
        hiera_files = Set()
        for root, dirs, files in os.walk(self.hiera_root):
            for name in files:
                if re.match('^.*.yaml$', name):
                    hiera_files.add(os.path.join(root, name))
        return hiera_files

    def _get_resources(self):

        r = requests.get('http://{h}/v3/resources'.format(h=self.host), data='limit=9000')
        return r.json()

    def _get_used_files(self, manifest_path, resources):

        file_set = Set()
        for r in resources:
            if( r['file']
                and not re.match("^{ep}/modules.*$".format(ep=manifest_path),
                    r['file'])
                and re.match("^{ep}.*$".format(ep=manifest_path), r['file'])):

                file_set.add(r['file'].replace(manifest_path, ''))
        return file_set

    def _diff_files(self, used_files):

        return self.manifests.difference(used_files)

    def _hiera_keys(self):

        hiera_data = []
        hiera_keys = Set()

        for hiera_file in self.hiera_files:
            with open(hiera_file) as f:
                hiera_data.append(yaml.load(f))
        for d in hiera_data:
            if d:
                [ hiera_keys.add(k) for k in d.keys()]
        return hiera_keys

    def _hiera_lookups(self):
        hiera_lookups = Set()
        for manifest_file in self.manifests:
            with open(self.repo_root + '/' + manifest_file) as f:
                for line in f:
                    g = re.match(".*hiera\('(.*)',.*$", line)
                    if g:
                        hiera_lookups.add(g.group(1))
        return hiera_lookups

    def hiera_use(self):

        hiera_keys = self._hiera_keys()
        hiera_lookups = self._hiera_lookups()
        return hiera_keys.difference(hiera_lookups)


    def manifest_use(self, environment):

        manifest_path = "{er}/{e}"
        resources = self._get_resources()
        used_files = self._get_used_files(
                        manifest_path.format(er=self.env_root, e=environment),
                        resources)
        unused_files = self._diff_files(used_files)
        return used_files, unused_files


