# 📦 Warehouse Inventory & Order System

![Built with FastAPI](https://img.shields.io/badge/Built%20with-FastAPI-green?style=flat-square)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue?style=flat-square)

> A backend system for managing product inventory across multiple warehouses, tracking user orders, and handling delivery logistics.

This project simulates a furniture retailer backend (like IKEA), including product series, warehouse zones, delivery methods, and customer orders. It's built using **FastAPI + SQLModel + PostgreSQL**, with clean separation between data models, business logic, and API routes.

---

## 📚 Table of Contents

- [Overview](#overview)
- [Key Components](#key-components)
- [Data Modeling and Relationships](#data-modeling-and-relationships)
- [How to Start](#how-to-start)
- [Running Tests](#running-tests)
- [Future Enhancements](#future-enhancements)

---

## 🚀 Overview

This backend system provides the following features:

- Register users and track their orders.
- Model physical **warehouses** with delivery zones and self-service options.
- Manage **product inventory** across warehouses using a stock system.
- Support **order placements** with various delivery methods and costs.
- Use **enum-based constraints** for categories, delivery types, and locations.

---

## 🧱 Key Components

- **Warehouse**: Tracks stock, zip code zones, and if self-pickup is allowed.
- **Product**: Belongs to a category and optional product series.
- **Stock**: Intermediate table between Warehouse and Product.
- **User**: Customers placing orders.
- **Order + OrderItem**: Customer purchases and which products are bought.
- **Enums**: Used to standardize categories, delivery methods, locations, etc.

---

## 🔗 Data Modeling and Relationships

### 🏢 Warehouse

```python
class Warehouse(SQLModel, table=True):
    warehouse_id: str
    name: str
    allows_self_service: bool
    served_zipcodes: list[str]
    stocks: list["Stock"] = Relationship(back_populates="warehouse")
```
