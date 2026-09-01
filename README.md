# E-commerce Catalog API

A Django REST Framework API for managing e-commerce product categories, products, product images, and search filters.

## Features

- Category CRUD API
- Product CRUD API
- Product image support
- Unique SKU validation
- Product search by title or SKU
- Price range filtering
- Category filtering with child category support
- Automated API tests

## Tech Stack

- Python
- Django
- Django REST Framework
- SQLite
- Pillow

## Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/api/
```

## API Endpoints

```text
GET    /api/categories/
POST   /api/categories/
GET    /api/categories/{id}/
PATCH  /api/categories/{id}/
DELETE /api/categories/{id}/

GET    /api/products/
POST   /api/products/
GET    /api/products/{id}/
PATCH  /api/products/{id}/
DELETE /api/products/{id}/

GET    /api/products/search/
```

## Product Search Filters

The search endpoint supports these query parameters:

```text
q          Search by product title or SKU
title      Search by product title
sku        Search by SKU
min_price  Minimum product price
max_price  Maximum product price
category   Category ID, including child categories
```

Example:

```bash
http://127.0.0.1:8000/api/products/search/?q=phone&min_price=100&max_price=800
```

## Tests

Run the test suite with:

```bash
python manage.py test
```

## Environment Variables

For production, set a secure Django secret key:

```bash
DJANGO_SECRET_KEY=your-secret-key
```

## Notes

The local SQLite database file `db.sqlite3`, uploaded media files, virtual environments, and temporary output files are ignored by Git.
