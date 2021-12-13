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

build:
	docker run --rm \
	  -v /$(shell pwd)/..://documents/ \
	  hdlc/doc:asciidoctor-py \
	  make -C doc all

asciidoctor-py:
	docker build \
	  -t hdlc/doc:asciidoctor-py \
	  -f- ../ < doc--asciidoctor-py.dockerfile

pyHDLC:
	docker build \
	  -t hdlc/doc:pyHDLC \
	  -f- ../ < doc--pyHDLC.dockerfile

clean-img:
	if [ -d public/img ]; then rm -rf public/img; fi

all: clean-img main-html ug-html dev-html
	mkdir -p asciidoctor/public/img/
	cp -vr asciidoctor/img/* asciidoctor/public/img/

main-html:
	cd asciidoctor/main && \
	./gen_tool_table.py && \
	asciidoctor \
	  -r ../lib/OCIImage-inline-macro.rb \
	  -r ../lib/GHAStatus-inline-macro.rb \
	  -r asciidoctor-diagram \
	  index.adoc \
	  --out-file ../public/index.html

ug-html:
	cd asciidoctor/ug && \
	asciidoctor \
	  -r ../lib/OCIImage-inline-macro.rb \
	  -r ../lib/GHAStatus-inline-macro.rb \
	  -r asciidoctor-diagram \
	  index.adoc \
	  --out-file ../public/ug/index.html

dev-html:
	cd asciidoctor/dev && \
	asciidoctor \
	  -r ../lib/OCIImage-inline-macro.rb \
	  -r ../lib/GHAStatus-inline-macro.rb \
	  -r asciidoctor-diagram \
	  index.adoc \
	  --out-file ../public/dev/index.html

map:
	docker run --rm \
	  -v /$(shell pwd)/..://wrk/ \
	  -w //wrk/utils \
	  hdlc/doc:pyHDLC \
	  sh -c 'pip3 install -e .; python3 pyHDLC/map.py'
