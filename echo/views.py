from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

from .models import Books, User
from .forms import BookForm, SignUpForm, LoginForm


def index(request):
    books_list = Books.objects.all()

    # Paginate the books (3 books per page)
    paginator = Paginator(books_list, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj, "user": request.user}
    return render(request, "echo/index.html", context)


@login_required
def add(request):
    if request.method == "POST":
        book_form = BookForm(request.POST)
        if book_form.is_valid():
            book_form.save()
            return redirect('index')
    else:
        book_form = BookForm()
    return render(request, "echo/addBook.html", {'book_form': book_form})


@login_required
def edit(request, book_id):
    bookToEdit = get_object_or_404(Books, id=book_id)

    if request.method == "POST":
        book_form = BookForm(request.POST, instance=bookToEdit)
        if book_form.is_valid():
            book_form.save()
            return redirect('index')
    else:
        book_form = BookForm(instance=bookToEdit)

    return render(request, "echo/editBook.html", {'book_form': book_form})


@login_required
def delete(request, book_id):
    bookToDelete = get_object_or_404(Books, id=book_id)
    bookToDelete.delete()
    return redirect('index')


def signUp(request):
    if request.method == "POST":
        signUp_form = SignUpForm(request.POST)
        if signUp_form.is_valid():
            user = signUp_form.save()
            login(request, user)
            return redirect('index')
    else:
        signUp_form = SignUpForm()
    return render(request, "echo/signUp.html", {'signUp_form': signUp_form})


def logIn(request):
    if request.method == "POST":
        logIn_form = LoginForm(request.POST)
        if logIn_form.is_valid():
            username = logIn_form.cleaned_data['username']
            password = logIn_form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                logIn_form.add_error(None, "Invalid username or password")
    else:
        logIn_form = LoginForm()
    return render(request, "echo/logIn.html", {'logIn_form': logIn_form})


def logOut(request):
    logout(request)
    return redirect('index')
