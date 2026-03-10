from decimal import Decimal
import os

import requests
from django.contrib import messages
from django.shortcuts import redirect, render

# Service URLs
CUSTOMER_SERVICE = os.getenv('CUSTOMER_SERVICE_URL', 'http://localhost:8002/api/customers')
STAFF_SERVICE = os.getenv('STAFF_SERVICE_URL', 'http://localhost:8007/api/staff')
BOOK_SERVICE = os.getenv('BOOK_SERVICE_URL', 'http://localhost:8003/api/books')
CART_SERVICE = os.getenv('CART_SERVICE_URL', 'http://localhost:8004/api/carts')
ORDER_SERVICE = os.getenv('ORDER_SERVICE_URL', 'http://localhost:8006/api/orders')
CATALOG_SERVICE = os.getenv('CATALOG_SERVICE_URL', 'http://localhost:8008/api/catalog')


def _address_from_request(request):
    return {
        'line1': request.POST.get('line1', '').strip(),
        'line2': request.POST.get('line2', '').strip(),
        'city': request.POST.get('city', '').strip(),
        'state': request.POST.get('state', '').strip(),
        'postal_code': request.POST.get('postal_code', '').strip(),
        'country': request.POST.get('country', '').strip(),
    }


def _is_valid_shipping_address(address):
    return bool(address['line1'] and address['city'] and address['country'])


def _book_payload_from_request(request):
    category_id, _ = _category_id_from_request(request)
    return {
        'title': request.POST.get('title', '').strip(),
        'author': request.POST.get('author', '').strip(),
        'price': request.POST.get('price', '').strip(),
        'stock': request.POST.get('stock', '').strip(),
        'category_id': category_id,
    }


def _category_id_from_request(request):
    raw_category_id = request.POST.get('category_id', '').strip()
    if not raw_category_id:
        return None, None
    try:
        return int(raw_category_id), None
    except ValueError:
        return None, 'category_id phai la so nguyen.'


def _sync_book_category(book_id, category_id):
    payload = {'category_id': category_id}
    return requests.put(
        f'{CATALOG_SERVICE}/books/{book_id}/category/',
        json=payload,
        timeout=5,
    )


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        data = {
            'name': request.POST['name'],
            'email': request.POST['email'],
            'password': request.POST['password'],
        }
        try:
            response = requests.post(f'{CUSTOMER_SERVICE}/register/', json=data, timeout=5)
            if response.status_code == 201:
                messages.success(request, 'Dang ky thanh cong! Vui long dang nhap.')
                return redirect('login')
            response_data = response.json() if response.content else {}
            message = response_data.get('error') or str(response_data) or 'Dang ky that bai!'
            messages.error(request, f'Dang ky that bai: {message}')
        except Exception as exc:
            messages.error(request, f'Loi ket noi: {exc}')

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        data = {
            'email': request.POST['email'],
            'password': request.POST['password'],
        }
        try:
            response = requests.post(f'{CUSTOMER_SERVICE}/login/', json=data, timeout=5)
            if response.status_code == 200:
                user_data = response.json()
                request.session.pop('staff_id', None)
                request.session.pop('staff_name', None)
                request.session.pop('staff_email', None)
                request.session.pop('staff_role', None)
                request.session['user_id'] = user_data['id']
                request.session['user_name'] = user_data['name']
                request.session['user_email'] = user_data['email']
                messages.success(request, f'Xin chao {user_data["name"]}!')
                return redirect('books')
            messages.error(request, 'Email hoac mat khau khong dung!')
        except Exception as exc:
            messages.error(request, f'Loi ket noi: {exc}')

    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    messages.success(request, 'Da dang xuat!')
    return redirect('home')


def staff_login(request):
    if request.method == 'POST':
        data = {
            'email': request.POST['email'],
            'password': request.POST['password'],
        }
        try:
            response = requests.post(f'{STAFF_SERVICE}/login/', json=data, timeout=5)
            if response.status_code == 200:
                staff_data = response.json()
                request.session.pop('user_id', None)
                request.session.pop('user_name', None)
                request.session.pop('user_email', None)
                request.session['staff_id'] = staff_data['id']
                request.session['staff_name'] = staff_data['name']
                request.session['staff_email'] = staff_data['email']
                request.session['staff_role'] = staff_data['role']
                messages.success(request, f'Staff login thanh cong: {staff_data["name"]}')
                return redirect('staff_dashboard')
            messages.error(request, 'Tai khoan staff khong hop le!')
        except Exception as exc:
            messages.error(request, f'Loi ket noi staff service: {exc}')

    return render(request, 'staff_login.html')


def books(request):
    if 'user_id' not in request.session:
        messages.warning(request, 'Vui long dang nhap!')
        return redirect('login')

    categories = []
    selected_category_id = request.GET.get('category_id', '').strip()
    selected_sort = request.GET.get('sort', '').strip()

    try:
        categories_response = requests.get(f'{CATALOG_SERVICE}/categories/', timeout=5)
        if categories_response.status_code == 200:
            categories = categories_response.json()
    except Exception:
        categories = []

    params = {}
    if selected_category_id:
        params['category_id'] = selected_category_id
    if selected_sort:
        params['sort'] = selected_sort

    try:
        response = requests.get(f'{CATALOG_SERVICE}/books/', params=params, timeout=5)
        books_list = response.json() if response.status_code == 200 else []
    except Exception as exc:
        books_list = []
        messages.error(request, f'Khong the tai danh sach sach: {exc}')

    return render(
        request,
        'books.html',
        {
            'books': books_list,
            'categories': categories,
            'selected_category_id': selected_category_id,
            'selected_sort': selected_sort,
        },
    )


def book_detail(request, book_id):
    if 'user_id' not in request.session:
        messages.warning(request, 'Vui long dang nhap!')
        return redirect('login')

    try:
        response = requests.get(f'{BOOK_SERVICE}/{book_id}/', timeout=5)
        if response.status_code != 200:
            messages.error(request, 'Khong tim thay sach.')
            return redirect('books')
        book = response.json()
    except Exception as exc:
        messages.error(request, f'Khong the tai thong tin sach: {exc}')
        return redirect('books')

    return render(request, 'book_detail.html', {'book': book})


def add_to_cart(request, book_id):
    if 'user_id' not in request.session:
        return redirect('login')

    customer_id = request.session['user_id']
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    data = {
        'book_id': book_id,
        'quantity': quantity,
    }

    try:
        response = requests.post(f'{CART_SERVICE}/{customer_id}/', json=data, timeout=5)
        if response.status_code == 201:
            messages.success(request, 'Da them sach vao gio hang!')
        else:
            messages.error(request, 'Khong the them vao gio hang!')
    except Exception as exc:
        messages.error(request, f'Loi: {exc}')

    redirect_to = request.POST.get('redirect_to', 'books')
    if redirect_to == 'detail':
        return redirect('book_detail', book_id=book_id)
    if redirect_to == 'cart':
        return redirect('cart')
    return redirect('books')


def cart_view(request):
    if 'user_id' not in request.session:
        return redirect('login')

    customer_id = request.session['user_id']
    cart_items = []
    total_price = Decimal('0.00')
    customer_address = {
        'line1': '',
        'line2': '',
        'city': '',
        'state': '',
        'postal_code': '',
        'country': '',
    }

    try:
        cart_response = requests.get(f'{CART_SERVICE}/{customer_id}/', timeout=5)
        if cart_response.status_code == 200:
            cart_data = cart_response.json()
            for item in cart_data.get('items', []):
                book_response = requests.get(f'{BOOK_SERVICE}/{item["book_id"]}/', timeout=5)
                if book_response.status_code != 200:
                    continue

                book = book_response.json()
                item_total = Decimal(str(book['price'])) * int(item['quantity'])
                cart_items.append(
                    {
                        'id': item['id'],
                        'book': book,
                        'quantity': int(item['quantity']),
                        'total': item_total,
                    }
                )
                total_price += item_total

        customer_response = requests.get(f'{CUSTOMER_SERVICE}/{customer_id}/', timeout=5)
        if customer_response.status_code == 200:
            customer_data = customer_response.json()
            customer_address.update(customer_data.get('address') or {})
    except Exception as exc:
        messages.error(request, f'Loi khi tai gio hang: {exc}')

    return render(
        request,
        'cart.html',
        {
            'cart_items': cart_items,
            'total_price': total_price,
            'customer_address': customer_address,
        },
    )


def remove_from_cart(request, item_id):
    if request.method == 'POST':
        try:
            response = requests.delete(f'{CART_SERVICE}/items/{item_id}/', timeout=5)
            if response.status_code == 200:
                messages.success(request, 'Da xoa sach khoi gio hang!')
            else:
                messages.error(request, 'Khong the xoa!')
        except Exception as exc:
            messages.error(request, f'Loi: {exc}')

    return redirect('cart')


def update_cart_item(request, item_id):
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        data = {'quantity': int(quantity)}
        try:
            response = requests.put(f'{CART_SERVICE}/items/{item_id}/update/', json=data, timeout=5)
            if response.status_code == 200:
                messages.success(request, 'Da cap nhat so luong!')
            else:
                messages.error(request, 'Khong the cap nhat!')
        except Exception as exc:
            messages.error(request, f'Loi: {exc}')

    return redirect('cart')


def checkout(request):
    if 'user_id' not in request.session:
        return redirect('login')

    if request.method != 'POST':
        return redirect('cart')

    customer_id = request.session['user_id']
    try:
        shipping_address = _address_from_request(request)
        if not _is_valid_shipping_address(shipping_address):
            messages.error(request, 'Dia chi giao hang can co line1, city va country.')
            return redirect('cart')

        update_address_response = requests.put(
            f'{CUSTOMER_SERVICE}/{customer_id}/address/',
            json=shipping_address,
            timeout=5,
        )
        if update_address_response.status_code != 200:
            messages.error(request, 'Khong the cap nhat dia chi giao hang.')
            return redirect('cart')

        cart_response = requests.get(f'{CART_SERVICE}/{customer_id}/', timeout=5)
        if cart_response.status_code != 200:
            messages.error(request, 'Khong the doc gio hang!')
            return redirect('cart')

        cart_data = cart_response.json()
        cart_items = cart_data.get('items', [])
        if not cart_items:
            messages.warning(request, 'Gio hang dang trong.')
            return redirect('cart')

        order_items = []
        cart_item_ids = []
        for item in cart_items:
            quantity = int(item['quantity'])
            book_response = requests.get(f'{BOOK_SERVICE}/{item["book_id"]}/', timeout=5)
            if book_response.status_code != 200:
                messages.error(request, f'Khong tim thay sach id={item["book_id"]}.')
                return redirect('cart')

            book = book_response.json()
            available_stock = int(book.get('stock', 0))
            if available_stock < quantity:
                messages.error(
                    request,
                    f'Sach "{book.get("title", "Unknown")}" khong du ton kho.',
                )
                return redirect('cart')

            order_items.append(
                {
                    'book_id': int(item['book_id']),
                    'book_title': book.get('title', ''),
                    'quantity': quantity,
                    'unit_price': str(book['price']),
                }
            )
            cart_item_ids.append(int(item['id']))

        create_order_response = requests.post(
            f'{ORDER_SERVICE}/{customer_id}/',
            json={'items': order_items, 'shipping_address': shipping_address},
            timeout=10,
        )
        if create_order_response.status_code != 201:
            messages.error(request, 'Tao don hang that bai!')
            return redirect('cart')

        for item in order_items:
            requests.put(
                f'{BOOK_SERVICE}/{item["book_id"]}/stock/',
                json={'stock_change': -int(item['quantity'])},
                timeout=5,
            )

        for item_id in cart_item_ids:
            requests.delete(f'{CART_SERVICE}/items/{item_id}/', timeout=5)

        messages.success(request, 'Dat hang thanh cong!')
        return redirect('orders')

    except Exception as exc:
        messages.error(request, f'Loi dat hang: {exc}')
        return redirect('cart')


def orders(request):
    if 'user_id' not in request.session:
        return redirect('login')

    customer_id = request.session['user_id']
    try:
        response = requests.get(f'{ORDER_SERVICE}/{customer_id}/', timeout=5)
        orders_data = response.json() if response.status_code == 200 else []
    except Exception as exc:
        messages.error(request, f'Loi khi tai don hang: {exc}')
        orders_data = []

    return render(request, 'orders.html', {'orders': orders_data})


def customer_profile(request):
    if 'user_id' not in request.session:
        messages.warning(request, 'Vui long dang nhap!')
        return redirect('login')

    customer_id = request.session['user_id']
    profile = {
        'name': request.session.get('user_name', ''),
        'email': request.session.get('user_email', ''),
        'address': {
            'line1': '',
            'line2': '',
            'city': '',
            'state': '',
            'postal_code': '',
            'country': '',
        },
    }

    if request.method == 'POST':
        payload = {
            'name': request.POST.get('name', '').strip(),
            'address': _address_from_request(request),
        }

        try:
            update_response = requests.put(
                f'{CUSTOMER_SERVICE}/{customer_id}/',
                json=payload,
                timeout=5,
            )
            if update_response.status_code == 200:
                updated_profile = update_response.json()
                request.session['user_name'] = updated_profile.get('name', request.session.get('user_name', ''))
                request.session['user_email'] = updated_profile.get('email', request.session.get('user_email', ''))
                profile.update(updated_profile)
                profile['address'] = updated_profile.get('address') or profile['address']
                messages.success(request, 'Cap nhat thong tin thanh cong!')
            else:
                response_data = update_response.json() if update_response.content else {}
                messages.error(request, f'Khong the cap nhat thong tin: {response_data}')
        except Exception as exc:
            messages.error(request, f'Loi cap nhat thong tin: {exc}')

    try:
        profile_response = requests.get(f'{CUSTOMER_SERVICE}/{customer_id}/', timeout=5)
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            profile.update(profile_data)
            profile['address'] = profile_data.get('address') or profile['address']
    except Exception as exc:
        messages.error(request, f'Khong the tai thong tin customer: {exc}')

    return render(request, 'customer_profile.html', {'profile': profile})


def staff_dashboard(request):
    if 'staff_id' not in request.session:
        messages.warning(request, 'Vui long dang nhap staff.')
        return redirect('staff_login')

    books_list = []
    orders_list = []
    categories_list = []

    try:
        books_response = requests.get(f'{CATALOG_SERVICE}/books/', timeout=5)
        if books_response.status_code == 200:
            books_list = books_response.json()
    except Exception as exc:
        messages.error(request, f'Loi tai danh sach sach: {exc}')

    try:
        categories_response = requests.get(f'{CATALOG_SERVICE}/categories/', timeout=5)
        if categories_response.status_code == 200:
            categories_list = categories_response.json()
    except Exception as exc:
        messages.error(request, f'Loi tai danh muc category: {exc}')

    try:
        response = requests.get(f'{ORDER_SERVICE}/all/', timeout=8)
        if response.status_code == 200:
            orders_list = response.json()
    except Exception as exc:
        messages.error(request, f'Loi tai danh sach don hang: {exc}')

    return render(
        request,
        'staff_dashboard.html',
        {
            'books': books_list,
            'orders': orders_list,
            'categories': categories_list,
            'staff_name': request.session.get('staff_name', ''),
            'staff_role': request.session.get('staff_role', ''),
        },
    )


def update_order_status_by_staff(request, order_id):
    if 'staff_id' not in request.session:
        return redirect('staff_login')

    if request.method != 'POST':
        return redirect('staff_dashboard')

    status_value = request.POST.get('status', '').strip()
    if not status_value:
        messages.error(request, 'Status khong hop le.')
        return redirect('staff_dashboard')

    try:
        response = requests.put(
            f'{ORDER_SERVICE}/detail/{order_id}/status/',
            json={'status': status_value},
            timeout=5,
        )
        if response.status_code == 200:
            messages.success(request, f'Da cap nhat order #{order_id} -> {status_value}.')
        else:
            messages.error(request, f'Cap nhat that bai cho order #{order_id}.')
    except Exception as exc:
        messages.error(request, f'Loi cap nhat order: {exc}')

    return redirect('staff_dashboard')


def create_book_by_staff(request):
    if 'staff_id' not in request.session:
        return redirect('staff_login')

    if request.method != 'POST':
        return redirect('staff_dashboard')

    data = _book_payload_from_request(request)
    category_id, category_error = _category_id_from_request(request)
    if category_error:
        messages.error(request, category_error)
        return redirect('staff_dashboard')

    try:
        response = requests.post(
            f'{BOOK_SERVICE}/create/',
            json=data,
            timeout=5,
        )
        if response.status_code == 201:
            created_book = response.json()
            created_book_id = created_book.get('id')
            if created_book_id:
                try:
                    category_response = _sync_book_category(created_book_id, category_id)
                    if category_response.status_code not in [200, 201]:
                        messages.warning(request, 'Them sach thanh cong, nhung gan category that bai.')
                except Exception:
                    messages.warning(request, 'Them sach thanh cong, nhung catalog-service khong phan hoi.')
            messages.success(request, 'Da them sach moi.')
        else:
            response_data = response.json() if response.content else {}
            messages.error(request, f'Khong the them sach: {response_data}')
    except Exception as exc:
        messages.error(request, f'Loi them sach: {exc}')

    return redirect('staff_dashboard')


def update_book_by_staff(request, book_id):
    if 'staff_id' not in request.session:
        return redirect('staff_login')

    if request.method != 'POST':
        return redirect('staff_dashboard')

    data = _book_payload_from_request(request)
    category_id, category_error = _category_id_from_request(request)
    if category_error:
        messages.error(request, category_error)
        return redirect('staff_dashboard')

    try:
        response = requests.put(
            f'{BOOK_SERVICE}/{book_id}/update/',
            json=data,
            timeout=5,
        )
        if response.status_code == 200:
            try:
                category_response = _sync_book_category(book_id, category_id)
                if category_response.status_code not in [200, 201]:
                    messages.warning(request, f'Da cap nhat sach #{book_id}, nhung category chua duoc dong bo.')
            except Exception:
                messages.warning(request, f'Da cap nhat sach #{book_id}, nhung catalog-service khong phan hoi.')
            messages.success(request, f'Da cap nhat sach #{book_id}.')
        else:
            response_data = response.json() if response.content else {}
            messages.error(request, f'Khong the cap nhat sach #{book_id}: {response_data}')
    except Exception as exc:
        messages.error(request, f'Loi cap nhat sach: {exc}')

    return redirect('staff_dashboard')


def delete_book_by_staff(request, book_id):
    if 'staff_id' not in request.session:
        return redirect('staff_login')

    if request.method != 'POST':
        return redirect('staff_dashboard')

    try:
        response = requests.delete(
            f'{BOOK_SERVICE}/{book_id}/delete/',
            timeout=5,
        )
        if response.status_code == 200:
            messages.success(request, f'Da xoa sach #{book_id}.')
        else:
            response_data = response.json() if response.content else {}
            messages.error(request, f'Khong the xoa sach #{book_id}: {response_data}')
    except Exception as exc:
        messages.error(request, f'Loi xoa sach: {exc}')

    return redirect('staff_dashboard')


def create_category_by_staff(request):
    if 'staff_id' not in request.session:
        return redirect('staff_login')

    if request.method != 'POST':
        return redirect('staff_dashboard')

    name = request.POST.get('name', '').strip()
    description = request.POST.get('description', '').strip()
    if not name:
        messages.error(request, 'Ten category khong duoc de trong.')
        return redirect('staff_dashboard')

    try:
        response = requests.post(
            f'{CATALOG_SERVICE}/categories/',
            json={'name': name, 'description': description},
            timeout=5,
        )
        if response.status_code == 201:
            messages.success(request, 'Da tao category moi.')
        else:
            response_data = response.json() if response.content else {}
            messages.error(request, f'Khong the tao category: {response_data}')
    except Exception as exc:
        messages.error(request, f'Loi tao category: {exc}')

    return redirect('staff_dashboard')


def update_category_by_staff(request, category_id):
    if 'staff_id' not in request.session:
        return redirect('staff_login')

    if request.method != 'POST':
        return redirect('staff_dashboard')

    name = request.POST.get('name', '').strip()
    description = request.POST.get('description', '').strip()
    if not name:
        messages.error(request, 'Ten category khong duoc de trong.')
        return redirect('staff_dashboard')

    try:
        response = requests.put(
            f'{CATALOG_SERVICE}/categories/{category_id}/',
            json={'name': name, 'description': description},
            timeout=5,
        )
        if response.status_code == 200:
            messages.success(request, f'Da cap nhat category #{category_id}.')
        else:
            response_data = response.json() if response.content else {}
            messages.error(request, f'Khong the cap nhat category #{category_id}: {response_data}')
    except Exception as exc:
        messages.error(request, f'Loi cap nhat category: {exc}')

    return redirect('staff_dashboard')


def delete_category_by_staff(request, category_id):
    if 'staff_id' not in request.session:
        return redirect('staff_login')

    if request.method != 'POST':
        return redirect('staff_dashboard')

    try:
        response = requests.delete(
            f'{CATALOG_SERVICE}/categories/{category_id}/',
            timeout=5,
        )
        if response.status_code == 200:
            messages.success(request, f'Da xoa category #{category_id}.')
        else:
            response_data = response.json() if response.content else {}
            messages.error(request, f'Khong the xoa category #{category_id}: {response_data}')
    except Exception as exc:
        messages.error(request, f'Loi xoa category: {exc}')

    return redirect('staff_dashboard')


def update_book_stock_by_staff(request, book_id):
    if 'staff_id' not in request.session:
        return redirect('staff_login')

    if request.method != 'POST':
        return redirect('staff_dashboard')

    stock_change = request.POST.get('stock_change', '0').strip()
    try:
        stock_change_int = int(stock_change)
    except ValueError:
        messages.error(request, 'Gia tri stock_change phai la so nguyen.')
        return redirect('staff_dashboard')

    if stock_change_int == 0:
        messages.warning(request, 'Khong co thay doi ton kho.')
        return redirect('staff_dashboard')

    try:
        response = requests.put(
            f'{BOOK_SERVICE}/{book_id}/stock/',
            json={'stock_change': stock_change_int},
            timeout=5,
        )
        if response.status_code == 200:
            messages.success(request, f'Da cap nhat ton kho sach #{book_id}.')
        else:
            messages.error(request, f'Khong the cap nhat ton kho sach #{book_id}.')
    except Exception as exc:
        messages.error(request, f'Loi cap nhat ton kho: {exc}')

    return redirect('staff_dashboard')
