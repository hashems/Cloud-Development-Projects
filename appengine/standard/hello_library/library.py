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
import json


class Book(ndb.Model):
    id = ndb.StringProperty()
    title = ndb.StringProperty(required = True)
    author = ndb.StringProperty()
    isbn = ndb.StringProperty(required = True)
    genre = ndb.StringProperty(repeated = True)
    checkedIn = ndb.BooleanProperty()


class Customer(ndb.Model):
    id = ndb.StringProperty()
    name = ndb.StringProperty(required = True)
    balance = ndb.FloatProperty()
    checked_out = ndb.StringProperty(repeated = True)


class AllBooksHandler(webapp2.RequestHandler):
    # Create new Book
    # POST /books
    def post(self):
        book_data = json.loads(self.request.body)

        new_book = Book(
            title = book_data['title'],
            author = book_data['author'],
            isbn = book_data['isbn'],
            genre = book_data['genre'],
            checkedIn = book_data['checkedIn']
        )
        new_book.put()
        new_book.id = new_book.key.urlsafe()

        book_dict = new_book.to_dict()
        book_dict['self'] = '/books/' + new_book.id

        self.response.set_status(201)
        self.response.write(str(json.dumps(book_dict)))

    # Get all Books
    # GET /books
    # Get all Books by status
    # GET /books?checkedIn=:boolean
    def get(self):
        books = []
        # Get all Books by status
        if self.request.query_string:
            query = []
            bool = self.request.GET['checkedIn']
            book_query = Book.query()
            all_books = book_query.fetch()

            for book in all_books:
                book.id = book.key.urlsafe()
                book_dict = book.to_dict()
                book_dict['self'] = '/books/' + book.id
                books.append(book_dict)

            for book_obj in books:
                if bool == 'True' or bool == 'true':
                    if book_obj['checkedIn']:
                        query.append(book_obj)

                elif bool == 'False' or bool == 'false':
                    if not book_obj['checkedIn']:
                        query.append(book_obj)

            self.response.write(json.dumps(query))

        # Get all Books
        else:
            book_query = Book.query()
            all_books = book_query.fetch()

            for book in all_books:
                book.id = book.key.urlsafe()
                book_dict = book.to_dict()
                book_dict['self'] = '/books/' + book.id
                books.append(json.dumps(book_dict))

            self.response.write(json.dumps(books))

    # Delete all Books
    # DELETE /books
    def delete(self):
        book_query = Book.query()
        all_books = book_query.fetch()
        customer_query = Customer.query()
        all_customers = customer_query.fetch()

        for book in all_books:
            book.id = book.key.urlsafe()
            book_dict = book.to_dict()
            book_dict['self'] = '/books/' + book.id

            # Update Customer checked out lists
            for customer in all_customers:
                customer.id = customer.key.urlsafe()

                if book_dict['self'] in customer.checked_out:
                    customer.checked_out.remove(book_dict['self'])
                    customer.put()

            book.key.delete()


class BookHandler(webapp2.RequestHandler):
    # Replace Book
    # PUT /books/:book_id
    def put(self, id = None):
        if id:
            book = ndb.Key(urlsafe = id).get()
            book.id = id

            book_data = json.loads(self.request.body)

            book.title = book_data['title']
            book.author = book_data['author']
            book.isbn = book_data['isbn']
            book.genre = book_data['genre']

            # Update Customer checked_out list if status is checked in
            if book_data['checkedIn'] == True:
                customer_query = Customer.query()
                all_customers = customer_query.fetch()

                book_dict = book.to_dict()
                book_dict['self'] = '/books/' + book.id

                for customer in all_customers:
                    # Reset Book status for current list
                    if book_dict['self'] in customer.checked_out:
                        customer.checked_out.remove(book_dict['self'])
                        customer.put()

                book.checkedIn = book_data['checkedIn']

            book.put()

            book_dict = book.to_dict()
            book_dict['self'] = '/books/' + book.id

            self.response.write(json.dumps(book_dict))

    # Update Book by id
    # PATCH /books/:book_id
    def patch(self, id = None):
        if id:
            book = ndb.Key(urlsafe = id).get()
            book.id = id
            book.put()

            book_data = json.loads(self.request.body)

            if book_data.get('title'):
                book.title = book_data['title']

            if book_data.get('author'):
                book.author = book_data['author']

            if book_data.get('isbn'):
                book.isbn = book_data['isbn']

            if book_data.get('genre'):
                book.genre = book_data['genre']

            if book_data.get('checkedIn'):
                # Update Customer checked_out list if status is checked in
                if book_data.get('checkedIn') == True:
                    customer_query = Customer.query()
                    all_customers = customer_query.fetch()

                    book_dict = book.to_dict()
                    book_dict['self'] = '/books/' + book.id

                    for customer in all_customers:
                        # Reset Book status for current list
                        if book_dict['self'] in customer.checked_out:
                            customer.checked_out.remove(book_dict['self'])
                            customer.put()

                book.checkedIn = book_data['checkedIn']

            book.put()
            book_dict = book.to_dict()
            book_dict['self'] = '/books/' + book.id

            self.response.write(json.dumps(book_dict))

    # Get Book by id
    # GET /books/:book_id
    def get(self, id = None):
        if id:
            book = ndb.Key(urlsafe = id).get()
            book.id = id
            book.put()

            book_dict = book.to_dict()
            book_dict['self'] = '/books/' + id
            self.response.write(json.dumps(book_dict))

    # Delete Book by id
    # DELETE /books/:book_id
    def delete(self, id = None):
        if id:
            book = ndb.Key(urlsafe = id).get()
            book.key.delete()


class AllCustomersHandler(webapp2.RequestHandler):
    # Create new Customer
    # POST /customers
    def post(self):
        customer_data = json.loads(self.request.body)

        new_customer = Customer(
            name = customer_data['name'],
            balance = customer_data['balance'],
            checked_out = customer_data['checked_out']
        )
        new_customer.put()
        new_customer.id = new_customer.key.urlsafe()

        customer_dict = new_customer.to_dict()
        customer_dict['self'] = '/customers/' + new_customer.id

        self.response.set_status(201)
        self.response.write(json.dumps(customer_dict))

    # Get all Customers
    # GET /customers
    def get(self):
        customers = []
        customer_query = Customer.query()
        all_customers = customer_query.fetch()

        for customer in all_customers:
            customer.id = customer.key.urlsafe()
            customer_dict = customer.to_dict()
            customer_dict['self'] = '/customers/' + customer.id
            customers.append(customer_dict)

        self.response.write(customers)

    # Delete all Customers
    # DELETE /customers
    def delete(self):
        customer_query = Customer.query()
        all_customers = customer_query.fetch()
        book_query = Book.query()
        all_books = book_query.fetch()

        for customer in all_customers:
            # Update Book status
            for book in all_books:
                book.id = book.key.urlsafe()
                book_dict = book.to_dict()
                book_dict['self'] = '/books/' + book.id

                if book_dict['self'] in customer.checked_out:
                    book.checkedIn = True
                    book.put()

            customer.key.delete()


class CustomerHandler(webapp2.RequestHandler):
    # Replace Customer
    # PUT /customers/:customer_id
    def put(self, id = None):
        if id:
            customer = ndb.Key(urlsafe = id).get()
            customer.id = id

            customer_data = json.loads(self.request.body)

            customer.name = customer_data['name']
            customer.balance = customer_data['balance']
            customer.checked_out = customer_data['checked_out']
            customer.put()

            # Update Book status
            # Update Book status
            book_query = Book.query()
            all_books = book_query.fetch()
            for book in all_books:
                book.id = book.key.urlsafe()
                book_dict = book.to_dict()
                book_dict['self'] = '/books/' + book.id

                if book_dict['self'] in customer.checked_out:
                    book.checkedIn = False
                    book.put()

            customer_dict = customer.to_dict()
            customer_dict['self'] = '/customers/' + customer.id

            self.response.write(json.dumps(customer_dict))

    # Update Customer by id
    # PATCH /customers/:customer_id
    def patch(self, id = None):
        if id:
            customer = ndb.Key(urlsafe = id).get()
            customer.id = id
            customer.put()

            customer_data = json.loads(self.request.body)

            if customer_data.get('name'):
                customer.name = customer_data['name']

            if customer_data.get('balance'):
                customer.balance = customer_data['balance']

            if customer_data.get('checked_out'):
                # Update Book status
                book_query = Book.query()
                all_books = book_query.fetch()
                for book in all_books:
                    book.id = book.key.urlsafe()
                    book_dict = book.to_dict()
                    book_dict['self'] = '/books/' + book.id

                    # Reset Book status for current list
                    if book_dict['self'] in customer.checked_out:
                        book.checkedIn = True
                        book.put()

                    # Set Book status for updated list
                    if book_dict['self'] in customer_data.get('checked_out'):
                        book.checkedIn = False
                        book.put()

                customer.checked_out = customer_data['checked_out']

            customer.put()
            customer_dict = customer.to_dict()
            customer_dict['self'] = '/customers/' + customer.id

            self.response.write(json.dumps(customer_dict))

    # Get Customer by id
    # GET /customers/:customer_id
    def get(self, id = None):
        if id:
            customer = ndb.Key(urlsafe = id).get()
            customer.id = id
            customer.put()

            customer_dict = customer.to_dict()
            customer_dict['self'] = '/customers/' + id
            self.response.write(json.dumps(customer_dict))

    # Delete Customer by id
    # DELETE /customers/:customer_id
    def delete(self, id = None):
        if id:
            customer = ndb.Key(urlsafe = id).get()
            customer.key.delete()


class CheckOutHandler(webapp2.RequestHandler):
    # Check out a Book to a Customer
    # PUT /customers/:customer_id/books/:book_id
    def put(self, customer_id = None, book_id = None):
        if customer_id and book_id:
            customer = ndb.Key(urlsafe = customer_id).get()
            book = ndb.Key(urlsafe = book_id).get()

            # Update Book's checked in status
            book.checkedIn = False
            book.put()
            book_dict = book.to_dict()
            book_dict['self'] = '/books/' + book_id

            # Update Customer's checked out list
            customer.checked_out.append(book_dict['self'])
            customer.id = customer_id
            customer.put()

            customer_dict = customer.to_dict()
            customer_dict['self'] = '/customers/' + customer_id
            self.response.set_status(201)
            self.response.write(str(json.dumps(customer_dict)))

    # Get checked out Book by id
    # GET /customers/:customer_id/books/:book_id
    def get(self, customer_id = None, book_id = None):
        if customer_id and book_id:
            customer = ndb.Key(urlsafe = customer_id).get()
            book = ndb.Key(urlsafe = book_id).get()
            customer.id = customer_id
            book.id = book_id
            customer.put()
            book.put()

            book_dict = book.to_dict()
            book_dict['self'] = '/books/' + book.id

            if book_dict['self'] in customer.checked_out:
                self.response.write(str(json.dumps(book_dict)))

    # Check in a Book from a Customer
    # DELETE /customers/:customer_id/books/:book_id
    def delete(self, customer_id = None, book_id = None):
        if customer_id and book_id:
            customer = ndb.Key(urlsafe = customer_id).get()
            book = ndb.Key(urlsafe = book_id).get()

            # Update Book's checked in status
            book.checkedIn = True
            book.put()
            book_dict = book.to_dict()
            book_dict['self'] = '/books/' + book_id

            # Update Customer's checked out list
            customer.checked_out.remove(book_dict['self'])
            customer.id = customer_id
            customer.put()

            customer_dict = customer.to_dict()
            customer_dict['self'] = '/customers/' + customer_id
            self.response.write(json.dumps(customer_dict))


class CustomerAllBooksHandler(webapp2.RequestHandler):
    # Get Customer's checked out Books
    # GET /customers/:customer_id/books
    def get(self, id = None):
        if id:
            customer = ndb.Key(urlsafe = id).get()
            customer.id = id
            customer.put()

            customer_dict = customer.to_dict()
            customer_dict['self'] = '/customers/' + id
            self.response.write(json.dumps(customer_dict['checked_out']))


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello, Library! It\'s me, REST Implementation!')

    def delete(self):
        book_query = Book.query()
        all_books = book_query.fetch()
        for book in all_books:
            book.key.delete()

        customer_query = Customer.query()
        all_customers = customer_query.fetch()
        for customer in all_customers:
            customer.key.delete()


allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/books', AllBooksHandler),
    ('/books?checkedIn=(.*)', AllBooksHandler),
    ('/books/([a-zA-Z0-9\_\-]+)', BookHandler),
    ('/customers', AllCustomersHandler),
    ('/customers/([a-zA-Z0-9\_\-]+)', CustomerHandler),
    # ('/customers/([a-zA-Z0-9\_\-]+)/books', CheckOutHandler),
    ('/customers/([a-zA-Z0-9\_\-]+)/books/([a-zA-Z0-9\_\-]+)', CheckOutHandler),
    ('/customers/([a-zA-Z0-9\_\-]+)/books', CustomerAllBooksHandler)
], debug=True)
