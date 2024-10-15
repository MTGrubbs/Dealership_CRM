# Dealership CRM

This is a Customer Relationship Management (CRM) system designed for car dealerships. It helps manage deals, track sales performance, and provide insights into daily and monthly sales data.

## Features

- Dashboard with daily and monthly sales statistics
- Deal management (create, view, edit deals)
- User roles (managers and salespeople)
- Detailed deal views with modal popups

## Installation

1. Clone the repository
   ```
   git clone https://github.com/yourusername/dealership-crm.git
   cd dealership-crm
   ```

2. Create a virtual environment and activate it
   ```
   python -m venv crm_env
   source crm_env/bin/activate  # On Windows use `crm_env\Scripts\activate`
   ```

3. Install the required packages
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your environment variables:
   ```
   DJANGO_SECRET_KEY=your_secret_key_here
   DJANGO_DEBUG=True
   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
   ```

5. Run migrations
   ```
   python manage.py migrate
   ```

6. Create a superuser
   ```
   python manage.py createsuperuser
   ```

7. Run the development server
   ```
   python manage.py runserver
   ```

8. Visit `http://127.0.0.1:8000` in your browser

## Usage

[Add instructions on how to use your CRM system]

## Contributing

[Add instructions for how others can contribute to your project]

## License

[Add your chosen license here]