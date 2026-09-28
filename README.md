# Focus Tree Project

A mini life-schedule planner inspired by the focus tree mechanics from *Hearts of Iron IV*.  
This project helps you break your life goals into structured, interconnected objectives across different time horizons: yearly, monthly, weekly, and lifetime plans.

---

## 🎮 Overview

**Focus Tree Project** is a Flask-based web application that transforms personal goal planning into an interactive strategy game. Instead of a traditional to-do list, you organize your life goals as a "focus tree"—a branching network where each goal can unlock new opportunities.

### The Concept

In Hearts of Iron IV, a focus tree is a branching research tree where completing one focus unlocks related focuses. This project adapts that mechanic for **real life**: you create goals across multiple time horizons, set prerequisites, and unlock deeper objectives as you complete foundational work.

### What You Can Do

- 📋 **Create life goals** ("focuses") with descriptions, time estimates, and point values
- 🎯 **Organize by scope**: Yearly, Monthly, Weekly, or Lifetime planning horizons
- 🔗 **Set prerequisites**: Lock goals behind completed focuses to enforce a logical progression
- ✅ **Track progress**: Mark goals complete and watch your "political power" score accumulate
- 🎨 **Custom icons**: Choose from thousands of Hearts of Iron IV-inspired icons
- 📊 **Score tracking**: See your total earned vs. possible points per scope and overall
- 💾 **Local storage**: All data stored in SQLite—no cloud dependency, full privacy

---

## ✨ Features

### Core Features
- **Interactive Focus Tree UI**: Visual representation of your goals and their relationships
- **Dependency-based Progression**: Unlock goals by completing prerequisites
- **Multi-scope Planning**: Separate trees for different time horizons
- **Completion Tracking**: Mark goals done, undo completion, delete goals
- **Score System**: Earn points for completing goals; track progress as "political power"
- **Searchable Icon Library**: Browse and select from thousands of HOI4 icons

### Technical Features
- **Lightweight Architecture**: Minimal dependencies, fast startup
- **SQLite Database**: Local, embeddable, no server setup required
- **CSRF Protection**: Secure forms with Flask-WTF
- **Responsive Design**: Works on desktop and tablet
- **Icon Caching**: Downloaded icons cached locally for speed
- **Scope-based Organization**: Separate data per time horizon

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Backend** | Python, Flask |
| **Database** | SQLite |
| **Forms** | WTForms, Flask-WTF |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Web Scraping** | BeautifulSoup4 |
| **Icons** | Hearts of Iron IV GFX assets (via Yard1's HoI4-GFX-Search) |

---

## 📁 Project Structure

```
Focus_Tree_Project/
├── app.py                 # Main Flask application
├── db.py                  # Database initialization and queries
├── forms.py               # WTForms form definitions
├── scraper.py             # Icon scraper for HOI4 GFX catalog
├── requirements.txt       # Python dependencies
├── static/
│   ├── css/
│   │   └── app.css        # Application styles
│   └── js/
│       └── app.js         # Frontend interactivity
├── templates/
│   └── index.html         # Main page template
└── data/
    ├── focus_tree.db      # SQLite database (auto-created)
    └── icon_cache/        # Downloaded icon images (auto-created)
```

### Key Files Explained

- **app.py** (7KB): Flask routes for adding/completing/deleting focuses, icon API, and rendering
- **db.py** (6KB): SQLite schema, CRUD operations, and scoring logic
- **forms.py** (1.3KB): WTForms form for creating focuses with validation
- **scraper.py** (2.3KB): Scrapes HOI4 icons from Yard1's catalog and stores metadata
- **templates/index.html** (7.4KB): Single-page template with overlays for details and icon picker

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- `pip` (Python package manager)

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/daiwik2009/Focus_Tree_Project.git
   cd Focus_Tree_Project
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

6. **Access the app**:
   Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## 📖 How to Use

### Getting Started

1. **Choose a scope** using the sidebar (Yearly, Monthly, Weekly, or Lifetime)
2. **Add a focus** using the form at the bottom:
   - Enter a focus name (required)
   - Add a description (optional)
   - Set a time estimate (optional)
   - Assign points (default: 10, max: 9999)
   - Choose a prerequisite focus (optional—leave as "None" for root focuses)
   - Select an icon
3. **View your tree** in the main area
4. **Complete focuses** by clicking a focus node and clicking "Complete focus"
5. **Track progress** via the "Political Power" score in the top right

### Example: Building a Career Growth Tree

**Yearly Scope:**
- Get a promotion (root focus, 50 points)
  
**Monthly Scope (locked until yearly goal done):**
- Complete project A (prerequisite: Get a promotion, 20 points)
- Learn new skill (prerequisite: Get a promotion, 15 points)

**Weekly Scope:**
- Read documentation (prerequisite: Learn new skill, 5 points)
- Code review (prerequisite: Complete project A, 5 points)

As you complete each goal, you unlock the next tier and accumulate political power!

---

## 🎨 Icon System

### Powered by Hearts of Iron IV

The icon picker uses a curated library from **Yard1's HoI4-GFX-Search**, a comprehensive database of game graphics from Hearts of Iron IV. This adds visual richness and thematic consistency to your goal planning.

**Credit**: Icons sourced from [Yard1's HoI4-GFX-Search](https://yard1.github.io/HoI4-GFX-Search/)
- Original assets: Paradox Interactive's Hearts of Iron IV
- Icon catalog: [Yard1 GitHub](https://github.com/Yard1)
- Search site: https://yard1.github.io/HoI4-GFX-Search/

### How Icons Work

1. On first run, the app automatically scrapes available icon categories from the Yard1 catalog
2. Icons are stored in the local SQLite database with search metadata
3. Downloaded images are cached locally in `data/icon_cache/` for instant access
4. You can manually refresh the icon library via the "Rescrape icons" button

### Icon Categories

The HOI4 catalog includes dozens of categories:
- National focuses
- Economic policies
- Military doctrines
- Ideologies
- Technology trees
- And many more...

---

## 🗄️ Database Schema

### focuses table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| scope | TEXT | One of: yearly, monthly, weekly, lifetime |
| name | TEXT | Focus name (max 100 chars) |
| description | TEXT | Detailed description (max 800 chars) |
| completion_time | TEXT | Estimated time to complete |
| points | INTEGER | Reward points (1-9999) |
| icon | TEXT | URL/path to selected icon |
| parent_id | INTEGER | ID of prerequisite focus (foreign key) |
| completed | BOOLEAN | 0 = incomplete, 1 = complete |
| completed_at | TEXT | ISO 8601 timestamp of completion |
| created_at | TEXT | ISO 8601 timestamp of creation |

### icons table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Icon display name |
| category | TEXT | Category from HOI4 catalog |
| url | TEXT | Remote URL to icon image |
| search_text | TEXT | Searchable text metadata |

### Indexes
- `idx_focuses_scope` on focuses(scope)
- `idx_icons_category` on icons(category)
- `idx_icons_search` on icons(search_text)

---

## 🔧 Configuration

The app uses sensible defaults. To customize:

- **Secret key** (in `app.py`): Change `app.config["SECRET_KEY"]` for production use
- **Database path** (in `db.py`): Modify `DB_PATH` to store data elsewhere
- **Icon cache location** (in `app.py`): Edit `ICON_CACHE` path
- **Debug mode**: Change `app.run(debug=True)` to `debug=False` in production

---

## 📊 Scoring & Progress

### How Scoring Works

- Each focus has a **points** value (default: 10)
- Completing a focus adds its points to your earned total
- The app tracks earned vs. possible points per scope and overall
- This is displayed as "Political Power" (PP), mimicking HOI4's resource system

### Example
```
Yearly Scope:
- Goal A: 50 points (completed)
- Goal B: 30 points (incomplete)
- Goal C: 20 points (incomplete)

Progress: 50 / 100 PP
```

---

## 🎯 Use Cases

This app works great for:

- **Career Development**: Track skill-building, certifications, and promotions
- **Fitness Goals**: Build workout routines that progress from basics to advanced
- **Learning Projects**: Structure learning paths with prerequisites
- **Life Planning**: Organize yearly objectives, monthly campaigns, and weekly operations
- **Habit Building**: Create cascading habits (morning routine → exercise → healthy eating)
- **Game Development**: Track project milestones with dependencies
- **Academic Planning**: Organize coursework and research goals

---

## 🛠️ Development

### Adding a Feature

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes to relevant files (e.g., `app.py` for routes, `db.py` for database)
4. Test locally: `python app.py`
5. Commit: `git commit -m "Add feature X"`
6. Push: `git push origin feature/my-feature`
7. Open a pull request

### Running Tests

Currently, there are no automated tests. Consider adding pytest or unittest coverage for:
- Form validation
- Database operations
- Icon scraping
- Route behavior

---

## 🐛 Troubleshooting

### Icons not loading
- Check internet connection (icons are fetched from Yard1's catalog)
- Click "Rescrape icons" to refresh the database
- Verify icon cache folder exists: `data/icon_cache/`

### Database locked error
- Close other instances of the app
- Delete `data/focus_tree.db` to reset (⚠️ loses all data)
- Check file permissions on `data/` folder

### Flask port already in use
- Change port in `app.py`: `app.run(debug=True, port=5001)`
- Or kill the process using port 5000

### Form validation errors
- Ensure focus **name** is provided (required)
- Ensure **points** is a number between 1 and 9999
- Check that descriptions don't exceed 800 characters

---

## 📝 License

This project is currently distributed without a formal license. For open-source publication, consider adding:
- MIT License (permissive, widely used)
- GPL v3 (copyleft)
- Apache 2.0 (permissive with patent clause)

---

## 🙏 Credits & Acknowledgments

- **Hearts of Iron IV**: Paradox Interactive (original game and graphics)
- **Icon Catalog**: [Yard1's HoI4-GFX-Search](https://yard1.github.io/HoI4-GFX-Search/) – Thank you for maintaining this incredible resource!
- **Framework**: Flask, WTForms, BeautifulSoup
- **Inspiration**: Focus tree mechanics from Hearts of Iron IV

---

## 🌐 Links

- **Repository**: https://github.com/daiwik2009/Focus_Tree_Project
- **Icon Library**: https://yard1.github.io/HoI4-GFX-Search/
- **Yard1 GitHub**: https://github.com/Yard1
- **Hearts of Iron IV**: https://www.paradoxinteractive.com/games/hearts-of-iron-iv

---

## 💡 Future Ideas

Potential improvements and features:

- [ ] Dark theme toggle
- [ ] Export/import focus trees as JSON
- [ ] Statistics dashboard (time spent, completion rate trends)
- [ ] Collaborative focus trees (share with friends)
- [ ] Mobile app version
- [ ] Custom icon uploads
- [ ] Focus templates for common goals
- [ ] Reminders and notifications
- [ ] Achievement system
- [ ] Focus notes and journals

---

**Made with ❤️ for strategic life planning**
