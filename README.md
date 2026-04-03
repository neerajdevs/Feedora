# 🚀 Feedora - Advanced Blogging Platform

Feedora is a modern, high-performance, and scalable blogging platform built with **Django** and **MongoDB**. Designed with a focus on system optimization and seamless user experience, it features in-memory caching, live AJAX search, secure OTP authentication, and dynamic DOM updates.

![Feedora Banner](https://via.placeholder.com/1000x400.png?text=Feedora+-+Explore+The+Future) 
*(Note: Apne project ka ek mast dark-theme screenshot le kar yahan link replace kar dena)*

## ✨ Key Technical Highlights

### 1. Advanced Authentication & Security
* **OTP Email Verification:** Custom user registration flow with secure time-bound OTP verification via email.
* **Environment Variables:** Strictly decoupled secret keys, database URIs, and email credentials using `.env` for production-grade security.

### 2. Performance Optimization (Redis & NoSQL)
* **MongoDB Architecture:** Leveraged MongoDB for flexible NoSQL data storage (Posts, Comments, Users).
* **In-Memory Caching (Redis):** Implemented Redis to cache the main feed, drastically reducing database read queries and cutting down page load times.
* **Optimized Session Management:** Handled user sessions securely using Redis memory instead of the default relational DB approach.

### 3. Seamless User Experience (AJAX & Vanilla JS)
* **Live Debounced Search:** Google-like live search dropdown that queries the database asynchronously with a 300ms debounce to prevent server overload.
* **Dynamic Content Loading:** Implemented "Load More" infinite scroll pagination using AJAX (fetching 5 posts per batch) to save memory and DOM clutter.
* **Real-time Interactions:** Users can add comments and like/dislike posts instantly using the `Fetch API`, updating the UI dynamically without full page reloads.

## 🛠️ Tech Stack

* **Backend:** Python, Django
* **Database:** MongoDB (via Djongo / PyMongo)
* **Cache & Sessions:** Redis
* **Frontend:** HTML5, Vanilla JavaScript, Tailwind CSS (Glassmorphism & Dark Mode)
* **Production Ready:** Gunicorn, WhiteNoise (for static file serving)

## 💻 Local Installation & Setup

Want to run Feedora on your local machine? Follow these steps:

**1. Clone the repository**
```bash
git clone [https://github.com/YourUsername/Feedora.git](https://github.com/YourUsername/Feedora.git)
cd Feedora