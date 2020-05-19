from django.shortcuts import render

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

    context = {
        'num_books': num_books,
        'num_books_with_novel': num_books_with_novel,
        'num_genres_with_fiction': num_genres_with_fiction,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
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

