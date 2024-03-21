from flask import Flask, render_template, request, redirect, url_for, jsonify
import pymssql

app = Flask(__name__)

def get_db_connection():
    return pymssql.connect(
        server='ell887.database.windows.net',
        user='atul',
        password='ell887#cc',
        database='product',
        port=1433,
        login_timeout=30
    )

def create_table():
    with pymssql.connect(
        server='ell887.database.windows.net',
        user='atul',
        password='ell887#cc',
        database='product',
        port=1433,
        login_timeout=30
    ) as connection:
        cursor = connection.cursor()

        # Check if the table exists
        cursor.execute("SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'products'")
        table_exists = cursor.fetchone()

        if not table_exists:
            # Table does not exist, create it
            cursor.execute(
                '''CREATE TABLE products (id INT PRIMARY KEY IDENTITY, name NVARCHAR(255) NOT NULL, description NVARCHAR(MAX))''')

        connection.commit()

create_table()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form['name']
        product_description = request.form['description']
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO dbo.products (name, description) VALUES (%s, %s)", (product_name, product_description))
        connection.commit()
        connection.close()
        return redirect(url_for('index'))
    return render_template('add_product.html')

@app.route('/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if request.method == 'POST':
        new_name = request.form['name']
        new_description = request.form['description']
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE dbo.products SET name = %s, description = %s WHERE id = %s",
                       (new_name, new_description, product_id))
        connection.commit()
        connection.close()
        return redirect(url_for('index'))
    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM dbo.products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    connection.close()

    if not product:
        return render_template('error.html', message='Product not found.')

    return render_template('edit_product.html', product=product)

@app.route('/delete/<int:product_id>')
def delete_product(product_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM dbo.products WHERE id = %s", (product_id,))
    connection.commit()
    connection.close()
    return redirect(url_for('index'))

@app.route('/reset')
def reset():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM dbo.products")
    connection.commit()
    connection.close()
    return redirect(url_for('index'))

@app.route('/view_all')
def view_all():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM dbo.products")
    products = cursor.fetchall()
    connection.close()
    return jsonify([{'id': product[0], 'name': product[1], 'description': product[2]} for product in products])

if __name__ == '__main__':
    app.run(debug=True)
