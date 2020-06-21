from django.urls import path
from . import views

# this file redirects the URLS (for example, 'books/') to the view (for example, 'views.BookListView.as_view()')
# the views can be functions (like 'views.index' or 'views.renew_book_librarian') or Django classes (like 'views.AuthorListView.as_view()')

urlpatterns = [
    path('', views.index, name='index'), # uses a function-based view
    path('books/', views.BookListView.as_view(), name='books'), # uses a class-based view
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'), # the pk parameter is passed to the view
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    path('borrowed/', views.AllLoanedBooksListView.as_view(), name='all-borrowed'),
    path('book/<uuid:pk>/renew', views.renew_book_librarian, name='renew-book-librarian'),
    path('author/create/', views.AuthorCreate.as_view(), name='author_create'),
    path('author/<int:pk>/update', views.AuthorUpdate.as_view(), name='author_update'),
    path('author/<int:pk>/delete', views.AuthorDelete.as_view(), name='author_delete'),
    path('book/create/', views.BookCreate.as_view(), name='book_create'),
    path('book/<int:pk>/update', views.BookUpdate.as_view(), name='book_update'),
    path('book/<int:pk>/delete', views.BookDelete.as_view(), name='book_delete'),
]

