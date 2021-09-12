# Authors:
#   Unai Martinez-Corral
#
# Copyright 2021 Unai Martinez-Corral <unai.martinezcorral@ehu.eus>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

require 'asciidoctor/extensions' unless RUBY_ENGINE == 'opal'

include Asciidoctor

# An inline macro that shows a shield corresponding to the size of a tag available in a
# repository from DockerHub.
#
# Usage
#
#   OCIImage:repo_name[tag]
#
Extensions.register do
  inline_macro do
    named :OCIImage
    name_positional_attributes 'tag'
    process do |parent, target, attrs|
      tag = attrs['tag'] || 'latest'
      _arr = target.sub('/',':').gsub('/','--').split(':')
      dtarget = _arr[0]
      dtag = _arr[1] || 'latest'
      ctag = (tag != 'latest') ? ":#{tag}" : ''
      rcollection = (['pkg', 'build'].include? dtarget) ? 'debian/bullseye/' : ''
      text = %(image:https://img.shields.io/docker/image-size/hdlc/#{dtarget}/#{dtag}?longCache=true&style=flat-square&label=#{target}#{ctag}&logo=Docker&logoColor=fff[title='#{target}#{ctag} container image size'])
      (create_anchor parent, text, type: :link, target: %(https://gcr.io/hdl-containers/#{rcollection}#{target})).render
    end
  end
end
