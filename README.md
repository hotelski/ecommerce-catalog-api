# E-commerce Catalog API

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Django](https://img.shields.io/badge/Django-5.2-green)
![DRF](https://img.shields.io/badge/Django%20REST%20Framework-3.18-red)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)

A clean Django REST Framework API for managing an e-commerce product catalog with categories, products, product images, SKU validation, and flexible search filters.

## Highlights

- Full CRUD for categories and products
- Product image upload support
- Unique SKU validation
- Search by product title or SKU
- Price range filtering
- Category filtering with child category support
- Automated API test coverage

## Tech Stack

| Tool | Purpose |
|---|---|
| Django | Web framework |
| Django REST Framework | API layer |
| SQLite | Local database |
| Pillow | Image upload support |

## Quick Start

Clone the repository:

```bash
git clone https://github.com/hotelski/ecommerce-catalog-api.git
cd ecommerce-catalog-api

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/api/
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/categories/` | List categories |
| POST | `/api/categories/` | Create category |
| GET | `/api/categories/{id}/` | Retrieve category |
| PATCH | `/api/categories/{id}/` | Update category |
| DELETE | `/api/categories/{id}/` | Delete category |
| GET | `/api/products/` | List products |
| POST | `/api/products/` | Create product |
| GET | `/api/products/{id}/` | Retrieve product |
| PATCH | `/api/products/{id}/` | Update product |
| DELETE | `/api/products/{id}/` | Delete product |
| GET | `/api/products/search/` | Search products |

## Search Example

```bash
GET /api/products/search/?q=phone&min_price=100&max_price=800
```

Supported filters:

```text
q          Search by title or SKU
title      Filter by product title
sku        Filter by SKU
min_price  Minimum price
max_price  Maximum price
category   Category ID, including child categories
```

## Tests

```bash
python manage.py test
```

