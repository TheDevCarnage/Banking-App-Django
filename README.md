# NextGen Bank – Django-Based Banking API

NextGen Bank is a modern banking API system built with **Django REST Framework**, designed to simulate real-world banking operations with secure authentication, user account management, and virtual card handling. It includes features like JWT + OTP (2-step) login, next-of-kin management, transaction handling, and virtual card operations.

---

## 🔧 Tech Stack

- **Backend:** Django, Django REST Framework
  
- **Database:** PostgreSQL
  
- **Auth:** JWT + OTP (2-Step Verification)
  
- **Task Queue:** Celery
  
- **Async Broker:** Redis
 
- **Email Testing:** Mailpit
  
- **API Docs:** Swagger
  
- **Containerization:** Docker
  
- **Monitoring:** Flower (for Celery)

---

## 🌟 Features

- User Registration & JWT Login with OTP Verification

- Add Next of Kin Information

- Create & Manage Bank Accounts

- Make Deposits, Withdrawals, Transfers Between Accounts

- Create Up to 3 Virtual Cards per User

- Top-Up Virtual Cards

- View All Transactions for a User

- Generate Transaction History as a PDF

- Interactive Swagger API Docs

- Email Notification via Mailpit

- Celery Task Monitoring with Flower

---

## 🚀 Getting Started

### 📦 Requirements

- [Docker](https://www.docker.com/)

- [Make](https://www.gnu.org/software/make/)

### 🛠 Run the Project

```
make build     # Build Docker containers
make up        # Start all services
make down      # Stop all services
````

---

## 📄 API Documentation

Swagger UI is available at:
**[http://localhost:8080/api/v1/schema/swagger-ui/](http://localhost:8080/api/v1/schema/swagger-ui/)**

---

## 📧 Email Testing

Use **Mailpit** to view email OTPs and other notifications:
**[http://localhost:8025](http://localhost:8025)**

---

## 📊 Celery Task Monitoring

Monitor background tasks via Flower:
**[http://localhost:5555](http://localhost:5555)**

---

## 🧪 Testing

You can test endpoints via Swagger or Postman using the JWT token and OTP flow. Payload examples are available in the GitHub repo.

---

## 📬 Contact

For any questions, feel free to raise an issue or contact me at my [email](shuklarishabh487@gmail.com).
