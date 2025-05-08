from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash

from .models import Books, User, Order, OrderItem
from .forms import BookForm, SignUpForm, LoginForm, ProfileForm


def index(request):
    books_list = Books.objects.all()

    # Paginate the books (3 books per page)
    paginator = Paginator(books_list, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Check for confirmation message in cookies
    confirmation_message = request.COOKIES.get('order_confirmation', None)

    context = {
        "page_obj": page_obj,
        "user": request.user,
        "confirmation_message": confirmation_message
    }

    # Clear the cookie by setting it with an expiry of 0 if it exists
    response = render(request, "echo/index.html", context)
    if confirmation_message:
        response.delete_cookie('order_confirmation')

    return response


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


@login_required
def profile(request):
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=request.user)
        if profile_form.is_valid():
            user = profile_form.save(commit=False)
            new_password = profile_form.cleaned_data.get('new_password')
            # If password was updated, set it
            if new_password:
                user.set_password(new_password)
            user.save()
            # Update session to prevent logout after password change
            if new_password:
                update_session_auth_hash(request, user)
            return redirect('index')
    else:
        profile_form = ProfileForm(instance=request.user)

    return render(request, 'echo/profile.html', {
        'form': profile_form,
        'user': request.user
    })


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


@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Books, id=book_id)
    # Initialize cart in session if it doesn't exist
    if 'cart' not in request.session:
        request.session['cart'] = {}

    # Add book to cart or increment quantity
    cart = request.session['cart']
    book_id_str = str(book_id)
    if book_id_str in cart:
        cart[book_id_str]['quantity'] += 1
    else:
        cart[book_id_str] = {
            'name': book.name,
            'author': book.author,
            'price': float(book.price),
            'quantity': 1
        }

    # Save the updated cart back to the session
    request.session['cart'] = cart
    request.session.modified = True  # Ensure session is marked as modified
    return redirect('index')


@login_required
def cart(request):
    cart = request.session.get('cart', {})
    # Calculate totals for each item and overall cart
    cart_items = []
    total_cart_price = 0
    for book_id, item in cart.items():
        item_total = item['price'] * item['quantity']
        total_cart_price += item_total
        cart_items.append({
            'book_id': book_id,
            'name': item['name'],
            'author': item['author'],
            'price': item['price'],
            'quantity': item['quantity'],
            'total': item_total
        })
    return render(request, 'echo/cart.html', {
        'cart_items': cart_items,
        'total_cart_price': total_cart_price,
        'user': request.user
    })


@login_required
def place_order(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if not cart:
            return redirect('cart')  # Redirect if cart is empty

        # Create a new order
        order = Order.objects.create(
            user=request.user,
            total_price=0
        )

        # Add items to the order and calculate total price
        total_price = 0
        for book_id, item in cart.items():
            item_total = item['price'] * item['quantity']
            total_price += item_total
            OrderItem.objects.create(
                order=order,
                book_name=item['name'],
                book_author=item['author'],
                price=item['price'],
                quantity=item['quantity']
            )

        # Update order total price
        order.total_price = total_price
        order.save()

        # Clear the cart
        request.session['cart'] = {}
        request.session.modified = True

        # Set confirmation cookie
        response = redirect('index')
        response.set_cookie(
            'order_confirmation',
            f'Order #{order.id} placed successfully.',
            max_age=60  # Cookie expires in 60 seconds
        )
        return response

    return redirect('cart')


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    # Precompute item totals for each order
    orders_with_totals = []
    for order in orders:
        items_with_totals = []
        for item in order.items.all():
            item_total = item.price * item.quantity
            items_with_totals.append({
                'book_name': item.book_name,
                'book_author': item.book_author,
                'price': item.price,
                'quantity': item.quantity,
                'total': item_total
            })
        orders_with_totals.append({
            'id': order.id,
            'created_at': order.created_at,
            'total_price': order.total_price,
            'items': items_with_totals
        })
    return render(request, 'echo/order_history.html', {
        'orders': orders_with_totals,
        'user': request.user
    })


@login_required
def update_quantity(request, book_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        book_id_str = str(book_id)
        if book_id_str in cart:
            action = request.POST.get('action')
            if action == 'increase':
                cart[book_id_str]['quantity'] += 1
            elif action == 'decrease' and cart[book_id_str]['quantity'] > 1:
                cart[book_id_str]['quantity'] -= 1

            # Save updated cart
            request.session['cart'] = cart
            request.session.modified = True
        return redirect('cart')
    return redirect('cart')


@login_required
def delete_from_cart(request, book_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        book_id_str = str(book_id)
        if book_id_str in cart:
            del cart[book_id_str]

            # Save updated cart
            request.session['cart'] = cart
            request.session.modified = True
        return redirect('cart')
    return redirect('cart')


@login_required
def clear_cart(request):
    if request.method == 'POST':
        request.session['cart'] = {}
        request.session.modified = True
        return redirect('cart')
    return redirect('cart')
