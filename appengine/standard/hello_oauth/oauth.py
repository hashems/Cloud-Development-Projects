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

# CITE: CS 496 Week 4 Content (various)
# CITE: CS 496 Piazza Forums (various)
# CITE: https://developers.google.com/identity/protocols/OAuth2
# CITE: http://stackoverflow.com/questions/18319101/whats-the-best-way-to-generate-random-strings-of-a-specific-length-in-python

# CS 496 HW4 API OAuth 2.0 Credentials
# Client ID: 428964381623-i1q6ovvd8biljqklkfv7gktgrspra5m9.apps.googleusercontent.com
# Client secret: 5WkvUxxTp4aGrNUO-eSdyLHZ


from google.appengine.api import urlfetch
import urllib
import webapp2
import logging
import json
from random import choice
from string import ascii_uppercase


# Global list to store and verify randomized state variables
_STATE = []


class OauthHandler(webapp2.RequestHandler):
    def get(self):
        google_api_token_url = 'https://www.googleapis.com/oauth2/v4/token'

        # Get state and code variables from query string
        state = self.request.get('state')
        code = self.request.get('code')

        # Validate state variable
        if state not in _STATE:
            self.response.write('Invalid State Variable')

        elif state in _STATE:
            self.response.write('State Variable: ' + state + '<br>')

            # Set POST request header
            get_token_header = {'Content-Type': 'application/x-www-form-urlencoded'}

            # Set POST request body parameters
            client_id = '428964381623-i1q6ovvd8biljqklkfv7gktgrspra5m9.apps.googleusercontent.com'
            client_secret = '5WkvUxxTp4aGrNUO-eSdyLHZ'
            redirect_uri = 'https://cs-496-hw4-158022.appspot.com/oauth'
            grant_type = 'authorization_code'

            parameters = {
                'code': code,
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': redirect_uri,
                'grant_type': grant_type
            }

            # Send POST request
            try:
                token_result = urlfetch.fetch(
                    url=google_api_token_url,
                    payload=urllib.urlencode(parameters),
                    method=urlfetch.POST,
                    headers=get_token_header
                )

                if token_result.status_code == 200:
                    # Get access token from POST response
                    token_result = json.loads(token_result.content)
                    access_token = token_result['access_token']

                    # Set GET request header
                    get_googleplus_header = {'Authorization': 'Bearer ' + access_token}

                    # Set GET request parameters
                    googleplus_result = urlfetch.fetch(
                        url='https://www.googleapis.com/plus/v1/people/me',
                        method=urlfetch.GET,
                        headers=get_googleplus_header
                    )

                    # Get first name, last name, and url from GET response
                    googleplus_data = json.loads(googleplus_result.content)
                    first_name = googleplus_data['name']['givenName']
                    last_name = googleplus_data['name']['familyName']
                    url = googleplus_data['url']
                    email = googleplus_data['emails'][0]['value']
                    self.response.write('User\'s First and Last Name: ' + first_name + ' ' + last_name + '<br>')
                    self.response.write('User\'s Google Plus Account URL: ' + '<a target=_blank href="' + url + '">' + url + '</a>' + '<br>')
                    self.response.write('User\'s Email: ' + email)

            except urlfetch.Error as e:
                logging.exception('Caught exception fetching Google\'s OAuth 2.0 Token URL')
                logging.debug(e)


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello, World! It\'s me, OAuth 2.0!')

        # Set GET request headers
        response_type = 'code'
        client_id = '428964381623-i1q6ovvd8biljqklkfv7gktgrspra5m9.apps.googleusercontent.com'
        redirect_uri = 'https://cs-496-hw4-158022.appspot.com/oauth'
        scope = 'email'
        state = ''.join(choice(ascii_uppercase) for i in range(10))

        # Store state in global list for tracking and validation
        global _STATE
        _STATE.append(state)

        # Build GET request query string
        google_oauth_url = 'https://accounts.google.com/o/oauth2/v2/auth' + \
                           '?response_type=' + response_type + \
                           '&client_id=' + client_id + \
                           '&redirect_uri=' + redirect_uri + \
                           '&scope=' + scope + \
                           '&state=' + state

        # Send GET request
        try:
            result = urlfetch.fetch(google_oauth_url)
            if result.status_code == 200:
                self.response.write(result.content)
        except urlfetch.Error as e:
            logging.exception('Caught exception fetching Google\'s OAuth 2.0 URL')
            logging.debug(e)


allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/oauth', OauthHandler)
], debug=True)
