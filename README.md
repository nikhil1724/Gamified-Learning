# 🎮 Gamified Learning Platform

A comprehensive digital learning platform that combines education with gamification elements to create an engaging and interactive learning experience. This platform features adaptive learning, skill trees, coding challenges, rewards, and more.

## ✨ Features

### For Students
- 📚 **Interactive Courses** - Learn through structured lessons with markdown-based content
- 💻 **Code Playground** - Practice coding with integrated Monaco editor
- 🧩 **Coding Challenges** - Solve programming problems to earn XP and badges
- 📝 **Quizzes** - Test your knowledge with interactive quizzes
- 🌳 **Skill Tree** - Visualize your learning progress through an interactive skill tree
- 🏆 **Rewards & Badges** - Earn achievements and unlock rewards
- 📊 **Analytics Dashboard** - Track your progress with detailed charts and statistics
- 🎯 **Daily Challenges** - Complete daily tasks to maintain your learning streak
- 🤖 **AI Tutor** - Get help with floating tutor assistance
- 📋 **Leaderboard** - Compete with other learners
- 🔔 **Notifications** - Stay updated with real-time notifications

### For Teachers/Instructors
- 👥 **Student Management** - Monitor student progress and performance
- 📖 **Course Creation** - Create and manage course content
- ✍️ **Problem Management** - Design coding challenges with test cases
- 📊 **Analytics** - View detailed analytics for your students
- 🎓 **Course Administration** - Manage enrollments and track completion

### For Admins
- 👨‍💼 **User Management** - Manage students, teachers, and admins
- 📚 **Content Management** - Oversee all courses and lessons
- 🔧 **System Configuration** - Configure platform settings
- 📈 **Platform Analytics** - Monitor overall platform performance

## 🛠️ Tech Stack

### Backend
- **Framework:** Flask 3.0.2
- **Database:** SQLAlchemy with MySQL
- **Authentication:** JWT (Flask-JWT-Extended)
- **API:** RESTful API with CORS support
- **Server:** Gunicorn for production

### Frontend
- **Framework:** React 18.2.0
- **Routing:** React Router DOM v6
- **UI Components:** Bootstrap 5.3.3
- **Code Editor:** Monaco Editor
- **Charts:** Recharts
- **Animations:** Framer Motion
- **Markdown:** React Markdown with syntax highlighting
- **State Management:** Context API

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 16.x or higher
- MySQL 8.0 or higher
- npm or yarn

## 🚀 Installation & Setup

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables:**
   - Create a `.env` file in the backend directory
   - Copy from `.env.example` (if available) or add:
     ```env
     FLASK_APP=app.py
     FLASK_ENV=development
     SECRET_KEY=your-secret-key-here
     JWT_SECRET_KEY=your-jwt-secret-key-here
     DATABASE_URL=mysql+pymysql://username:password@localhost/gamified_learning
     ```

6. **Initialize database:**
   ```bash
   python app.py
   ```
   The database will be created on first run.

7. **Seed initial data (optional):**
   ```bash
   python seed_data.py
   ```

8. **Run the backend server:**
   ```bash
   flask run
   # or
   python app.py
   ```
   Backend will run on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure API URL:**
   - Update `src/services/api.js` if backend is not running on `http://localhost:5000`

4. **Run the development server:**
   ```bash
   npm start
   ```
   Frontend will run on `http://localhost:3000`

5. **Build for production:**
   ```bash
   npm run build
   ```

## 📁 Project Structure

```
GAMIFIED_LEARNING/
├── backend/
│   ├── routes/              # API route handlers
│   ├── models.py            # Database models
│   ├── app.py              # Flask application entry point
│   ├── config.py           # Configuration settings
│   ├── database.py         # Database initialization
│   ├── adaptive_engine.py  # AI-powered learning engine
│   ├── seed_data.py        # Database seeding script
│   └── requirements.txt    # Python dependencies
│
├── frontend/
│   ├── public/
│   │   └── content/        # Course content (markdown files)
│   ├── src/
│   │   ├── components/     # Reusable React components
│   │   ├── pages/          # Page components
│   │   ├── context/        # React Context providers
│   │   ├── services/       # API service layer
│   │   ├── styles/         # CSS stylesheets
│   │   └── App.js          # Main application component
│   └── package.json        # Node.js dependencies
│
└── README.md
```

## 🎯 Usage

### Default Credentials (if seeded)
- **Admin:** admin@example.com
- **Teacher:** teacher@example.com
- **Student:** student@example.com
- Password: (check seed_data.py)

### Key Workflows

1. **Student Learning Path:**
   - Register/Login
   - Browse available courses
   - Enroll in courses
   - Complete lessons and quizzes
   - Solve coding challenges
   - Track progress on dashboard
   - Earn badges and rewards

2. **Teacher Management:**
   - Login as teacher
   - Create new courses
   - Add lessons and content
   - Create coding problems
   - Monitor student progress
   - View analytics

3. **Admin Operations:**
   - Manage users and roles
   - Configure platform settings
   - Monitor system analytics
   - Manage content and courses

## 🔑 Key Features in Detail

### Adaptive Learning Engine
The platform includes an adaptive learning engine that personalizes content recommendations based on:
- Student performance
- Learning pace
- Skill proficiency
- Problem-solving patterns

### Code Execution
Integrated code playground with:
- Syntax highlighting
- Multiple language support (Python, Java, etc.)
- Real-time code execution
- Test case validation

### Gamification Elements
- **XP System:** Earn experience points for activities
- **Leveling:** Progress through levels as you learn
- **Badges:** Unlock achievements for milestones
- **Streaks:** Maintain daily learning streaks
- **Leaderboards:** Compete with peers

## 🎨 Design System

The project includes a comprehensive design system with:
- Custom CSS variables for theming
- Reusable component styles
- Responsive design patterns
- Animation utilities

See `DESIGN_SYSTEM_USAGE.md` and `DESIGN_SYSTEM_CHEATSHEET.md` for details.

## 🐛 Debugging

For debugging guidance, see `DEBUG_CHECKLIST.md`.

## 📝 API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Course Endpoints
- `GET /api/courses` - Get all courses
- `GET /api/courses/:id` - Get course details
- `POST /api/courses/:id/enroll` - Enroll in course

### Problem Endpoints
- `GET /api/problems` - Get all problems
- `POST /api/problems/:id/submit` - Submit solution

(For complete API documentation, see individual route files in `backend/routes/`)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Built with React and Flask
- UI components inspired by modern design principles
- Gamification concepts from educational psychology research

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Happy Learning! 🚀**
