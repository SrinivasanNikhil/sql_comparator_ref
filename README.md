# SQL Comparator

A Python tool for comparing SQL query execution plans and results across different database environments. This tool is designed to help students and individuals interested in SQL ensure consistency and correctness of SQL queries by comparing user-submitted queries against reference queries.

## Project Description

The SQL Comparator project aims to provide a comprehensive solution for comparing SQL queries and their execution results across different database environments. It is particularly useful for educational purposes, allowing students to verify the accuracy and efficiency of their SQL queries. The tool supports various comparison features, including file-based comparisons, single query comparisons, and detailed feedback on query differences.

## Features

- **File Comparison**: Compare SQL queries from user-uploaded JSON files against reference JSON files.
- **Single Query Comparison**: Compare individual SQL queries directly through the web interface.
- **Query Analysis**: Analyze the textual differences between user queries and reference queries.
- **Result Comparison**: Compare the results of executing user queries and reference queries, including column structure and record counts.
- **Detailed Feedback**: Provide detailed feedback on missing and additional terms in user queries, as well as exact match status.

## Setup

1. Clone the repository:

```bash
git clone <repository_url>
cd sql_comparator_ref
```

2. Create a virtual environment and activate it:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   Create a `.env` file in the root directory and add the following:

```
SECRET_KEY=your_secret_key
DB_HOST=your_db_host
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_db_name
```

5. Initialize the database:

```bash
flask db upgrade
```

## Usage

1. Run the application:

```bash
flask run
```

2. Open your web browser and go to `http://127.0.0.1:5000`.

3. Use the web interface to upload JSON files for comparison or to compare individual SQL queries.

## Configuration

The application uses a `config.py` file for configuration. You can modify the database connection details and other settings in this file.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Submit a pull request

## License

MIT License
