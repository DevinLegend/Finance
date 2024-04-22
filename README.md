# Finance Tracker

Finance Tracker is a web-based application developed during CS50 that allows users to simulate buying and selling stocks in real-time. It provides a platform for users to manage a portfolio of stocks, track stock prices, and handle transactions without using real money.

## Features

- **User Registration and Login**: Secure authentication system to manage user access.
- **Real-time Stock Prices**: Users can check real-time stock prices using the `lookup` function.
- **Portfolio Management**: Users can view their current holdings and the value of their portfolio.
- **Buying and Selling Stocks**: Users can simulate stock transactions.
- **Transaction History**: Users can view a history of all transactions.
- **Financial Summaries**: The application provides a detailed summary of the user's financial status.

## Technologies

- Python 3.12
- Flask
- SQLite
- CS50 Library
- HTML, CSS
- JavaScript (for front-end enhancements)

## Setup

### Prerequisites

Ensure you have Python and pip installed on your machine. You will also need Flask and several other Python libraries, which are listed in the `requirements.txt` file.

### Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/DevinLegend/Finance.git
    cd Finance
    ```

2. **Set up a virtual environment** (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

1. **Environment Variables**:
    Set the necessary environment variables:
    ```bash
    export FLASK_APP=app.py
    export FLASK_ENV=development
    ```
    On Windows CMD, use `set` instead of `export`.

2. **Initialize the Database**:
    Ensure the SQLite database is set up by running the initial setup scripts if provided.

3. **Start the Application**:
    ```bash
    flask run
    ```
    This will start the server on `http://127.0.0.1:5000`, where you can access the application.

## Credits

This project was developed as part of the educational curriculum of [Harvard University's CS50 course](https://cs50.harvard.edu). Special thanks to the course staff for providing the CS50 Library and other learning resources.

## Contributing

Contributions to the Finance Tracker are welcome. Please ensure that your code adheres to the project's coding standards and submit a pull request for review.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

