# Portfolio Dashboard

A modern web-based dashboard for tracking, analyzing, and visualizing investment portfolios using Python and Streamlit. Designed by a programmer for programmers. The idea is to provide a specialized, yet generalized platform for independent stock investors. Users with some technical chops can use the embedded tools to specialize and personalize their own system to their hearts content. Go forth and fork!

---

## 📌 Features

- Portfolio tracking and performance analytics for individual investors
- Interactive visualizations with Plotly (planned)
- SQL database integration using SQLAlchemy and DuckDB
- Modular architecture with clear separation of concerns
- Docker support for easy deployment

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python (SQLAlchemy, DuckDB)
- **Data Fetching**: yfinance
- **Visualization**: Plotly
- **Dependency Management**: uv (via `pyproject.toml` and `uv.lock`)
- **Deployment**: Docker

---

## 📂 Project Structure

``` text
Portfolio-Dashboard/
├── src/
│   ├── core/                  # Core logic and utilities
│   ├── config/                # Configuration logic
│   ├── images/                # Static assets
│   ├── models/                # Database models and SQL scripts
│   ├── pages/                 # Individual dashboard pages
│   ├── utility/               # Helper functions
│   ├── app.py                 # Main entry point for the Streamlit app
│   └── ...
├── docker/                    # Docker configuration
├── tests/                     # Test files
└── README.md                  # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Docker (optional, for containerized deployment)
- UV (optional, for development)

### Installation (Docker)

This is the easiest installation if you just want to give it a try, or use it as is. I'm still working on the filesystem, so details of this installation will change from time to time.

1. Pull the Docker image from DockerHub:

   ```bash
   docker pull nomadmot/portfolio-dashboard:latest
   ```

2. Either download the compose.yaml file from the docker directory of the GitHub repository, or copy the following:

   ```yaml
   services:
   PortfolioDashboard:
      image: docker.io/nomadmot/portfolio-dashboard:latest
      environment:
         - DATABASE_URI=sqlite://///home/appuser/investorlab/DATA/portfolio.db
         - DUCK_PUDDLE=/home/appuser/investorlab/DUCK_PUDDLE
         - LOGLEVEL_APPLICATION=INFO
         - LOGLEVEL_STREAMLIT=WARN
         - LOGLEVEL_SQLALCHEMY=WARN
         - YFINANCE_DEBUG=FALSE
         - SQLALCHEMY_ECHO=FALSE
         - SQLALCHEMY_ECHO_POOL=FALSE
      ports:
         - target: 8080
         published: "8080"
         protocol: tcp
      volumes:
         - type: bind
         source: /path/to/your/data
         target: /home/appuser/investorlab
      ```

3. Run Docker Compose:

   ```bash
   docker compose up
   ```

### Installation (Github)

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/Portfolio-Dashboard.git
   cd Portfolio-Dashboard
   ```

2. **Set Up the Environment**

   - Install dependencies using:

     ```bash
     uv install
     ```

### Next Steps
# explain how to populate and use database
---

## 🚀 Roadmap

I'm continuously improving the Portfolio Dashboard based on community feedback and open issues. Below is a summary of the current priorities and planned features:

### Performance & Data Accuracy

- [#154] Fix performance summary not updating date range when daily balances are updated
- [#145] Correct the wrong day count for PERIODS.D30
- [#2] Adjust the performance algorithm to account for deposits

### User Experience & Interface

- [#148] Create an alerts page to view and filter application notifications

### New Features

- [#148] Integrate AI chat as a first step to full AI integration
- [#101] Create a Security Details page to provide information on selected stocks
- [#39] Develop a Watchlist page for tracking specific stocks or assets
- [#90] Introduce a Portfolio Journal for tracking transactions and notes
- [#43] Enable Obsidian integration for seamless note-taking and portfolio synchronization

### Core Functionality

- [#133] Refine the PERIODS logic for accurate time-based portfolio analysis
- [#57] Implement support for stock splits in portfolio calculations
- [#116] Implement a multiple account feature for easier portfolio management

### Other Planned Features

- Better integration with database (SQLAlchemy? DuckDB? Something else?)
- Automated upload of user transactions and other data
- UI for reviewing custom time series on plots (Time Machine)
- Backtesting
- Constant refactoring (I love refactoring)
- Testing suite for regression testing

---

## 📝 How You Can Help

If you’re interested in contributing to any of these features or fixes, check out the Contributing Guide below for detailed instructions on how to get started. I welcome contributions from everyone!

### How to Contribute

1. **Fork the Repository**

   - Click the "Fork" button on GitHub to create your own copy.

2. **Clone the Repository**

   - Clone your forked repository to your local machine and install as detailed above

     ```bash
     git clone https://github.com/your-username/Portfolio-Dashboard.git
     cd Portfolio-Dashboard
     ```

3. **Set Up the Environment**

   - Install dependencies using:

     ```bash
     uv install
     ```

4. **Create a Feature Branch**

   - Create and switch to a new branch:

     ```bash
     git checkout -b feature/your-feature-name
     ```

5. **Make Your Changes**

   - Implement your feature or fix. Ensure your changes align with the project’s coding standards.

6. **Write Tests**

   - Add tests in the `tests/` directory to ensure functionality.

7. **Commit Your Changes**

   - Commit your changes with a descriptive message:

     ```bash
     git add .
     git commit -m "Describe your changes here"
     ```

8. **Push Your Changes**

   - Push your changes to your forked repository:

     ```bash
     git push origin feature/your-feature-name
     ```

9. **Open a Pull Request**

   - Go to the original repository on GitHub and create a new pull request with a detailed description.

10. **Engage with Feedback**

    - Respond to any comments or suggestions from maintainers.

---

## 🤝 Code of Conduct

Please adhere to our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming and inclusive environment.

---

## 📢 Questions?

If you have any questions or need further assistance, feel free to open an issue or pull request
