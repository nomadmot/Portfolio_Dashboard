## [0.2.3] - 2026-08-23

### 🐛 Bug Fixes

- Fix add to current directory
- Fixed copy of configuration files in docker build

### 💼 Other

- Ignore VSCode workspace file
- New start balance
- Git ignore test_daily_balances.csv
- New script to load test balances from test generation script
- Display version and environment on startup; only display Borg button in DEV environment
- Remove duck puddle data path from settings, changr database uri in settings to database catalog, use database catalog to determine duck puddle data path
- Set environment to "PROD" for release
- Update README and screenshots
- Remove unneccesary DUCK_PUDDLE setting
- Set the max and min dates based on current daily balance file contents - Fixes #183
- Merge pull request #184 from nomadmot/183-bug-cannot-advance-date-in-performance-summary-after-adding-new-balance

183 bug cannot advance date in performance summary after adding new balance
- Correct database settings
- Correct database catalog filename
- Ignore workspace files
- Always add tag name when referencing image
- Opencode notes
- Don't use docker compose
- Delete unused tests
- Don't use ducklake, use single duckdb file (---.db) instead; move market_holidays table into db file
- Update version and description
- Renamed to CHANGELOG.md
- Add AGENTS.md and ANALYSIS.md to gitignore
- Nevermind: don't ignore AGENTS.md and ANALYSIS.db
- Changed setting DATABASE_CATALOG to DATABASE_FILE
- Remove unused file
- Remove sqlalchemy settings, add setting for watchlist folder
- Add setting for watchlist folder
- Merge pull request #186 from nomadmot/185-dont-use-ducklake

fix# 185 - dont use ducklake
- Correct names for docker image mount points
- Change db name from test to prod in docker image
- Use prod database insead of test database
- Update documentation
- Update version to 0.2.3
## [0.2.2] - 2026-08-14

### 🐛 Bug Fixes

- Fix _loggerlogger stutter
- Fix date calculations fot YTD and YR1

### 💼 Other

- Uppdate __version__.py
- Update __version__.py
- Ignore opencode.json
- OpenCode AGENTS.md
- WIP: changes as suggested by AI
- WIP: cleaned up errors
- Use emoji icons instead of fontawesome classes
- Do not set state for widget after widget is instantiated, fix icons for forward/back buttons, do not change period selected to "CUS" when using forward/back buttons
- Refarkle time_machine_component to always maintain number of trading days (eg always 30 trading days for period D30)
- Use underscores to mark callback functions as private
- Conform increment and decrement callback functions to existing standards
- Delete commented code
- Add setter/getter and callback functions for days_increment input field
- Increment_days widget now updates the rest of the component properly
- Add new functions get_market_days_for_period calculate_begin_date count_trading_days to market_calendar.py
- Use public functions instead of deprecated private functions
- Move function get_market_days_for_period from utility/market.py to utility/periods.py
- Move import for ,get_market_days_for_period for easier reading
- Use slider instead of standard numeric input, cosmetic changes
- Delete unused (commented) code
- Configure maximum days increment/decrement for time_machine_component
- Merge pull request #168 from nomadmot/161-enhancement-add-buttons-to-slide-dates-forward-and-backward-in-time-machine-component

161 enhancement add buttons to slide dates forward and backward in time machine component
- Add database info to systeminfo, cosmetic changes
- Merge pull request #170 from nomadmot/169-show-database-info

add database info to systeminfo, cosmetic changes
- Additional notes for OpenCode agents
- Remove examle files from docker container
- Use uv sync to install python environment; do not install dev tools
- AI generated initial test script
- Clarify agent instructions for using python environment
- Delete unneeded shell script, improve instructions in AGENTS.md
- Replace field validator for LogLevelEnum, provide option to configure yaml configuration file with environment variable
- Add pytest configuration
- Can't reload Settings
- Remove unused imports,  linting
- Use proper testing techniques
- Convert to standard pytest patterns
- New test for utility/market/calendar.py
- Move the src/tests folder to the project root
- Move pytest and watchdog to "test" dependency group
- Add pythonpath to include src/ directory when testing
- Start over
- Move tests/ directory from src/ to project root
- Move pytest and watchdog to optional-dependencies
- Updated environment setup details
- Merge pull request #177 from nomadmot/171-enhancement-create-a-test-suite

171 enhancement create a test suite
- Remove SQLite3 from install, use uv sync instead if pip install
- New .env file for docker install
- New script for docker install
- Update AGENTS.md for new models
- Ignore .venv
- Add new get_first_balance_date and get_first_trade_date functions
- Add new calculate_end_date function in market_calendar.py
- Add min and max dates for date sliding functions
- Use balance file begin and end dates as min and max dates for time machine control
- Import calculate_end_date
- Maintain begin and end dates based on selected period when dates are slid
- Corrected tests folder location
- Allow get_stock_history to accept either an ENUM or corresponding STRING value
- Add mocks for DuckDB exceptions to avoid calling real database
- Store status messages in session state so they are available everywhere
- Initialize a status message component for the session using the client IP address as a key
- Use the status message component initialized in app for all status message updates
- Merge pull request #181 from nomadmot/179-enable-status-toasts-in-utility-components

179 enable status toasts in utility components
- Closes #176

mve "debug section to top level
- Update with all valid options
- Automatically adjust UI options for development/production based on __version__.py
- Merge pull request #182 from nomadmot/180-enhancement-enable-style-choices-for-widgets

180 enhancement enable style choices for widgets
- Remove accidental newline character
- Merge pull request #167 from nomadmot/chaotic-chipmunk

Chaotic Chipmunk release
- Change environment from DEV to PROD
- Unignore .env
- Update Streamlit config.toml to include all possible settings
- Add src/.settings/.env to gitignore
- Production .env file for Docker build
- Move Streamlit config.toml to .streamlit directory
- Expose default port 8501, removed unneeded lines
- Removed unneeded env-file option, publish default port 8501
- Remove extraneous comment
## [0.2.1a] - 2026-06-02

### 💼 Other

- Merge branch 'main' of https://github.com/nomadmot/Portfolio-Dashboard
- Remove sqlalchemy as dependency
- Update DuckDB version to 1.5.2
- Add new CHANGELOG file
- Use duckdb exceptions instead of sqlalchemy exceptions
- Delete unused scripts
- Update configurations to use duckdb instead of sqlalchemy
- Set duckdb OVERRIDE_DATA_PATH to true for case where duckdb database has moved to a location other than where it was originally created (e.g. mounted in Docker)
- Delete logic for sqlalcheny logging
## [0.2.1] - 2026-06-01

### 🐛 Bug Fixes

- Fixed formatting
- Fix ducklake connection logic, refactor imports
- Fix lookup_associated_symbols logic, clean up comments
- Fix ducklake connection logic, refactor imports
- Fix lookup_associated_symbols logic, clean up comments

### 💼 Other

- Merge branch 'main' of https://github.com/nomadmot/Portfolio-Dashboard
- Add screenshots to README
- Update screenshots
- Add cliff.toml to gitignore
- Version 0.2.1 DEVELOPMENT
- Rename src/models folder as src/schemas
- Convert the database scema to Pydantic in preparation for move to DuckDB
- Convert to use DuckDB instead of SQLAlchemy
- Export DATABASE_CONNECTION instead of DATABASE_ENGINE for DuckDB
- Split enumerations from Pydantic classes, export all classes from __init__.py
- Update to use the ducklake extension
- WIP: refactor to use DuckDB
- Move "tests" directory into 'src' directory
- Add pytest to project dependencies
- Delete unneeded file
- Use relative imports for __init__.py
- Moved modules from core/ to utility/
- Removed unneccesary db connection, renamed logger as _logger
- Replaced missing get_last_trade_date function
- New test suite for query_portfolio module
- Delete accidental copy
- Script to generate portfolio balance test data
- Add logging, rename database
- Version 0.2.1 DEVELOPMENT
- Version 0.2.1 DEVELOPMENT
- Merge branch 'cranky-crocodile' of https://github.com/nomadmot/Portfolio-Dashboard into cranky-crocodile
- Rename src/models folder as src/schemas
- Convert the database scema to Pydantic in preparation for move to DuckDB
- Convert to use DuckDB instead of SQLAlchemy
- Export DATABASE_CONNECTION instead of DATABASE_ENGINE for DuckDB
- Split enumerations from Pydantic classes, export all classes from __init__.py
- Update to use the ducklake extension
- WIP: refactor to use DuckDB
- Move "tests" directory into 'src' directory
- Add pytest to project dependencies
- Delete unneeded file
- Use relative imports for __init__.py
- Moved modules from core/ to utility/
- Removed unneccesary db connection, renamed logger as _logger
- Replaced missing get_last_trade_date function
- New test suite for query_portfolio module
- Delete accidental copy
- Merge pull request #159 from nomadmot/158-enhancement-refactor-database-handling

158 enhancement refactor database handling
- Script to generate portfolio balance test data
- Add logging, rename database
- Merge branch 'cranky-crocodile' of https://github.com/nomadmot/Portfolio-Dashboard into cranky-crocodile
- Added optional end date; removed accidental space in file name
- Remove deprecated script
- Remove old (commented) version of balance management function, linting
- Check if database result is not None before extracting results, remove commented code
- Delete accidentally tracked HOLD file
- Add get_last_balance_date method to query_portfoli.py
- When present, use input from_date and to_date for date calculations in get_period_dates method
- Add optional end date for TimeMachineComponent creation
- Use new get_last_balance_date method in query_portfolio.py to set initial end date in TimeMachineComponent
- Merge pull request #162 from nomadmot/nomadmot/issue154

Nomadmot/issue154 is closed separately -- this merge fixes related issue #133
- Removed placeholder and default value from daily balance amount input field, added user notifications if input date or amount is missing
- Merge pull request #163 from nomadmot/160-remove-new-balance-default

removed placeholder and default value from daily balance amount input…
- Update screen shots
- Delete SQLite from system descriptions, update Roadmap
- Update environment for production release
- Ignore cliff.toml
- Merge pull request #153 from nomadmot/cranky-crocodile

Refactor for DuckDB, fix problems in performance summary and Time Machine date calculations

### 🚜 Refactor

- Refactored imports, add '_' to local-only variables
- Refactored imports, add '_' to front of local-only variables
- Refactored imports, rename logger as _logger
- Refactored imports, add '_' to local-only variables
- Refactored imports, add '_' to front of local-only variables
- Refactored imports, rename logger as _logger
## [0.2.0-alpha] - 2026-04-08

### 🐛 Bug Fixes

- Fix pylance unable to resolve local imports
- Fix Dockerfile to use "src" folder
- Fixed type assignment warnings for 'date' column
- Fixed mapping error for DailyBalance "date" field
- Fixed linting problems
- Fix linting problems
- Fixed formatting issue
- Fixed formatting error
- Fixes Use ORM for database queries
Fixes #18
- Fix key error in get_trades when returned dataframe is empty
- Fix key error in get_trades when returned dataframe is empty
- Fixed misplaced comma
- Fix hovertamplate syntax; adjust clickmode and dragmode in figure, remove pan/zoom, etc buttons in plotly modebar
- Fixed format string for customdata in dly_pct_change hovertemplate
- Fixed percent calculations; rearranged grand totals for logical order
- Fix summary unrealized p/l when current position is short
- Fixes #143
- Fixedd/clarified installation instructions
- Fix instructions for github install

### 💼 Other

- Initial commit
- Moving on.....
- Add watchdog to dependencies
- Ignore pycache files
- Moving on.....
- Merge branch 'main' of https://github.com/nomadmot/Portfolio-Dashboard
- Remove extraneous bytecode file
- Remove "practice" files
- Added __init__.py files to top-level and all sub-folders
- Vscode debug launch configuration
- Routines to read tables in the portfolio database
- Configuration and initialization of global variables
- Sqlalchemy definition of portfolio database
- Renamed as portfolio.py and moved to models folder
- First (sort of) working code
- Vscode debug launch configuration
- Ignore vscode launch.json
- Merge branch 'main' of https://github.com/nomadmot/Portfolio-Dashboard
- Merge branch 'main' of https://github.com/nomadmot/Portfolio-Dashboard
- Remove unused file
- Added log level and server sections
- Remove the title at the top of the page
- Adjust appearance
- Ignore .DS_Store everywhere
- Delete unused files
- Stock bull icon/logo
- Ignore stock-bull icon in images folder
- Add stock bull icon
- Delete unused pages
- Move source code to Portfolio-Dashboard subfolder
- Delete unused file
- Move source code to Portfolio-Dashboard subfolder
- Move to Portfolio-Dashboard subfolder
- Ignore app log file
- Format log entries
- Add cwd configuration to used source code subfolder Portfolio-Dashboard
- Add note to indicate looger level setting is overidden in app code
- Configure and initialize loggers for streamlit and sqlalchemy
- Shell script to run the application
- Use loglevel settings from standard logging module
- Adapt to use in this context: use logger, raise exceptions, etc.
- Delete unused code
- Rename manage_daily_balances.py in utility folder to manage_portfolio_balances to avoid confusion
- Update required streamlit version to 1.48.1... enables advanced layout
- Update to latest version of multiple packages
- Add docker build for app
- New page to manage daily_balances table in portfolio database
- Add page configuration
- Use todasys date for update date default, refine layout
- Rename utility module to data and organize import thru __init__.py
- Add Periods enumeration for selection of periods
- Capitalize "YTD" fir display value
- Add end_date parameter to get_stock_history function
- Use period instead of # days or begin date as input to  get_balance_history, much linting
- Add option to select period, fix end_date bug for comparison index data
- Get_balance_history returns all dates if input period is None
- Add initialization script to configure Docker container
- Application runtime configuration files and scripts are now copied from docker/files directory
- Much linting
- Add select box and horizontal layout for selection of comparison symbol
- Rename Python source folder to "src"
- Rename Python source folder to "src"
- Merge branch 'main' of https://github.com/nomadmot/Portfolio-Dashboard
- Merge branch 'main' of https://github.com/nomadmot/Portfolio-Dashboard
- Handled possibility that widget values may be uninitialized
- Adjusted for new project layout, fixed deprecation warning
- Provided explicit conversion from Row object to mapped Account object
- Placeholder readme generated by AI
- Placeholder readme generated by AI
- Merge branch 'main' of https://github.com/nomadmot/Portfolio-Dashboard
- Do not rerun page after showing database update/delete success so success message is displayed
- Move stock data fetch routines and helpers to new "services" folder
- Rename src/data folder to "core"
- Linting: added class and function doc, broke up long strings, other misc
- Provided docs for all classes, fixed mapping for TradeType and SecurityType classes to use python native data types
- New test script for model/portfolio module
- Move Periods class definition to top of services/stock_data.py, adjusted module exports
- New script to test get_stock_history function in services/stock_portfolio.py
- Limit period selection to just a few choices
- Merge pull request #4 from nomadmot/development

Development
- Cleaned up Periods import in core/query_portfolio.py, added ascending parameter to get_balance_history function to specify sort
- Update get_balance_history call to include period and sort parameters
- Store current status message in session state for display after page rerun
- Ensure that surrent message is written to the proper container
- New utility componetnt StatusMessageComponent manages and displays status messages in a streamlit page
- Use StatusMessageComponent to manage display of status messages
- Addedd documentation for the ascending parameter in get_balance_history
- Merge pull request #5 from nomadmot:nomadmot/issue1

Nomadmot/issue1
- In the set_status_message method of StatusMessageComponent, call the status message function on the current interface to provide immediate feedback
- Enclose calls to StatusMessageComponent.set_status_message inside "with" block to provide context for message display
- Only use SatusMessageComponent for database success messages, otherwise use standard Streamlit message functions
- Add use case documentation to cover appropriate useage of StatusMessageComponent
- Merge pull request #7 from nomadmot:nomadmot/issue6

fixes display of status messages
- Merge branch 'development' of https://github.com/nomadmot/Portfolio-Dashboard into development
- Chnge name of class Periods in stock_data.py to YfPeriods to signify useage with YFinance
- Export class Periods at the module level
- Add new class Periods for use when selecting time periods
- Must match input period parameter against Period values
- Use core.Periods for time period selection instead of YFinance periods
- Raise an error if both days and begin date are set (illogical selection criteria)
- Set initial selection index fpr Period selection to 2 (50 daysw)
- Import Periods from core module, request daily balance history for PERIODS.ALL
- Must pass Period to get_balance_history as value
- Debug: __repr__ function for Security object needed 'f' prefix to specify f-string
- Merge pull request #10 from nomadmot:nomadmot/issue3

Add Periods to core
- Added get_periods and get_label as member functions in Periods class, deleted unused members
- Use new get_periods and get_label functions in period selectbox to format properly
- Pass Period as class, not string
- Use Period label in chart title
- Use Period value in chart title
- Merge branch 'nomadmot/issue11' of https://github.com/nomadmot/Portfolio-Dashboard into nomadmot/issue11
- Remove extraneous value property in chart title
- Changed misleading variable names and comments to reflect addition of user-selected comparison ticker
- Merge pull request #12 from nomadmot:nomadmot/issue11

pass Periods object instead of value through  functions
- Add configuration and initialization logic to enable YFinance debug mode
- Merge pull request #13 from nomadmot/nomadmot/issue8
- Delete extraneous comment
- Add image_id file from docker build to .gitignore
- Add push to DockerHub after build is complete, provide better feedback during build
- Provide better feedback
- Merge pull request #15 from nomadmot/nomadmot/issue14
- Merge pull request #16 from nomadmot/development
- Changed starting date for ytd data from 1/1 of the current year to 12/31 of the previous year
fixes issueAdjust starting date for ytd performance
Fixes #21
- Merge pull request #22 from nomadmot:nomadmot/issue21

adjust ytd starting date
- Merge pull request #23 from nomadmot/development

Development
- Calculate performance for each day rather tha accumulating previous days to eliminat rouinding error
fixes Rounding error on daily performance
Fixes #19
- Merge pull request #25 from nomadmot/nomadmot/issue19

fix rounding error on daily performance
- Add subheader displaying total cumulative performance for period
fixes Performance for period
Fixes #20
- Merge pull request #26 from nomadmot:nomadmot/issue20

display total cumulative performance
- Add the daily balance to the voer tooltip
fixes Daily Balance tooltip
Fixes #9
- Formatting and efficiency tweaks
- Replace get_stock_history parameters (accidentally erased)
- Merge pull request #27 from nomadmot:nomadmot/issue9

daily balance in tooltip
- Merge pull request #28 from nomadmot/development

Daily performance chart enhancements
- Copilot generated code (needs debugging)
- New VS Code configuration to debug Streamlit applications
- Add working directory to configuration
- Merged balances and comparison tables to ensure valid valuse for all dates
- Merge pull request #31 from nomadmot/nomadmot/issue29

Nomadmot/issue29
- Reorganize page logic, add subheader displaying comparison ticker cumulative performance
- Merge pull request #32 from nomadmot/nomadmot/issue30

add summary line for comparison performance
- Merge pull request #33 from nomadmot/development

Development
- Add Detail Pe3rformance page to menu
- Add get_security symbols and get_trades to module
- Sort of works
- Add summary line displaying total gain/loss for all displayed transactions
- Add date selection
- Remove unused code, add documentation
- Create a layout container for the input fields
- Merge pull request #36 from nomadmot/nomadmot/issue35

Detail Performance page
- Added function to calculate daily performance over a series of daily balances
- Added daily percent change to plot as hidden line, include balance as customdata
- Merge pull request #40 from nomadmot/nomadmot/issue38

Nomadmot/issue38
- Added function to append associated options symbols into an input list of stock symbols
- Move "Include Options checkbox to top line. If box is checked, include associated options symbols in the displayed list.
- Merge pull request #48 from nomadmot:45-detail-performance-options

Include Options checkbox
- In progress
- Improved appearance of detail performance page
- Merge pull request #49 from nomadmot/47-detail-performance-formatting

prettify detail performance page
- Merge pull request #50 from nomadmot/cunning-monkey

Cunning monkey release
- Add sudo to image
- Add "Last trade Date' subhead under "Detail Performance Analysis" header on detail performance page, removed unused (commented) code
- Changed font for last trade date message
- Merge pull request #52 from nomadmot:51-show-last-transaction-date

last transaction date message
fixes #51
- Moved daily balance and percent change to top of hover box and added comparison percent chage to bottom
- Merge pull request #53 from nomadmot/nomadmot/issue42

reconfigured hover data on daily performance chart
- Increase width of inputs box on daily performance page
- Added date filter logic to get_trades function
- Use period selection input instead of begin and end dates
- Merge branch '54-period-selection-in-detail-performance-page' of https://github.com/nomadmot/Portfolio-Dashboard into 54-period-selection-in-detail-performance-page
- Merge pull request #55 from nomadmot/54-period-selection-in-detail-performance-page

54 period selection in detail performance page
- Add get_basic_quote function using yfinance to fetch current stock information
- Added current market value based on current holdings and current market price
- Merge pull request #56 from nomadmot/46-unrealized-gains

interim unrealized earnings code for Detail Performance page - requires further study
- Use DATABASE_URI environmenbt variable to specify database file for connection
fixes #34
- Use DATABASE_URI environmenbt variable to specify database file for connection
fixes #34
- Merge branch '34-environment-configuration' of https://github.com/nomadmot/Portfolio-Dashboard into 34-environment-configuration
- Merge pull request #61 from nomadmot/34-environment-configuration

34 environment configuration
- Set current amounts to zero if trades dataframe is emoty
fixes #59
- Merge pull request #62 from nomadmot/59-exception-when-selected-transactions-is-empty

set current amounts to zero if trades dataframe is emoty
- Use Docker Compose to install application
- Log "Starting Application" message as info instead of debug
- Remove unneeded production override of config.py for docker build
- Configure database and logging with environment variables
- Removed unnecesary comments
- Merge pull request #66 from nomadmot/65-docker-compose

close issue #65 docker compose
- Merge branch 'brutal-moose' into 17-minimize-db-open-interval
- Dispose SQLAlchemy database engine after every page
- Merge pull request #70 from nomadmot/17-minimize-db-open-interval

minimize db open interval
- Merge pull request #71 from nomadmot/brutal-moose

Brutal moose
- Don't round total trade amount
- Switch sign of tracde amount so buy is credit (as it should be)
- Switch sign of trade amount when calculating market value so buy/sell is accounted properly
- Merge pull request #74 from nomadmot/60-performance-detail-amounts

fixes #60 performance detail amounts
- Add debug logging, use previous close as current price if current price is zero
- Add debug logging, use previous close as current price if current price is zero
- Merge branch '46-unrealized-gains' of https://github.com/nomadmot/Portfolio-Dashboard into 46-unrealized-gains
- Ffixt lint: line too long
- LINT: capitalize variables in global scope
- Added columns to total cost and realized profit/loss, cleaned up calculations, much other stuff
- Add debug logging, use integer index to fix type warnings
- Merge pull request #76 from nomadmot/46-unrealized-gains

46 unrealized gains
- Expand overall width of detail performance table to 1000 px, expand width of symbol column to 150 px
- Merge pull request #77 from nomadmot/72-widen-symbol-column-on-detail-performance-page

expand width of detail performance table
- Added block at top of page displaying samounts for current day; split hovertemplate string to avoid 'line too long' warning
- Merge pull request #78 from nomadmot/64-as-of-date-on-daily-performance-page

64-as-of-date-on-daily-performance-page
- Merge pull request #79 from nomadmot/73-freeze-charts

ignore drag events on performance chart
- Add environment variables to debug settings
- Group selected trades by symbol and process each group independently
- Use itertuples for traversing data to avoid type warning
- Delete unneeded comments from experiments
- Display summary and total information  for realized and unrealized p/l
- Merge pull request #81 from nomadmot:80-multiple-symbols-in-detail-performance-page

enable multiple symbols in trade analysis
- Merge pull request #75 from nomadmot/demented-weasel

Demented weasel release
- Sum contents of "Realized P/L"  column for summary
- Merge pull request #87 from nomadmot/84-performance-detail-ux

fix "Realized P/L" summary
- Move stock_data.py to core module, delete services module
- Add unrealized p/l to deatil and summary tables, correct calculations
- Routines to test functions in stock_info module
- Add get_security_info to return Security dataclass for a single symbol from the database
- Move get_stock_history function to core module
- For options, multiply quantity by 100 when calculating market value; add column for current market value in summary table
- Merge pull request #88 from nomadmot/85-add-unearned-pl-column

issue 85 add unearned pl column
- New shell script to export environment variqbles from  .env file
- Use .env file to set environment variables
- Use load-env.sh to export .env variables
- Add a constant for the symbol selection widget on the Detail Performance page
- Add declaration for autoupdate_multiselect_component
- Multiselect component that automatically updates the current options and selections for immediate user feedback
- Use the new auto-update multiselect component to select stock and option sxymbols
- Merge pull request #91 from nomadmot/84-performance-detail-ux

fixes #84 performance detail ux
- Move SYMBOL_MULTISELECT_KEY from config.py to detail_performance.py
- Do not send an empty dataframe to analyze_trades
- Merge pull request #92 from nomadmot/89-balance-botched

89 balance botched
- Merge pull request #93 from nomadmot/dw-fix-1

Dw fix 1
- New compose file for osx envirnoment
- Remove "test" from container description
- Force user inputs to upper case, add paramters to accept placeholder and allow addition of new options
- For multiselect component, set placeholder text and enable addition of new options
- Merge pull request #96 from nomadmot/94-detail-performance-symbols

94 detail performance symbols
- Work in progress
- Work in progress
- Merge branch 'FEATURE--stock-journal' of https://github.com/nomadmot/Portfolio-Dashboard into FEATURE--stock-journal
- Add logging
- Added method to crfeate new Obsidian note
- Added debug configuration to launch the current python file
- Moved tests folder out of src folder to project root
- Moved test reoutines from obsidian.py to tests/test-obsidian.py; added optional  parameter "content" in new_obsidian_file function to provide initial content for the new file
- Added test for new obsidian file creation
- Add '&' before content string in file creation url
- Merge pull request #98 from nomadmot/43-enable-obsidian

43 enable obsidian
- Accept a list of stock symbol strings as a query parameter to display details the associated transactions
- Merge pull request #100 from nomadmot/99-url-select-detail-performance-symbol

99 url select detail performance symbol
- Print environment variables as they are loaded
- Use python logging instead of streamlit logging
- Added configuration option for the Streamlit log
- Removed trailing whitespace
- Use python logger
- Merge pull request #102 from nomadmot/67-sqlalchemy-logging

fix logging
- Work in progress
- Refarkled trade analysis logic for long positions, removed global total variables, added grand_total_invested to page, much else
- Add FFTY to list of comparison symbols
- Adapted analysis logic to account for short trades
- Sort buy transactions in front of sales if they occur un the same day
- Deleted needless yfinance lookup; short position does not affect total invested; display Zero instead of NaN when market value is zero
- Enhance comments
- More comment enhancement
- Add grand totals for current basis, current market value and pct realized/unrealized  pl
- Maintain total_invested as running total of all buy transactions
- Do not allow addition of non-existen symbols; do not print totals for empty trade summary
- Don 't look up current price for summary when ther are no current holdings; various fixes and enhancements for trade analysis
- Merge pull request #103 from nomadmot/95-pl-percent-in-detail-performance

closes #95
- Add ASSIGN to TradeType for option assignment transaction
- New tool for running SQLAlchemy operations on the portfolio datqabase
- Add portfolio db connections for SQLTools
- Replace use_container_width with width='content' per deprecation warning
- SQL to fix missing option assignment transaction
- Replace use_container_width with width='content' per deprecation warning
- Merge branch '104-option-assignment' of https://github.com/nomadmot/Portfolio-Dashboard into 104-option-assignment
- Merge pull request #105 from nomadmot/104-option-assignment

104 option assignment
- Merge pull request #106 from nomadmot/wounded-wombat

Wounded wombat release
- Change width='content" to width='stretch" for performance chart on daily performance page
- Ensure that all numeric variables are properly typed; remove "type: ignore" wherever possible
- Merge pull request #110 from nomadmot/109-improve-type-checking-in-detail-performance-page

109 improve type checking in detail performance page
- Move config.py to model folder as settings.py
- Use camel case for settings fieldnames
- Use camel case for settings fieldnames
- Merge branch '107-configuration-upgrade' of https://github.com/nomadmot/Portfolio-Dashboard into 107-configuration-upgrade
- Upgrade libraries, add lpydantic_settings
- Added pydantic BaseSettings class to hold basic configuration
- Optionally read settings from .env
- WIP: move settings.py to new "config" folder
- WIP: move settings.py to new "config" folder
- WIP: move settings.py to new "config" folder
- Split settings and database configuration into seperate modules, export at package level
- Import SETTINGS and DATABASE_ENGINE configurations from config package
- Do not use yfinance enable_debug_mode fumnction per deprecation warning
- No need to load environment variables from .env
- Read .env file from .settings directory
- New .settings folder for configuration files
- Add documentation for Settings class
- Add display of today daily pct change for comparison symbol
- Merge pull request #112 from nomadmot/107-configuration-upgrade

107 configuration upgrade
- Move user input widgets to sidebar; use st.title for page header
- Split string to fix line too long warning
- Set initial page configuration
- Use a large icon size for the left panel
- Merge pull request #114 from nomadmot/108-left-panel

move all user input widgets to a sliding left panel
- Add DuckDB to project
- Add setting for DuckDB databse file
- New module with function get_closed_count returns the count of stock market holidays between two dates
- WIP: new function to return start and end dates for a selected period
- WIP: add logging, get_period_dates function
- Add get_period_dates from module core.import to module exports
- Change to .settings directory before reading .env file
- WIP: add implementaqtions for periods YTD, YR1, and ALL
- Return earliest possible date instead of None as begin date for period ALL
- Add market_calendar functions to utility module exports
- Add function to check if the stock market is open on a given date
- Add implementations for 30, 50 and 90 day periods
- Add TimeMachineComponent to exports for module utility
- Streamlit component to handle date and period selection
- Export get_time_machine_component instead of TimeMachineComponent class
- Specify data types where applicable; fix initial values; check for valid period
- Many changes... it mostly works now
- Use from_ and to_  dates for record selection instead of period
- Use TimeMachineComponent instead of selecttbox for period selection
- Use time Machine Component instead of selectbox for period selection
- Provide begin and end dates for get_balance_history function; add account name to page title
- Get_period_dates will not return None
- Rename daily_performance to performance_summary; associated UI changes
- Reorganized page; updated UI verbiage
- Added account name to page title
- Add Periods.NONE to represent the uninitialized state
- Move period date calculation from callback to period setter function; enable period input for component creation; enhance logging
- Add 1 day to end_date to include in returned results; enhance comments
- Use begin and end dates instead of period for selection in get_trades
- Merge pull request #118 from nomadmot/97-period-selection-for-custom-date

97 period selection for custom date
- Removed unnecessary imports
- System info page and support utility functions
- Update time machine dates to begin and end dates from trades
- Add logging, update time machine begin and end dates in time machine to first and last dates found on file
- Works properly now
- Merge pull request #120 from nomadmot/119-adjust-time-machine-dates-in-performance-summary

119 adjust time machine dates in performance summary
- Add constant for component key; update to match page name
- Merge pull request #123 from nomadmot/122-performance-summary-page-component-rename

add constant for component key; update to match page name
- Removed unnecessary return from render method
- Rename method amcu_get_instance to get_aumc_instance
- Re-engineered auto-update multiselect component to follow the same pattern as in time machine component
- Merge pull request #124 from nomadmot/121-enhancerewrite-auto-update-multiselect-component

121 enhancerewrite auto update multiselect component
- Re-engineered component to follow the same pattern as the time machine component
- Export get_status_message_component function instead of StatusMessageComponent class
- No need to clear StatusMessageComponent here
- Use the re-engineered status message component; remove unnecessary session state
- Move the status message component to the bottom of the sidebar; much linting
- Delete commented code
- Add type hints and documentation
- Add type hints
- Use new time machine and status message components
- Set status message to default in clear_status_message function
- Reorganize code; much linting
- Merge pull request #126 from nomadmot/115-status-messages

115 status messages
- Merge pull request #128 from nomadmot/illustrious-aardvark

Illustrious aardvark
- Add environment variable for duck pond directory
- Merge pull request #129 from nomadmot/illustrious-aardvark

add environment variable for duck pond directory
- Set index on period selectbox widget when rendered
- Merge pull request #131 from nomadmot/130-persist-period-selection-in-time-machine

persist period selectbox in TimeMachineComponent so it will come back to it's previous setting
- Rename global SETTINGS as ENVIRONMENT
- Rename file settings.py as env_settings.py
- Add library pyyaml to project
- Add app_config.yml to gitignore
- Work in progress
- New config.settings module combines input from environment, .setings/.env, and .settings/app_config.yml for application configuration
- Example .env file
- New utility module to manage application logging
- Use performance_summary_period from settins defaults to set the initial period
- Add httpx to project libraries
- Use new utility.get_logger function for application logging
- Change name of global variable ENVIRONMENT to SETTINGS
- Add debug configuration item to settings to specify debug level logging for selected modules
- Add file name to debug messager
- Much linting and debugging
- Use default.performance_summary_symbols setting as options for comparison symbol selectbox in Performance Summary page
- Merge pull request #136 from nomadmot/113-configure-daily-performance-comparison-symbols

113 configure daily performance comparison symbols
- Add directory .vscode to gitignore
- Add app_config.yml to gitignore
- Merge branch '125-time-machine-period-not-persistent' of https://github.com/nomadmot/Portfolio-Dashboard into 125-time-machine-period-not-persistent
- Render period selectbox with initial index corresponding to most recent value
- Merge pull request #137 from nomadmot/125-time-machine-period-not-persistent

125 time machine period not persistent
- Remove from git tracxking
- Add .vscode/settings.json to .gitignore
- Add utility.status_message_component.StatusType to module exports
- Refarkled everything to use Streamlit toast
- Use new StatusMessageComponent for user alerts
- Merge pull request #138 from nomadmot/134-check-status-update

134 check status update
- Add user status messages to Detail Performance page using StatusMessageComponent
- Merge pull request #140 from nomadmot/127-detail-performance-status-messages

provide user feedback in Detail Performance page
- Move database.py from settings to utility to avoid circular import
- Add sqlalchemy_echo and sqlalchemy_echo_pool configuration items to assist debugging sqlalchemy
- Import DATABASE._ENGINE from utility module
- Additional settings for SQLAlchemy logging
- Set loglevel on all pre-defined SQLAlchemy channels
- Make begin_date and end_date parameter names consistent; log entry into module methods
- Add file name to module entry debug message
- From_date and to_date parameter names changed to begin_date and end_date
- Don't track compose-osx.yaml
- Add new settings to docker build
- New file to ignore __pycache__ when doing docker build
- Adjust exclusion when adding files to image; ensure everything owned by devuser
- Example files with reasonable defaults to run system
- Explanation for .settings directory
- Add compose-osx-test.yaml to .gitignore
- Use DuckDB file interface instead of database to avoid locked database errors
- Enhanced user and log messages
- Rename duck database to duck puddle
- Merge pull request #144 from nomadmot/17-minimize-db-open-interval

17 minimize db open interval
- Remove "centered" page configuration; delayed dataframe display until after database updates
- Remove "centered" page configuration; delayed dataframe display until after database updates
- Merge branch '139-flashing-in-manage-daily-balances-page' of https://github.com/nomadmot/Portfolio-Dashboard into 139-flashing-in-manage-daily-balances-page
- Merge pull request #147 from nomadmot/139-flashing-in-manage-daily-balances-page

139 flashing in manage daily balances page
- Add pages... to debug example entry
- Use module "pages." + file stem for logger name with Streamlit pages
- Removed deprecated note
- Merge pull request #149 from nomadmot/146-use-file-name-for-logging-pages

146 use file name for logging pages
- Add __version __.py file containing version metada; display metadata in system info page
- Merge pull request #150 from nomadmot/141-show-version-in-system-info

141 show version in system info
- Add __version __.py file containing version metada; display metadata in system info page
- Added development header to all pages to visuall identify the development environment
- Merge pull request #151 from nomadmot/142-identify-dev-environment

142 identify dev environment
- Create a Borg button at the end of the sidebar  to display system information on the page
- Move logic to display system information to the "show_system_info" function in the utility module
- Linting, add hover help to Borg button
- Don't expect final slash on setting for duck puddle directory
- Rename duck database as duck puddle
- Merge pull request #152 from nomadmot/132-fade-system-info

132 fade system info
- Merge pull request #135 from nomadmot/cynical-kitten

Cynical kitten
- Version 0.2.0 PROD
- Update stuff
- Use production database, not test
- README and CODE OF CONDUCT for repository (work in prgoress)
- Rename devuser as appuser, don't include vscode server
- Change repository name, use docker command instead of podman
- Change repository name, rename devuser as appuser, polish for public
- Polish for public
- Ignore build test scripts
- Ignore test scripts
- Add docker installation instructions
- Going public
- Use discussions
- Add next steps (intial preview)
- Add next steps (intial preview)

### 🧪 Testing

- Test scripts for docker build and push
- Test script for periods.py
