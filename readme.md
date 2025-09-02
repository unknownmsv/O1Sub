Advanced Subscription Manager

![Flask](https://img.shields.io/badge/Flask-2.3.x-lightgrey?style=for-the-badge&logo=flask)
![Python](https://img.shields.io/badge/Python-3.6%2B-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-Apache%202.0-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge)

A powerful, secure, and web-based subscription management platform built with Flask. This application provides a dual-layer architecture: a central admin panel for administrators to manage public resources and users, and a personalized user space for creating and managing private subscription configurations.

https://via.placeholder.com/800x400/2c3e50/ffffff?text=Advanced+Subscription+Manager+Dashboard (Screenshot of the Admin Dashboard)

✨ Key Features

🔐 Security & Administration

· Secure Admin Panel: Password-protected dashboard (/admin) for full system control.
· User Management: Create users, monitor data usage, and set custom request limits.
· Persistent Data Storage: All data is saved in JSON files, ensuring persistence across restarts.

🔗 Subscription Management

· Public Subscription Pools: Manage centralized subscription links categorized by type (e.g., Normal, Fragment).
· User-Created Subscriptions: A dedicated panel (/sub/make) for users to create personalized subscription links.
· Config Management: Users can add or remove individual server configurations (e.g., vless://...) via an intuitive interface.

📊 Monitoring & Performance

· Usage Analytics: Both admins and users can view detailed usage statistics. Admins have a system-wide view.
· Intelligent Caching: Fetched subscription links are cached to enhance performance and reduce redundant external requests.
· Real-time Stats: Monitor request counts and usage for any subscription in real-time.

🚀 Quick Start

Prerequisites

· Python 3.6 or higher
· pip (Python package manager)

Installation & Setup

1. Clone the Repository:
   ```bash
   git clone https://github.com/unknownmsv/O1Sub.git
   cd O1Sub
   ```
2. Install Dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Application:
   ```bash
   python app.py
   ```
   The application will be available at http://127.0.0.1:5000.
4. Initial Setup (Optional): The app auto-creates necessary JSON files. You can pre-configure them:
   · subscriptions.json: Pre-define categories {"normal": [], "fullnormal": [], "fragment": []}
   · users.json: Start with an empty object {}
   · custom_subs.json: Start with an empty object {}

📖 Usage Guide

For Administrators

1. Navigate to http://127.0.0.1:5000/admin.
2. Log in using the default password: Aa@14041404.
3. Security Notice: It is critical to change the default password in the app.py file before deployment.
4. From the admin dashboard, you can:
   · Add or remove public subscription links to different pools.
   · Create new users and set their individual request limits (use -1 for unlimited).
   · Monitor data usage across all users and public subscriptions.

For Users

1. Create a Custom Subscription:
   · Go to http://127.0.0.1:5000/sub/make.
   · Enter a unique name for your subscription and click "Create & Manage".
2. Manage Your Subscription:
   · You will be redirected to your personal panel (/sub/make/<your-sub-name>).
   · Here you can find your unique subscription URL.
   · Add new configurations by pasting links into the text area.
   · Delete existing configurations and monitor your request count.
3. Accessing Subscriptions:
   · Public Links: /sub/<type>?name=<username> (e.g., /sub/normal?name=john)
   · Custom Links: /sub/custom/<sub-name> (e.g., /sub/custom/my-sub)

📂 Project Structure

```
advanced-subscription-manager/
│
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
│
├── subscriptions.json     # Stores public subscription links
├── users.json             # Stores user data (usage, limits)
├── custom_subs.json       # Stores user-created subscriptions and configs
│
└── templates/             # HTML Templates
    ├── login.html         # Admin login page
    ├── admin.html         # Admin management panel
    ├── user_panel.html    # User's personal subscription panel
    └── make_sub.html      # Page to create a new custom subscription
```

🔧 Configuration

Key configuration settings can be modified directly in app.py:

· SECRET_KEY: Change for production deployments.
· HOST and PORT: Adjust binding address and port.
· ADMIN_PASSWORD: The default admin password. CHANGE THIS IN PRODUCTION.

📜 License

This project is licensed under the MIT License. See the LICENSE file for details.

🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

---

Happy Managing! For questions or support, please open an issue on the repository.
