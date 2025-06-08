# TradeCraft - Trading Journal Application

A comprehensive trading journal web application built with Dash/Plotly, designed to help traders track, analyze, and improve their trading performance.

## 🚀 Features

- **Dashboard**: Overview of trading performance with key metrics and visualizations
- **Trade Log**: Detailed trade entry and management system with filtering and search
- **Analytics**: Advanced charts and analysis tools for trading performance
- **Settings**: Application configuration and database management

## 🛠️ Technology Stack

- **Frontend**: Dash, Plotly, Bootstrap Components
- **Backend**: Python, Flask (via Dash)
- **Database**: SQLite
- **Analytics**: Pandas, NumPy
- **Styling**: Custom CSS with Bootstrap

## ⚡ Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd TradeCraft
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Initialize the database:**
```bash
python utils/init_db.py
```

4. **Load sample data (optional):**
```bash
python seed_sample_data.py
```

5. **Run the application:**
```bash
python app.py
```

6. **Open your browser** and navigate to `http://127.0.0.1:8050/`

## 📁 Project Structure

```
TradeCraft/
├── app.py                 # Main application entry point
├── models.py              # Database models and data structures
├── sample_data.py         # Sample trading data for testing
├── requirements.txt       # Python dependencies
├── seed_sample_data.py    # Script to load sample data
├── assets/
│   └── style.css         # Custom CSS styling
├── data/
│   ├── schema.sql        # Database schema
│   └── tradecraft.db     # SQLite database
├── pages/
│   ├── dashboard.py      # Dashboard page with metrics
│   ├── trades.py         # Trade log page
│   ├── analytics.py      # Analytics page with charts
│   └── settings.py       # Settings and configuration
└── utils/
    ├── db_utils.py       # Database utilities and CRUD operations
    ├── analytics.py      # Analytics calculation functions
    ├── init_db.py        # Database initialization script
    └── seed_db.py        # Database seeding functions
```

## 🎯 Key Features

### Dashboard
- **Performance Metrics**: Total P&L, win rate, average win/loss
- **Visual Charts**: Equity curve, monthly P&L breakdown
- **Quick Stats**: Recent trading activity and key statistics
- **Responsive Design**: Bootstrap-based responsive layout

### Trade Log
- **Trade Entry**: Add trades with multiple legs (options, stocks)
- **Filtering**: Filter by symbol, date range, status, tags
- **Management**: Edit, delete, and organize trades
- **Tags System**: Categorize trades with custom tags

### Analytics
- **Performance Analysis**: Detailed P&L analysis and trends
- **Risk Metrics**: Drawdown analysis and risk assessment
- **Visual Charts**: Interactive Plotly charts and graphs
- **Time-based Analysis**: Daily, weekly, monthly performance

### Settings
- **Database Management**: Backup, restore, clear data
- **Sample Data**: Load test data for demonstration
- **Configuration**: Customize application settings
- **Export/Import**: Data management tools

## 🏗️ Architecture

The application follows SOLID principles with a modular design:

- **Single Responsibility**: Each module has a focused purpose
- **Open/Closed**: Easy to extend with new features
- **Liskov Substitution**: Consistent interfaces throughout
- **Interface Segregation**: Minimal, focused interfaces
- **Dependency Inversion**: Abstractions over implementations

### Code Organization

- **Models**: Data structures and database schemas
- **Utils**: Reusable utility functions and database operations
- **Pages**: Individual page components with Dash layouts
- **Assets**: Static files (CSS, images)

## 🔧 Development

### Adding New Features

1. **Database Changes**: Update `models.py` and `schema.sql`
2. **Utilities**: Add functions to appropriate utils modules
3. **UI Components**: Create or modify page layouts
4. **Styling**: Update CSS in the assets folder

### Database Schema

The application uses SQLite with the following main tables:
- `users`: User account information
- `trades`: Main trade records
- `trade_legs`: Individual trade executions
- `tags`: Trade categorization system

## 📊 Sample Data

The application includes 1,300 sample trades covering:
- Various asset types (stocks, options)
- Different trade outcomes (wins, losses, open positions)
- Multiple time periods and symbols
- Realistic P&L scenarios

## 🚀 Production Deployment

For production deployment:

1. **Environment Variables**: Set up `.env` file with production settings
2. **Database**: Consider PostgreSQL for larger datasets
3. **Security**: Implement user authentication and authorization
4. **Performance**: Add caching and optimization
5. **Monitoring**: Set up logging and error tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow existing code patterns
4. Add appropriate documentation
5. Test thoroughly
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For questions, feature requests, or issues:
- Open an issue on GitHub
- Check the documentation
- Review the code examples

---

**TradeCraft** - Empowering traders with better insights and performance tracking.
