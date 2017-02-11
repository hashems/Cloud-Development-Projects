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

from google.appengine.ext import ndb
import webapp2
import logging
import json


# Client ID: 428964381623-i1q6ovvd8biljqklkfv7gktgrspra5m9.apps.googleusercontent.com
# Client secret: 5WkvUxxTp4aGrNUO-eSdyLHZ


class OauthHandler(webapp2.RequestHandler):
    def get(self):
        # DEBUG Print contents of request
        logging.debug('The contents of the GET request is: ' + repr(self.request.GET))


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello, World! It\'s me, OAuth 2.0!')


allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/oauth', OauthHandler)
], debug=True)
