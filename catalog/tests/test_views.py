import datetime
import uuid

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User, Permission # Required to assign User as a borrower, and grant permission to set book as returned

from catalog.models import Author, BookInstance, Book, Genre, Language

class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 13 authors for pagination test
        number_of_authors = 13

        for author_id in range(number_of_authors):
            Author.objects.create(
                first_name=f'Christian {author_id}',
                last_name=f'Surname {author_id}',
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['author_list']) == 10)

    def test_lists_all_authors(self):
        response = self.client.get(reverse('authors')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['author_list']) == 3)

class LoanedBookInstancesByUserListViewTest(TestCase):
    def setUp(self):
        # Create two users
        # setUp used instead of setUpTestData because the objects will be modified later
        test_user1 = User.objects.create_user(username='testuser1', password='1X<IIbnibusdg')
        test_user2 = User.objects.create_user(username='testuser2', password='18DFH5jhkeHO!')

        test_user1.save()
        test_user2.save()

        # Create a Book
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary.',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )

        # Create Genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book) # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create 30 BookInstance objects
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.localtime() + datetime.timedelta(days=book_copy%5)
            the_borrower = test_user1 if book_copy % 2 else test_user2
            status = 'm'
            BookInstance.objects.create(
                book=test_book,
                imprint='Unlikely Imprint, 2016',
                due_back=return_date,
                borrower=the_borrower,
                status=status,
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<IIbnibusdg')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success
        self.assertEqual(response.status_code, 200) # status code 200 indicates success

        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/bookinstance_list_borrowed_user.html')

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username='testuser1', password='1X<IIbnibusdg')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success
        self.assertEqual(response.status_code, 200) # status code 200 indicates success

        # Check that we initially don't have any books in the list (none on loan)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 0)

        # Now change all books to be on loan
        books = BookInstance.objects.all()[:10]

        for book in books:
            book.status = 'o'
            book.save()

        # Check that we now have borrowed books in the list
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success
        self.assertEqual(response.status_code, 200) # status code 200 indicates success

        self.assertTrue('bookinstance_list' in response.context)
        # Confirm all books belong to testuser1 and are on loan
        for bookitem in response.context['bookinstance_list']:
            self.assertEqual(response.context['user'], bookitem.borrower)
            self.assertEqual('o', bookitem.status)

    def test_pages_ordered_by_due_date(self):
        # Change all books to be on loan
        for book in BookInstance.objects.all():
            book.status = 'o'
            book.save()

        login = self.client.login(username='testuser1', password='1X<IIbnibusdg')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success
        self.assertEqual(response.status_code, 200) # status code 200 indicates success      

        # Confirm that of the items, only 10 are displayed due to pagination
        self.assertEqual(len(response.context['bookinstance_list']), 10)

        last_date = 0
        for book in response.context['bookinstance_list']:
            if last_date == 0:
                last_date = book.due_back
            else:
                self.assertTrue(last_date <= book.due_back)
                last_date = book.due_back


class RenewBookInstancesViewTest(TestCase):
    def setUp(self):
        # Create two users
        # setUp used instead of setUpTestData because the objects will be modified later
        test_user1 = User.objects.create_user(username='testuser1', password='1X<IIbnibusdg')
        test_user2 = User.objects.create_user(username='testuser2', password='18DFH5jhkeHO!')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create a Book
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary.',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )

        # Create Genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book) # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create a BookInstance object for test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            borrower=test_user1,
            status='o',
        )

        # Create a BookInstance object for test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            borrower=test_user2,
            status='o',
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        # Manually check redirect (can't use assertRedirects, because the redirect URL is unpredictable).
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_redirect_if_logged_in_but_not_correct_permissions(self):
        login = self.client.login(username='testuser1', password='1X<IIbnibusdg')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        # This redirects to a new login page, with a message saying to log in with an account with permissions
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username='testuser2', password='18DFH5jhkeHO!')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance2.pk}))

        # Check that it lets us log in - this is our book and we have the right permissions.
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(username='testuser2', password='18DFH5jhkeHO!')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))

        # Check that it lets us log in. We're a librarian, so we can view any users book
        self.assertEqual(response.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        # Unlikely UID to match our bookInstance!
        test_uid = uuid.uuid4()
        login = self.client.login(username='testuser2', password='18DFH5jhkeHO!')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': test_uid}))
        self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='18DFH5jhkeHO!')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 200) # status code 200 indicates success

        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/book_renew_librarian.html')

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username='testuser2', password='18DFH5jhkeHO!')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 200) # status code 200 indicates success

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(response.context['form'].initial['renewal_date'], date_3_weeks_in_future)

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        login = self.client.login(username='testuser2', password='18DFH5jhkeHO!')
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        # POST data using the client
        response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}), {'renewal_date': valid_date_in_future})
        self.assertRedirects(response, reverse('all-borrowed'))

    def test_form_invalid_renewal_date_past(self):
        login = self.client.login(username='testuser2', password='18DFH5jhkeHO!')
        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
        # POST data using the client
        response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}), {'renewal_date': date_in_past})
        self.assertEqual(response.status_code, 200)
        # User assertFormError to verify that the error messages are as expected
        self.assertFormError(response, 'form', 'renewal_date', 'Invalid date - renewal in past')

    def test_form_invalid_renewal_date_future(self):
        login = self.client.login(username='testuser2', password='18DFH5jhkeHO!')
        invalid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)
        # POST data using the client
        response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}), {'renewal_date': invalid_date_in_future})
        self.assertEqual(response.status_code, 200)
        # User assertFormError to verify that the error messages are as expected
        self.assertFormError(response, 'form', 'renewal_date', 'Invalid date - renewal more than 4 weeks ahead')


# Challenge yourself, part 10

class AuthorCreateViewTest(TestCase):
    def setUp(self):
        # Create two users, one with permission and one without
        # setUp used instead of setUpTestData because the objects will be modified later
        test_user1 = User.objects.create_user(username='testuser1', password='1X<IIbnibusdg')
        test_user2 = User.objects.create_user(username='testuser2', password='18DFH5jhkeHO!')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Add, edit, delete Author records')
        test_user2.user_permissions.add(permission)
        test_user2.save()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('author_create'))
        # Manually check redirect (can't use assertRedirects, because the redirect URL is unpredictable).
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_redirect_if_logged_in_but_not_correct_permissions(self):
        login = self.client.login(username='testuser1', password='1X<IIbnibusdg')
        response = self.client.get(reverse('author_create'))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission(self):
        login = self.client.login(username='testuser2', password='18DFH5jhkeHO!')
        response = self.client.get(reverse('author_create'))
        # Check that it lets us log in - this is our book and we have the right permissions.
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='18DFH5jhkeHO!')
        response = self.client.get(reverse('author_create'))
        self.assertEqual(response.status_code, 200) # status code 200 indicates success
        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/author_form.html')

    def test_redirects_to_all_author_list_on_success(self):
        login = self.client.login(username='testuser2', password='18DFH5jhkeHO!')
        first_name = "First"
        last_name = "Last"
        date_of_birth = datetime.date.today() - datetime.timedelta(days=100*365)
        date_of_death = datetime.date.today() - datetime.timedelta(days=10*365)
        # POST data using the client
        response = self.client.post(reverse('author_create'), {
            'first_name': first_name,
            'last_name': last_name,
            'date_of_birth': date_of_birth,
            'date_of_death': date_of_death,
        })
        self.assertRedirects(response, reverse('author-detail', kwargs={'pk': 1})) # pk is 1 because this is the first author created

    def test_initial_values(self):
        login = self.client.login(username='testuser2', password='18DFH5jhkeHO!')
        response = self.client.get(reverse('author_create'))
        self.assertEqual(response.status_code, 200) # status code 200 indicates success

        initial_date_of_death = '05/01/2018'
        self.assertEqual(response.context['form'].initial['date_of_death'], initial_date_of_death)