from sets import Set
import os
import re
import requests

class Infralint(object):


    def __init__(self, host='localhost', env_root=os.getcwd(), repo_root='/etc/puppet/environments'):
        self.host = host
        self.env_root = env_root
        self.repo_root = repo_root
        self.files = self._get_files()

    def _get_files(self):

        puppet_files = Set()
        for root, dirs, files in os.walk(self.repo_root):
            for name in files:
                if re.match('^.*.pp$', name):
                    puppet_files.add(os.path.join(root.replace(self.repo_root, ''), name))
        return puppet_files

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

        return self.files.difference(used_files)

    def manifest_use(self, environment):

        manifest_path = "{er}/{e}"
        resources = self._get_resources()
        used_files = self._get_used_files(
                        manifest_path.format(er=self.env_root, e=environment),
                        resources)
        unused_files = self._diff_files(used_files)
        return used_files, unused_files
