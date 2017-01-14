# Copyright 2016 Google Inc.
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

import webapp2
# Import datetime library
import datetime


class MainPage(webapp2.RequestHandler):
    def get(self):
        # Create server side data output per assignment instructions
        # Create datetime object from system clock
        current = datetime.datetime.now()

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World! It\'s me, Python!\n\n')

    # Source cited: https://docs.python.org/2/library/datetime.html?highlight=datetime#strftime-and-strptime-behavior
        self.response.write('Today is ')
        self.response.write(current.strftime('%A, %B %d, %Y (in London).\n\n'))

        self.response.write('The time (in London) is ')
        self.response.write(current.strftime('%I:%M:%S %p.'))


app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
