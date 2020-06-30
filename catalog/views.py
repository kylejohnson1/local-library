import datetime

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from catalog.forms import RenewBookForm
from catalog.models import Author

# Create your views here.
from catalog.models import Book, Author, BookInstance, Genre
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status= 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Number of books that contain "novel"
    num_books_with_novel = Book.objects.filter(title__icontains='novel').count()

    # Number of genres that contain "fiction"
    num_genres_with_fiction = Genre.objects.filter(name__icontains='fiction').count()

    # Number of visits to this view, as counted in the session variable
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_books_with_novel': num_books_with_novel,
        'num_genres_with_fiction': num_genres_with_fiction,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }

    # Render HTML template index.html with the data in the context variable
    # render returns an HttpResponse object
    return render(request, 'index.html', context=context)


from django.views import generic
class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model=BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class AllLoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan."""
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_librarian.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk) # get the BookInstance with primary key pk

    # If this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding)
        form = RenewBookForm(request.POST)

        # Check if the form is valid
        if form.is_valid():
            # Process the data in form.cleaned_data as required (do what form is supposed to do)
            # Here we just write it to the model due_back field
            book_instance.due_back = form.cleaned_data['renewal_date'] # change book instance in database
            book_instance.save() # write to database

            # Redirect to a new URL
            return HttpResponseRedirect(reverse('all-borrowed')) # reverse gets the URL based on the string, because actual URL may change
    # If this is a GET (or any other method) this (probably) means this is the first time the user has seen the form
    # Create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}
    permission_required = 'catalog.can_edit_authors'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.can_edit_authors'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors') # reverse_lazy used because a URL to a class-based view attribute is used
    permission_required = 'catalog.can_edit_authors'

class BookCreate(PermissionRequiredMixin, CreateView):
    # uses template "book_form.html"
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_edit_books'

class BookUpdate(PermissionRequiredMixin, UpdateView):
    # uses template "book_form.html"
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_edit_books'

class BookDelete(PermissionRequiredMixin, DeleteView):
    # uses template "book_confirm_delete.html"
    model = Book
    success_url = reverse_lazy('books') # reverse_lazy used because a URL to a class-based view attribute is used
    permission_required = 'catalog.can_edit_books'