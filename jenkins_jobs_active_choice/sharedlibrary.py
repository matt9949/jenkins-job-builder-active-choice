# Copyright 2016 Bulat Gaifullin
#
# This file is part of jenkins-job-builder-active-choice
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import xml.etree.ElementTree as Xml
import jenkins_jobs.modules.base
import json

class SharedLibrary(jenkins_jobs.modules.base.Base):

    REQUIRED_LIBRARY_CONFIGURATION = [
        # (yaml tag)
        ('name', 'name'),
        ('defaultVersion', 'defaultVersion')
    ]

    REQUIRED_USERREMOTECONFIG_CONFIGURATION = [
        # (yaml tag)
        ('repositoryUrl', 'url'),
        ('credentialsId', 'credentialsId')
    ]

    REQUIRED_BRANCHES_CONFIGURATION = [
        ('branchSpecifier', 'name')
    ]

    OPTIONAL_LIBRARY_CONFIGURATION = [
        # ( yaml tag, xml tag, default value )
        ('loadImplicitly', 'implicit', 'true'),
        ('allowDefaultVersionOverride', 'allowVersionOverride', 'true'),
        ('includeInChangesets', 'includeInChangesets', 'false')
    ]


    def _to_str(self, x):
        if not isinstance(x, str):
            return str(x).lower()
        return x


    def _add_element(self, xml_parent, tag, value):
        Xml.SubElement(xml_parent, tag).text = self._to_str(value)


    def _add_script(self, xml_parent, tag, value):
        if type(value) is list:
            script_str = ''.join(value)
        else:
            script_str = value
        # section = Xml.SubElement(xml_parent, tag)
        Xml.SubElement(xml_parent, "script").text = script_str


    def _unique_string(self, project, name):
        return 'sharedlibrary-{0}-{1}'.format(project, name).lower()

    def gen_xml(self, xml_parent, data):
        print("data is:" + json.dumps(data))

        sharedlibrary = data.get('sharedlibrary', [])

        if sharedlibrary:
            element_name = 'org.jenkinsci.plugins.workflow.libs.FolderLibraries'
            section = Xml.SubElement(xml_parent, element_name,
                                     {'plugin': 'workflow-cps-global-lib@2.12'})
            libraries = Xml.SubElement(section, 'libraries')
            library_configuration = Xml.SubElement(libraries, 'org.jenkinsci.plugins.workflow.libs.LibraryConfiguration')

            for name, tag in self.REQUIRED_LIBRARY_CONFIGURATION:
                try:
                    print("Found argument: " + name + ",  value: " + tag)
                    print("sharedlibrary is:" + json.dumps(sharedlibrary))
                    self._add_element(library_configuration, tag, sharedlibrary[name])
                except KeyError:
                    raise Exception("missing mandatory argument %s" % name)

            for name, tag, default in self.OPTIONAL_LIBRARY_CONFIGURATION:
                self._add_element(library_configuration, tag, sharedlibrary.get(name, default))


            retriever = Xml.SubElement(library_configuration, 'retriever',
                                       {'class': 'org.jenkinsci.plugins.workflow.libs.SCMRetriever'})
            scm = Xml.SubElement(retriever, 'scm',
                                 {'class': 'hudson.plugins.git.GitSCM',
                                  'plugin': 'git@3.9.1'})
            user_remote_configs = Xml.SubElement(scm, 'userRemoteConfigs')
            user_remote_config = Xml.SubElement(user_remote_configs, 'hudson.plugins.git.UserRemoteConfig')

            for name, tag in self.REQUIRED_USERREMOTECONFIG_CONFIGURATION:
                try:
                    self._add_element(user_remote_config, tag, sharedlibrary[name])
                except KeyError:
                    raise Exception("missing mandatory argument %s" % name)


            branches = Xml.SubElement(scm, 'branches')
            branch_spec = Xml.SubElement(branches, 'hudson.plugins.git.BranchSpec')

            for name, tag in self.REQUIRED_BRANCHES_CONFIGURATION:
                try:
                    self._add_element(branch_spec, tag, sharedlibrary[name])
                except KeyError:
                    raise Exception("missing mandatory argument %s" % name)

            self._add_element(scm, 'doGenerateSubmoduleConfigurations', 'false')