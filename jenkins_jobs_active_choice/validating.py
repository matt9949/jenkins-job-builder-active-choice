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


# - validating:
#   name: CASCADE_CHOICE
#   regex:
#   description: "A parameter named CASCADE_CHOICE which options foo and bar."
#   displayExpression: value  [OPTIONAL]
#   sandbox: false            [OPTIONAL]


REQUIRED = [
    # (yaml tag)
    ('name', 'name'),
    ('regex', 'regex')
]

OPTIONAL = [
    # ( yaml tag, xml tag, default value )
    ('description', 'description', ''),
    ('defaultValue', 'defaultValue', ''),
    ('failedValidationMessage', 'failedValidationMessage', '')
]




def _to_str(x):
    if not isinstance(x, str):
        return str(x).lower()
    return x


def _add_element(xml_parent, tag, value):
    Xml.SubElement(xml_parent, tag).text = _to_str(value)


def validating_parameter(parser, xml_parent, data):
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


    # <hudson.plugins.validating__string__parameter.ValidatingStringParameterDefinition plugin="validating-string-paramete
    # r@2.3">
    # <name>suffix</name>
    # <description>Environment suffix</description>
    # <defaultValue></defaultValue>
    # <regex>[a-z]\w{2,9}</regex>
    # <failedValidationMessage>Example: feature1 (3-10 chars starting with a letter</failedValidationMessage>
    # </hudson.plugins.validating__string__parameter.ValidatingStringParameterDefinition>



    element_name = 'hudson.plugins.validating__string__parameter.ValidatingStringParameterDefinition'

    section = Xml.SubElement(xml_parent, element_name)

    for name, tag in REQUIRED:
        try:
            _add_element(section, tag, data[name])
        except KeyError:
            raise Exception("missing mandatory argument %s" % name)

    for name, tag, default in OPTIONAL:
        _add_element(section, tag, data.get(name, default))

