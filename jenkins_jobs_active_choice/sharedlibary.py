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


# - active-choice:
#   name: CASCADE_CHOICE
#   script: |
#     return ['foo:selected', 'bar']
#   description: "A parameter named CASCADE_CHOICE which options foo and bar."
#   displayExpression: value  [OPTIONAL]
#   sandbox: false            [OPTIONAL]


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


def _to_str(x):
    if not isinstance(x, str):
        return str(x).lower()
    return x


def _add_element(xml_parent, tag, value):
    Xml.SubElement(xml_parent, tag).text = _to_str(value)


def _add_script(xml_parent, tag, value):
    if type(value) is list:
        script_str = ''.join(value)
    else:
        script_str = value
    # section = Xml.SubElement(xml_parent, tag)
    Xml.SubElement(xml_parent, "script").text = script_str


def _unique_string(project, name):
    return 'pipelinejob_sharedlibrary-{0}-{1}'.format(project, name).lower()


def sharedlibrary_parameter(parser, xml_parent, data):
    """yaml: cascade-choice
    Creates an active choice parameter
    Requires the Jenkins :jenkins-wiki:`Active Choices Plugin <Active+Choices+Plugin>`.

    :arg str name: the name of the parameter
    :arg str script: the groovy script which generates choices
    :arg str description: a description of the parameter (optional)
    arg: int visible-item-count: a number of visible items
    arg: str fallback-script: a groovy script which will be evaluated if main script fails (optional)
    arg: str reference: the name of parameter on changing that the parameter will be re-evaluated
    arg: str choice-type: a choice type, can be on of single, multi, checkbox or radio
    arg: bool filterable: added text box to filter elements
    Example::

    .. code-block:: yaml

        - cascade-choice:
          name: CASCADE_CHOICE
          project: test_project
          script: |
            return ['foo', 'bar']
    """

    element_name = 'org.jenkinsci.plugins.workflow.libs.FolderLibraries'
    section = Xml.SubElement(xml_parent, element_name,
                             {'plugin': 'workflow-cps-global-lib@2.12'})
    libraries = Xml.SubElement(section, 'libraries')
    library_configuration = Xml.SubElement(libraries, 'org.jenkinsci.plugins.workflow.libs.LibraryConfiguration')

    for name, tag in REQUIRED_LIBRARY_CONFIGURATION:
        try:
            _add_element(library_configuration, tag, data[name])
        except KeyError:
            raise Exception("missing mandatory argument %s" % name)

    for name, tag, default in OPTIONAL_LIBRARY_CONFIGURATION:
        _add_element(library_configuration, tag, data.get(name, default))


    retriever = Xml.SubElement(library_configuration, 'org.jenkinsci.plugins.workflow.libs.LibraryConfiguration',
                               {'class': 'org.jenkinsci.plugins.workflow.libs.SCMRetriever'})
    scm = Xml.SubElement(retriever, 'org.jenkinsci.plugins.workflow.libs.LibraryConfiguration',
                         {'class': 'hudson.plugins.git.GitSCM',
                          'plugin': 'git@3.9.1'})
    user_remote_configs = Xml.SubElement(scm, 'userRemoteConfigs')
    user_remote_config = Xml.SubElement(user_remote_configs, 'hudson.plugins.git.UserRemoteConfig')

    for name, tag in REQUIRED_USERREMOTECONFIG_CONFIGURATION:
        try:
            _add_element(user_remote_config, tag, data[name])
        except KeyError:
            raise Exception("missing mandatory argument %s" % name)


    branches = Xml.SubElement(scm, 'branches')
    branch_spec = Xml.SubElement(branches, 'hudson.plugins.git.BranchSpec')

    for name, tag in REQUIRED_BRANCHES_CONFIGURATION:
        try:
            _add_element(branch_spec, tag, data[name])
        except KeyError:
            raise Exception("missing mandatory argument %s" % name)


    _add_element(scm, 'doGenerateSubmoduleConfigurations', 'false')