#  QuickDeliver Lite

QuickDeliver Lite is a **Flask-based Delivery Management System** designed to streamline delivery operations for customers and drivers. It supports OTP-secured registration, delivery creation, driver assignment, delivery status tracking, and features an AI-powered chatbot using Cohere.

---

##  Objective

Build a role-based logistics platform where:
- Customers create delivery requests.
- Drivers accept and complete deliveries.
- Delivery progress is tracked in real time.
- An AI chatbot answers user queries related to the platform.

---

##  Tech Stack

| Layer              | Technology                       |
|--------------------|----------------------------------|
| **Backend**        | Python (Flask)                   |
| **Frontend**       | HTML, CSS, Bootstrap, Jinja2     |
| **Data Storage**   | JSON files                       |
| **AI Assistant**   | Cohere API (Command R+)          |
| **Authentication** | Password hashing (Werkzeug), OTP |
| **Env Management** | python-dotenv (.env file)        |

---

##  Key Features

-  Role-based dashboards for Customers & Drivers
-  OTP verification during user registration
-  Delivery request creation, acceptance, and tracking
-  AI chatbot for platform assistance (Cohere API)
-  Password encryption and session management
-  Simple, responsive UI

---

##  Implementation Methodology

- **Flask Framework:** For routing, authentication, and business logic.
- **Role-Based Access:** Separate views for customers and drivers.
- **Data Persistence:** Lightweight JSON file storage for prototype simplicity.
- **OTP Security:** Console-based OTP verification for user registration.
- **AI Chatbot:** Integrated using Cohere’s Command R+ model.
- **Template Engine:** Jinja2 templates for dynamic HTML rendering.



