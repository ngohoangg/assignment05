from unittest.mock import Mock, patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Cart, CartItem


class CartValidationTests(APITestCase):
    @patch('carts.views.requests.get')
    def test_add_item_rejects_non_positive_quantity(self, mock_get):
        response = self.client.post(
            reverse('cart_view', args=[1]),
            {'book_id': 10, 'quantity': 0},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity', response.data)
        self.assertEqual(CartItem.objects.count(), 0)
        mock_get.assert_not_called()

    @patch('carts.views.requests.get')
    def test_add_item_rejects_invalid_book_id(self, mock_get):
        mock_get.return_value = Mock(status_code=status.HTTP_404_NOT_FOUND)

        response = self.client.post(
            reverse('cart_view', args=[1]),
            {'book_id': 9999, 'quantity': 2},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['book_id'][0], 'Book does not exist.')
        self.assertEqual(CartItem.objects.count(), 0)

    @patch('carts.views.requests.get')
    def test_add_item_increments_existing_item_quantity(self, mock_get):
        mock_get.return_value = Mock(status_code=status.HTTP_200_OK)

        url = reverse('cart_view', args=[1])
        self.client.post(url, {'book_id': 7, 'quantity': 2}, format='json')
        self.client.post(url, {'book_id': 7, 'quantity': 3}, format='json')

        cart_item = CartItem.objects.get(cart__customer_id=1, book_id=7)
        self.assertEqual(cart_item.quantity, 5)

    def test_update_item_rejects_zero_quantity(self):
        cart = Cart.objects.create(customer_id=1)
        item = CartItem.objects.create(cart=cart, book_id=7, quantity=2)

        response = self.client.put(
            reverse('update_item', args=[item.id]),
            {'quantity': 0},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 2)

    def test_update_item_sets_exact_quantity(self):
        cart = Cart.objects.create(customer_id=1)
        item = CartItem.objects.create(cart=cart, book_id=7, quantity=2)

        response = self.client.put(
            reverse('update_item', args=[item.id]),
            {'quantity': 6},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 6)
