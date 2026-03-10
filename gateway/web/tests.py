from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse


class BookDetailViewTests(TestCase):
    def setUp(self):
        session = self.client.session
        session['user_id'] = 1
        session.save()

    @patch('web.views.requests.get')
    def test_book_detail_renders_book_data(self, mock_get):
        mock_get.return_value = Mock(
            status_code=200,
            json=Mock(
                return_value={
                    'id': 7,
                    'title': 'Clean Code',
                    'author': 'Robert C. Martin',
                    'price': '32.00',
                    'stock': 12,
                }
            ),
        )

        response = self.client.get(reverse('book_detail', args=[7]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Clean Code')
        self.assertContains(response, 'Robert C. Martin')


class AddToCartRedirectTests(TestCase):
    def setUp(self):
        session = self.client.session
        session['user_id'] = 1
        session.save()

    @patch('web.views.requests.post')
    def test_add_to_cart_redirects_to_detail_when_requested(self, mock_post):
        mock_post.return_value = Mock(status_code=201)

        response = self.client.post(
            reverse('add_to_cart', args=[7]),
            {'quantity': '2', 'redirect_to': 'detail'},
        )

        self.assertRedirects(response, reverse('book_detail', args=[7]))

    @patch('web.views.requests.post')
    def test_add_to_cart_redirects_to_cart_when_requested(self, mock_post):
        mock_post.return_value = Mock(status_code=201)

        response = self.client.post(
            reverse('add_to_cart', args=[7]),
            {'quantity': '3', 'redirect_to': 'cart'},
        )

        self.assertRedirects(response, reverse('cart'))
