# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


"""
The Parameters module allows you to specify build parameters for a job.
**Component**: parameters
  :Macro: parameter
  :Entry Point: jenkins_jobs.parameters
Example::
  job:
    name: test_job
    parameters:
      - string:
          name: FOO
          default: bar
          description: "A parameter named FOO, defaults to 'bar'."
"""

import xml.etree.ElementTree as XML

from jenkins_jobs.errors import JenkinsJobsException
from jenkins_jobs.errors import MissingAttributeError
from jenkins_jobs.errors import InvalidAttributeError
import jenkins_jobs.modules.base
import jenkins_jobs.modules.helpers as helpers

class SharedLibrary(jenkins_jobs.modules.base.Base):
    sequence = 21

    component_type = 'sharedlibrary'
    component_list_type = 'sharedlibrary'

    def gen_xml(self, xml_parent, data):
        properties = xml_parent.find('properties')
        if properties is None:
            properties = XML.SubElement(xml_parent, 'properties')

        sharedlibrary = data.get('sharedlibrary', [])
        hmodel = 'hudson.model.'
        if sharedlibrary:
            # The conditionals here are to work around the extended_choice
            # parameter also being definable in the properties module.  This
            # usage has been deprecated but not removed.  Because it may have
            # added these elements before us, we need to check if they already
            # exist, and only add them if they're missing.
            sdefs = properties.find(hmodel + 'SharedLibraryDefinitionProperty')
            if sdefs is None:
                sdefs = XML.SubElement(properties,
                                       hmodel + 'SharedLibraryDefinitionProperty')
            sdefs = pdefp.find('sharedLibraryDefinitions')
            if sdefs is None:
                sdefs = XML.SubElement(sdefs, 'sharedLibraryDefinitions')
            for param in sharedlibrary:
                self.registry.dispatch('sharedlibrary', sdefs, param)