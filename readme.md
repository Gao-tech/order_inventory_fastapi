# 🛒 Order_Inventory System — FastAPI + AWS Lambda + RDS

**Author:** Jie Gao (Jessi)  
📅 **Date:** April 2025

---

## 🧱 Project Goal

Build a **scalable backend system** to support:

- ✅ Real-time stock allocation
- 🚚 Region-based delivery from nearest warehouse
- 🛒 Guest checkout (no login required)

Original Tech Stack:

- 🐍 **FastAPI** (Python) + Mangum
- 🛢️ **PostgreSQL** (AWS RDS)
- 🔐 JWT (User and Admin-free)
- ☁️ **Serverless Application Model** (SAM)
- 🧱 Deployed using AWS Lambda & CloudFormation

---

### Assumption 1: Regional Delivery Logic

> A product is always delivered from the nearest warehouse, based on zipcode.

- 📦 **Fixed delivery cost** by method:
  - Self-service
  - Curbside
  - In-door
- 🕒 **Standardized delivery time**: 3 days from order

✅ This simplifies modeling by removing the need for dynamic cost/time calculation in the MVP.

---

### Assumption 2: Product ID System

> Inspired by IKEA’s system, each product has a unique **“Article number”**

Example:
Product ID: 493.857.51 # Complete Bed ├── Frame: 704.894.50 └── Mattress: 604.894.55

For this project:

- Only the **parent product ID** (e.g., `493.857.51`) is used
- Keeps schema simple and focused

🔧 Future work can support bundles and sub-items with one-to-many relationships.

---

## 🗂 Relational Table Design

Six core tables reflect the main business logic:

User # Stores user or guest details
Product # Main catalog of items (single ID per product)
Warehouse # Regional fulfillment centers
Stock # Inventory quantity per product per warehouse
Order # Contains address, delivery method, etc.
OrderItem # Quantity per product in the order

- ✔️ Stock is allocated based on **nearest warehouse**
- ✔️ Orders can be created by **guests** (no login required)
- ✔️ Product availability is **region-aware**

---

## 🔄 Order Flow (Including Guest Users)

1. Guest places order with delivery address
2. Backend:
   - Finds nearest warehouse based on zipcode
   - Checks stock availability
   - Calculates cost & delivery ETA (fixed rules)
3. Order stored in database
4. JWT is issued **only if needed** (for admin APIs)

---

## 🔬 Tested via Postman

- ✅ Create guest orders
- ✅ Add items from stock
- ✅ Verify stock reduction from correct warehouse

---

## ☁️ Cloud Deployment Experience

> “I thought: let’s scale this up and deploy it to the cloud!”  
> Spoiler: **the cloud had other plans.**

The goal was to build **serverless logic**, and integrating:

- RDS (hold PostgreSQL database)
- Region-aware warehouse logic
- SQL + Lambda latency optimization

...meant more configuration and tuning than expected — **a great learning journey**.

---
