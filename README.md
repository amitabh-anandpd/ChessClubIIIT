# IIIT Hyderabad Chess Club Website

This is the official chess website for the IIIT Hyderabad Chess Club, designed specifically for IIIT Hyderabad students. The platform’s unique feature is its dynamic **leaderboard**, allowing students to compete, track their progress, and engage with the campus chess community.

## Features

- **Leaderboard:** Track player rankings and match results in real time.
- **User Accounts:** Secure login and profile management for IIIT Hyderabad students.
- **Tournaments:** Organize and participate in chess tournaments.
- **Live Matches:** Play chess games online with other students.
- **Newsletters:** Stay updated with club news and articles.

## Getting Started

Follow these steps to run the project locally on your PC.

### Prerequisites

- Python 3.8 or higher
- [Redis](https://redis.io/) server (for real-time features)
- (Optional) MySQL if you want to use it instead of SQLite

### Installation

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd ChessClubRepo
   ```

2. **Set up a virtual environment (recommended):**
   ```sh
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```sh
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Create a `.env` file in the root directory.
   - Add the following variables (example):
     ```
     DJANGO_KEY=your_django_secret_key
     REDIS_URL=redis://<user>:<password>@<host>:<port>
     DJANGO_SUPERUSER_USERNAME=admin
     DJANGO_SUPERUSER_EMAIL=admin@example.com
     DJANGO_SUPERUSER_PASSWORD=yourpassword
     ```
   - (Optional) Add MySQL credentials if using MySQL.

5. **Run the build script (Windows users can run the commands manually):**
   ```sh
   python manage.py makemigrations
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py createsuperuser  # If not using the .env variables
   ```

6. **Start the Redis server** (if not already running):
   - Make sure your `REDIS_URL` in `.env` matches your Redis instance.

7. **Run the development server:**
   ```sh
   python manage.py runserver
   ```

8. **Access the website:**
   - Open your browser and go to [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Notes

- For real-time features (like live matches), Redis must be running and accessible.
- The default database is SQLite, but you can switch to MySQL by updating the settings and `.env`.
- Static files are collected in the `staticfiles/` directory.
