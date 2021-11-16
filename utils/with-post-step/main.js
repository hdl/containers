// Authors:
//   Unai Martinez-Corral
//
// Copyright 2021 Unai Martinez-Corral <unai.martinezcorral@ehu.eus>
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// SPDX-License-Identifier: Apache-2.0

// Context: https://github.com/docker/login-action/issues/72

const { exec } = require('child_process');

function run(cmd) {
  exec(cmd, (error, stdout, stderr) => {
    if ( stdout.length != 0 ) { console.log(`${stdout}`); }
    if ( stderr.length != 0 ) { console.error(`${stderr}`); }
    if (error) {
      console.error(`exec error: ${error}`);
    }
    return error;
  });
}

if ( process.env.STATE_POST != undefined ) { // Are we in the 'post' step?
  run(process.env.INPUT_POST);
} else { // Otherwise, this is the main step
  run(process.env.INPUT_MAIN);
  console.log(`::save-state name=POST::true`);
}
