from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)

# Initialize the database
def init_db():
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY,
                        type TEXT,
                        category TEXT,
                        amount REAL,
                        date TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Home route (show summary and transactions)
@app.route('/')
def index():
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transactions')
    transactions = cursor.fetchall()

    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'income'")
    total_income = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'expense'")
    total_expenses = cursor.fetchone()[0] or 0

    balance = total_income - total_expenses

    conn.close()
    return render_template('index.html', transactions=transactions, income=total_income, expenses=total_expenses, balance=balance)

# Add a transaction
@app.route('/add', methods=['POST'])
def add_transaction():
    t_type = request.form['type']
    category = request.form['category']
    amount = float(request.form['amount'])
    date = request.form['date']

    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO transactions (type, category, amount, date) VALUES (?, ?, ?, ?)', 
                   (t_type, category, amount, date))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Delete a transaction
@app.route('/delete/<int:id>')
def delete_transaction(id):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Route to get data for charts
@app.route('/chart-data')
def chart_data():
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    # Get category-wise sums
    cursor.execute('SELECT category, SUM(amount) FROM transactions WHERE type="expense" GROUP BY category')
    expenses_by_category = cursor.fetchall()

    # Get date-wise expenses
    cursor.execute('SELECT date, SUM(amount) FROM transactions WHERE type="expense" GROUP BY date ORDER BY date')
    expenses_by_date = cursor.fetchall()

    conn.close()

    # Prepare data for charts
    data = {
        "categories": [row[0] for row in expenses_by_category],
        "amounts": [row[1] for row in expenses_by_category],
        "dates": [row[0] for row in expenses_by_date],
        "daily_expenses": [row[1] for row in expenses_by_date],
    }

    return jsonify(data)



if __name__ == '__main__':
    app.run(debug=True)
