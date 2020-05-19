from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), # uses a function-based view
    path('books/', views.BookListView.as_view(), name='books'), # uses a class-based view
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail')
]

