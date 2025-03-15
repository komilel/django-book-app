from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator

from .models import Books
from .forms import BookForm


def index(request):
    books_list = Books.objects.all()

    # Paginate the books (3 book per page)
    paginator = Paginator(books_list, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj}
    return render(request, "echo/index.html", context)


def add(request):
    if request.method == "POST":
        book_form = BookForm(request.POST)
        if book_form.is_valid():
            book_form.save()
            return redirect('index')
    else:
        book_form = BookForm()
    return render(request, "echo/add.html", {'book_form': book_form})


def edit(request, book_id):
    bookToEdit = get_object_or_404(Books, id=book_id)

    print(f"Request method: {request.method}")
    if request.method == "POST":
        book_form = BookForm(request.POST, instance=bookToEdit)
        if book_form.is_valid():
            book_form.save()
            return redirect('index')
    else:
        book_form = BookForm(instance=bookToEdit)

    print(f"DEBUG BOOK: {bookToEdit}")
    print(f"DEBUG: {book_form.instance}")
    return render(request, "echo/edit.html", {'book_form': book_form})


def delete(requst, book_id):
    bookToDelete = get_object_or_404(Books, id=book_id)
    bookToDelete.delete()
    return redirect('index')
