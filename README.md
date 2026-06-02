# Storefront

A simple e-commerce storefront where customers can browse products, filter by collection, add items to a cart, and place orders. Built with a Django REST Framework backend and a React frontend.

## Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_store
python manage.py runserver
```

API base: `http://127.0.0.1:8000/api/store/`

Core endpoints:

- `GET /api/store/products/?search=&collection=&available=true`
- `GET /api/store/collections/`
- `POST /api/store/carts/`
- `POST /api/store/carts/{cart_id}/items/`
- `POST /api/store/carts/checkout/`
- `GET /api/store/orders/?email=customer@example.com`

## Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` to Django.

## Verification

```bash
python manage.py test store
python manage.py check
```
