# NBA Data Analytics & Prediction App

A comprehensive NBA data collection, transformation, and analytics application built with Django, featuring automated data pipelines, predictive modeling, and RESTful API endpoints.

## 🏀 Overview

This project provides an end-to-end solution for collecting, transforming, and analyzing NBA statistics. It leverages the NBA API to gather real-time and historical data, processes it through dbt transformations, stores it in a MySQL database, and provides analytical insights through machine learning models.

## ✨ Features

- **Automated Data Collection**: Fetch NBA data including team stats, player stats, rosters, and game matchups
- **Data Transformation Pipeline**: dbt-based ETL pipeline for data staging and transformations
- **RESTful API**: Django Ninja-powered API endpoints for data access and operations
- **Predictive Modeling**: Machine learning models for game outcome predictions
- **Containerized Deployment**: Docker and Docker Compose setup for easy deployment
- **Database Management**: MySQL database with automated upsert operations

## 🏗️ Architecture

```
nba_app/
├── backend/
│   └── src/
│       ├── api/              # Django Ninja API endpoints
│       ├── app/              # Django app configuration
│       ├── services/         # Core business logic
│       │   ├── data_collection/    # NBA API data collection
│       │   ├── db/                 # Database operations
│       │   └── predictive_model/   # ML prediction models
│       └── pipeline_nba/     # dbt transformation pipeline
├── docker-compose.yml        # Multi-container orchestration
├── Dockerfile               # Application container definition
└── requirements.txt         # Python dependencies
```

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 4.2+ with Django Ninja
- **Language**: Python 3.9
- **Database**: MySQL 8.0
- **ORM**: SQLAlchemy, SQLModel, Django ORM

### Data Pipeline
- **ETL**: dbt (data build tool)
- **Data Processing**: Pandas, Polars
- **NBA API**: nba_api

### Machine Learning
- **Framework**: scikit-learn
- **Data Analysis**: Polars, Pandas

### DevOps
- **Containerization**: Docker, Docker Compose
- **Cloud**: AWS (boto3, s3fs)

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for local development)
- Git

## 🚀 Getting Started

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nba_app
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Build and start services**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - API: http://localhost:8000
   - MySQL: localhost:3307

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure database**
   - Ensure MySQL is running on port 3307
   - Update database credentials in settings

3. **Run migrations**
   ```bash
   cd backend/src
   python manage.py migrate
   ```

4. **Start development server**
   ```bash
   python manage.py runserver
   ```

## 📊 Data Models

### Core Tables
- **SeasonRecord**: NBA season information
- **TeamInfo**: Team details (name, city, founded year)
- **PlayerInfo**: Player biographical data
- **TeamRoster**: Team-player relationships
- **PlayerStats**: Player performance statistics
- **TeamStats**: Team performance metrics
- **TeamMatchups**: Head-to-head team statistics

## 🔌 API Endpoints

### Data Collection

**Collect All NBA Data**
```http
GET /api/nba/collect/all
```

**Collect Specific Table**
```http
GET /api/nba/collect/{table_name}
```

**Get Predictions**
```http
GET /api/nba/predictions/
```

**Get Team Matchup Data**
```http
GET /api/nba/team-matchups/
```

**Get Team Statistics**
```http
GET /api/nba/team-stats/
```

**Get Player Statistics**
```http
GET /api/nba/player-stats/
```

## 🔄 dbt Pipeline

The project includes a comprehensive dbt pipeline for data transformations:

### Staging Models
- `stg_nba_player_stats.sql`: Clean and stage player statistics
- `stg_nba_team_stats.sql`: Clean and stage team statistics
- `stg_nba_team_matchups.sql`: Clean and stage team matchup data

### Transformation Models
- `transformations_player_stats.sql`: Advanced player metrics
- `transformations_team_stats.sql`: Advanced team analytics
- `transformations_team_matchups.sql`: Head-to-head analysis

### Running dbt

```bash
cd backend/src/pipeline_nba

# Test connections
dbt debug

# Run all models
dbt run

# Test models
dbt test

# Generate documentation
dbt docs generate
dbt docs serve
```

## 🤖 Predictive Modeling

The application includes machine learning capabilities for:
- Game outcome predictions
- Team performance forecasting
- Player statistics projections

Models are trained on historical data and updated regularly through the data pipeline.

## 🗃️ Database Configuration

### MySQL Setup

The application uses MySQL with the following default configuration:

- **Host**: mysql-host (Docker) / localhost (local)
- **Port**: 3307
- **Database**: nba_test
- **User**: admin
- **Password**: admin

⚠️ **Note**: Change default credentials in production environments.

## 🐳 Docker Services

### nba_app_backend
- Django application server
- Exposed on port 8000
- Auto-reloads on code changes (via volume mount)

### mysql-host
- MySQL 8.0 database
- Exposed on port 3307
- Includes health checks

## 📁 Project Structure Details

### Services

**data_collection/**
- `collect.py`: NBA API data collection logic
- `build_data_service.py`: Data pipeline orchestration
- `transformer_helper.py`: Data transformation utilities
- `constants.py`: Configuration constants

**db/**
- `db_service.py`: Database operations and queries
- `models_upsert.py`: Bulk insert/update operations

**predictive_model/**
- `model.py`: ML model definitions
- `service.py`: Model training and inference
- `constants.py`: Model configuration

## 🧪 Testing

```bash
# Run Django tests
cd backend/src
python manage.py test

# Run dbt tests
cd pipeline_nba
dbt test
```

## 📝 Logging

Logs are stored in:
- `backend/src/logs/`: Application logs
- `backend/src/pipeline_nba/logs/`: dbt logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [nba_api](https://github.com/swar/nba_api) - NBA statistics API
- [dbt](https://www.getdbt.com/) - Data transformation framework
- [Django Ninja](https://django-ninja.rest-framework.com/) - Fast Django REST framework

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

Built with ❤️ for NBA analytics enthusiasts
