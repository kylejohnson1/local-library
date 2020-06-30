import datetime

from django.test import TestCase
from django.utils import timezone

from catalog.forms import RenewBookForm

# Because these tests do not use databse or test client, could consider changing this to use SimpleTestCase

class RenewBookFormTest(TestCase):
    def test_renew_form_date_field_label(self):
        # Tests that field's label is correct
        form = RenewBookForm()
        self.assertTrue(form.fields['renewal_date'].label == None or form.fields['renewal_date'] == 'renewal date')

    def test_renew_form_date_field_help_text(self):
        # Tests that field's help text is correct
        form = RenewBookForm()
        self.assertEqual(form.fields['renewal_date'].help_text, 'Enter a date between now and 4 weeks (default 3).')

    def test_renew_form_date_in_past(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form = RenewBookForm(data={'renewal_date': date})
        self.assertFalse(form.is_valid())

    def test_renew_form_date_too_far_in_future(self):
        date = datetime.date.today() + datetime.timedelta(weeks=4) + datetime.timedelta(days=1)
        form = RenewBookForm(data={'renewal_date': date})
        self.assertFalse(form.is_valid())

    def test_renew_form_date_today(self):
            date = datetime.date.today()
            form = RenewBookForm(data={'renewal_date': date})
            self.assertTrue(form.is_valid())

    def test_renew_form_date_max(self):
        date = datetime.date.today() + datetime.timedelta(weeks=4)
        form = RenewBookForm(data={'renewal_date': date})
        self.assertTrue(form.is_valid())

    

    
    