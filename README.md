# Trade Craft - Professional Trading Journal

A comprehensive, self-hosted trading journal and analytics platform built with Python Dash. Track your trades, analyze performance, and improve your trading strategy with detailed insights and visualizations.

## 🚀 Features

### Core Functionality
- **Multi-user Support**: Separate accounts and portfolios for different users
- **Comprehensive Trade Tracking**: Record trades with multiple legs, fees, and detailed notes
- **Advanced Analytics**: Performance metrics, risk analysis, and statistical insights
- **Interactive Charts**: Equity curves, drawdown analysis, and performance visualizations
- **Flexible Filtering**: Filter trades by date, symbol, tags, and custom criteria
- **Calendar View**: Visual overview of daily trading activity and performance

### Analytics & Insights
- **Performance Metrics**: Win rate, profit factor, Sharpe ratio, and more
- **Risk Analysis**: Maximum drawdown, Value at Risk (VaR), and risk-adjusted returns
- **Pattern Recognition**: Identify trading patterns by time, day of week, and market conditions
- **Symbol Analysis**: Performance breakdown by individual symbols and asset classes
- **Monthly Heatmaps**: Visual representation of monthly returns

### Technical Features
- **Modern Web Interface**: Responsive design built with Dash and Bootstrap
- **SQLite Database**: Lightweight, file-based database with full ACID compliance
- **Data Validation**: Comprehensive input validation and error handling
- **Export Capabilities**: Export trade data and analytics to CSV
- **Extensible Architecture**: Modular design for easy customization and feature additions

## 📋 Requirements

- Python 3.10+
- Modern web browser (Chrome, Firefox, Safari, Edge)

## 🛠️ Installation

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/tradecraft.git
   cd tradecraft
   ```

2. **Set up development environment**
   ```bash
   make setup-dev
   ```

3. **Run the application**
   ```bash
   make run
   ```

4. **Open your browser**
   Navigate to `http://localhost:8050`

### Manual Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

3. **Initialize database**
   ```bash
   python utils/db_init.py
   python utils/sample_data.py  # Optional: add sample data
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

## 🏗️ Architecture

### Project Structure
```
tradecraft/
├── app.py                 # Main application entry point
├── components/            # Reusable UI components
│   ├── charts.py         # Chart components
│   ├── filters.py        # Filter components
│   └── trade_form.py     # Trade entry forms
├── pages/                # Application pages
│   ├── analytics.py      # Analytics dashboard
│   ├── calendar.py       # Calendar view
│   ├── settings.py       # User settings
│   ├── trade_detail.py   # Individual trade details
│   └── trade_log.py      # Trade log table
├── utils/                # Utility modules
│   ├── analytics.py      # Advanced analytics functions
│   ├── config.py         # Configuration management
│   ├── db_access.py      # Database operations
│   ├── db_init.py        # Database initialization
│   ├── exceptions.py     # Custom exceptions
│   ├── filters.py        # Data filtering utilities
│   ├── sample_data.py    # Sample data generation
│   └── validation.py     # Input validation
├── tests/                # Test suite
├── data/                 # Database files
└── assets/               # Static assets (CSS, images)
```

### Database Schema
- **Users**: User accounts and authentication
- **Accounts**: Trading accounts per user (multiple accounts supported)
- **Trades**: Individual trade records with metadata
- **Trade Legs**: Individual buy/sell transactions within trades
- **Tags**: Categorization system for trades
- **Symbols**: Asset symbols and metadata

## 📊 Usage

### Adding Trades

1. Navigate to the **Trade Log** page
2. Click **Add Trade** button
3. Fill in trade details:
   - Market type (Stock, Option, Future, etc.)
   - Symbol
   - Notes and tags
4. Add trade legs:
   - Action (Buy/Sell)
   - Date and time
   - Quantity and price
   - Fees
5. Save the trade

### Viewing Analytics

1. Go to the **Analytics** page
2. Use filters to focus on specific:
   - Date ranges
   - Symbols
   - Tags
3. Review key metrics:
   - Win rate and profit factor
   - Risk-adjusted returns
   - Performance patterns
4. Analyze charts:
   - Equity curve
   - Drawdown analysis
   - Monthly performance heatmap

### Calendar View

1. Visit the **Calendar** page
2. View daily P&L and trade counts
3. Navigate between months
4. Review weekly summaries

## 🧪 Testing

Run the test suite:
```bash
make test
```

Run specific test categories:
```bash
pytest tests/test_db_access.py -v
pytest tests/test_validation.py -v
```

Generate coverage report:
```bash
pytest --cov=utils --cov-report=html
```

## 🔧 Development

### Code Quality

Format code:
```bash
make format
```

Run linting:
```bash
make lint
```

### Adding Features

1. **Database Changes**: Update schema in `utils/db_init.py`
2. **New Pages**: Add to `pages/` directory and register with Dash
3. **Components**: Create reusable components in `components/`
4. **Analytics**: Add new calculations to `utils/analytics.py`
5. **Tests**: Add corresponding tests in `tests/`

### Configuration

Edit `.env` file to customize:
- Database location
- Application settings
- Logging configuration
- External API keys (for future integrations)

## 🚀 Deployment

### Local Production

1. Set production configuration:
   ```bash
   export DEBUG=false
   export HOST=0.0.0.0
   export PORT=8050
   ```

2. Run with production settings:
   ```bash
   python app.py
   ```

### Docker (Future)

```bash
make docker-build
make docker-run
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run tests and linting: `make test lint`
5. Commit changes: `git commit -am 'Add feature'`
6. Push to branch: `git push origin feature-name`
7. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write comprehensive tests for new features
- Update documentation for API changes
- Use meaningful commit messages

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- **Issues**: Report bugs and request features via GitHub Issues
- **Discussions**: Join community discussions for questions and ideas
- **Documentation**: Check the wiki for detailed documentation

## 🗺️ Roadmap

### Upcoming Features
- [ ] Import from broker APIs (Interactive Brokers, TD Ameritrade)
- [ ] Advanced portfolio analytics
- [ ] Risk management tools
- [ ] Mobile-responsive improvements
- [ ] Real-time market data integration
- [ ] Automated trade journaling
- [ ] Performance benchmarking
- [ ] Export to popular formats (PDF reports, Excel)

### Long-term Goals
- [ ] Multi-broker support
- [ ] Social features (share strategies, compare performance)
- [ ] Machine learning insights
- [ ] Advanced backtesting capabilities
- [ ] API for third-party integrations

---

**Trade Craft** - Professional trading journal for serious traders. Built with ❤️ using Python and Dash.