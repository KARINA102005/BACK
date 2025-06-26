from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Database connection pool
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT')
    )
    print("Connection pool created successfully")
except Exception as e:
    print(f"Error creating connection pool: {e}")

# Helper function to get a database connection
def get_db_connection():
    return connection_pool.getconn()

# Helper function to release a database connection
def release_db_connection(conn):
    connection_pool.putconn(conn)

# Donantes (Donors) CRUD
@app.route('/donantes', methods=['GET', 'POST'])
@app.route('/donantes/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def handle_donantes(id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if request.method == 'GET':
            if id:
                cursor.execute('SELECT * FROM Donantes WHERE id_donante = %s', (id,))
                donor = cursor.fetchone()
                if donor:
                    return jsonify({
                        'id_donante': donor[0],
                        'nombre': donor[1],
                        'contacto': donor[2],
                        'direccion': donor[3],
                        'fecha_registro': donor[4]
                    })
                else:
                    return jsonify({'message': 'Donor not found'}), 404
            else:
                cursor.execute('SELECT * FROM Donantes')
                donors = cursor.fetchall()
                return jsonify([{
                    'id_donante': donor[0],
                    'nombre': donor[1],
                    'contacto': donor[2],
                    'direccion': donor[3],
                    'fecha_registro': donor[4]
                } for donor in donors])
        
        elif request.method == 'POST':
            data = request.get_json()
            cursor.execute(
                'INSERT INTO Donantes (nombre, contacto, direccion, fecha_registro) VALUES (%s, %s, %s, %s) RETURNING id_donante',
                (data['nombre'], data['contacto'], data['direccion'], data.get('fecha_registro', 'NOW()'))
            )
            new_id = cursor.fetchone()[0]
            conn.commit()
            return jsonify({'message': 'Donor created successfully', 'id_donante': new_id}), 201
        
        elif request.method == 'PUT':
            data = request.get_json()
            cursor.execute(
                'UPDATE Donantes SET nombre = %s, contacto = %s, direccion = %s, fecha_registro = %s WHERE id_donante = %s',
                (data['nombre'], data['contacto'], data['direccion'], data.get('fecha_registro'), id)
            )
            if cursor.rowcount == 0:
                return jsonify({'message': 'Donor not found'}), 404
            conn.commit()
            return jsonify({'message': 'Donor updated successfully'})
        
        elif request.method == 'DELETE':
            cursor.execute('DELETE FROM Donantes WHERE id_donante = %s', (id,))
            if cursor.rowcount == 0:
                return jsonify({'message': 'Donor not found'}), 404
            conn.commit()
            return jsonify({'message': 'Donor deleted successfully'})
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        release_db_connection(conn)

# Equipos_Medicos (Medical Equipment) CRUD
@app.route('/equipos-medicos', methods=['GET', 'POST'])
@app.route('/equipos-medicos/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def handle_equipos_medicos(id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if request.method == 'GET':
            if id:
                cursor.execute('''
                    SELECT e.*, d.nombre as nombre_donante 
                    FROM Equipos_Medicos e 
                    LEFT JOIN Donantes d ON e.id_donante = d.id_donante 
                    WHERE e.id_equipo = %s
                ''', (id,))
                equipo = cursor.fetchone()
                if equipo:
                    return jsonify({
                        'id_equipo': equipo[0],
                        'nombre_equipo': equipo[1],
                        'marca': equipo[2],
                        'modelo': equipo[3],
                        'estado': equipo[4],
                        'fecha_fabricacion': equipo[5],
                        'fecha_donacion': equipo[6],
                        'id_donante': equipo[7],
                        'nombre_donante': equipo[8]
                    })
                else:
                    return jsonify({'message': 'Equipment not found'}), 404
            else:
                cursor.execute('SELECT * FROM Equipos_Medicos')
                equipos = cursor.fetchall()
                return jsonify([{
                    'id_equipo': equipo[0],
                    'nombre_equipo': equipo[1],
                    'marca': equipo[2],
                    'modelo': equipo[3],
                    'estado': equipo[4],
                    'fecha_fabricacion': equipo[5],
                    'fecha_donacion': equipo[6],
                    'id_donante': equipo[7]
                } for equipo in equipos])
        
        elif request.method == 'POST':
            data = request.get_json()
            cursor.execute(
                '''INSERT INTO Equipos_Medicos 
                (nombre_equipo, marca, modelo, estado, fecha_fabricacion, fecha_donacion, id_donante) 
                VALUES (%s, %s, %s, %s, %s, %s, %s) 
                RETURNING id_equipo''',
                (data['nombre_equipo'], data.get('marca'), data.get('modelo'), 
                 data['estado'], data.get('fecha_fabricacion'), 
                 data.get('fecha_donacion', 'NOW()'), data.get('id_donante'))
            )
            new_id = cursor.fetchone()[0]
            conn.commit()
            return jsonify({'message': 'Equipment created successfully', 'id_equipo': new_id}), 201
        
        elif request.method == 'PUT':
            data = request.get_json()
            cursor.execute(
                '''UPDATE Equipos_Medicos 
                SET nombre_equipo = %s, marca = %s, modelo = %s, estado = %s, 
                    fecha_fabricacion = %s, fecha_donacion = %s, id_donante = %s 
                WHERE id_equipo = %s''',
                (data['nombre_equipo'], data.get('marca'), data.get('modelo'), 
                 data['estado'], data.get('fecha_fabricacion'), 
                 data.get('fecha_donacion'), data.get('id_donante'), id)
            )
            if cursor.rowcount == 0:
                return jsonify({'message': 'Equipment not found'}), 404
            conn.commit()
            return jsonify({'message': 'Equipment updated successfully'})
        
        elif request.method == 'DELETE':
            cursor.execute('DELETE FROM Equipos_Medicos WHERE id_equipo = %s', (id,))
            if cursor.rowcount == 0:
                return jsonify({'message': 'Equipment not found'}), 404
            conn.commit()
            return jsonify({'message': 'Equipment deleted successfully'})
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        release_db_connection(conn)

# Entregas (Deliveries) CRUD
@app.route('/entregas', methods=['GET', 'POST'])
@app.route('/entregas/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def handle_entregas(id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if request.method == 'GET':
            if id:
                cursor.execute('''
                    SELECT e.*, eq.nombre_equipo 
                    FROM Entregas e 
                    JOIN Equipos_Medicos eq ON e.id_equipo = eq.id_equipo 
                    WHERE e.id_entrega = %s
                ''', (id,))
                entrega = cursor.fetchone()
                if entrega:
                    return jsonify({
                        'id_entrega': entrega[0],
                        'fecha_entrega': entrega[1],
                        'estado_equipo': entrega[2],
                        'id_equipo': entrega[3],
                        'nombre_equipo': entrega[4]
                    })
                else:
                    return jsonify({'message': 'Delivery not found'}), 404
            else:
                cursor.execute('''
                    SELECT e.*, eq.nombre_equipo 
                    FROM Entregas e 
                    JOIN Equipos_Medicos eq ON e.id_equipo = eq.id_equipo
                ''')
                entregas = cursor.fetchall()
                return jsonify([{
                    'id_entrega': entrega[0],
                    'fecha_entrega': entrega[1],
                    'estado_equipo': entrega[2],
                    'id_equipo': entrega[3],
                    'nombre_equipo': entrega[4]
                } for entrega in entregas])
        
        elif request.method == 'POST':
            data = request.get_json()
            cursor.execute(
                '''INSERT INTO Entregas 
                (fecha_entrega, estado_equipo, id_equipo) 
                VALUES (%s, %s, %s) 
                RETURNING id_entrega''',
                (data.get('fecha_entrega', 'NOW()'), data['estado_equipo'], data['id_equipo'])
            )
            new_id = cursor.fetchone()[0]
            conn.commit()
            return jsonify({'message': 'Delivery created successfully', 'id_entrega': new_id}), 201
        
        elif request.method == 'PUT':
            data = request.get_json()
            cursor.execute(
                '''UPDATE Entregas 
                SET fecha_entrega = %s, estado_equipo = %s, id_equipo = %s 
                WHERE id_entrega = %s''',
                (data.get('fecha_entrega'), data['estado_equipo'], data.get('id_equipo'), id)
            )
            if cursor.rowcount == 0:
                return jsonify({'message': 'Delivery not found'}), 404
            conn.commit()
            return jsonify({'message': 'Delivery updated successfully'})
        
        elif request.method == 'DELETE':
            cursor.execute('DELETE FROM Entregas WHERE id_entrega = %s', (id,))
            if cursor.rowcount == 0:
                return jsonify({'message': 'Delivery not found'}), 404
            conn.commit()
            return jsonify({'message': 'Delivery deleted successfully'})
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        release_db_connection(conn)

# Additional Reports
@app.route('/reportes/equipos-por-estado')
def report_equipos_por_estado():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT estado, COUNT(*) as cantidad 
            FROM Equipos_Medicos 
            GROUP BY estado 
            ORDER BY cantidad DESC
        ''')
        results = cursor.fetchall()
        return jsonify([{'estado': row[0], 'cantidad': row[1]} for row in results])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        release_db_connection(conn)

@app.route('/reportes/entregas-recientes')
def report_entregas_recientes():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT e.id_entrega, e.fecha_entrega, e.estado_equipo,
                   eq.nombre_equipo, eq.marca, eq.modelo,
                   d.nombre as donante
            FROM Entregas e
            JOIN Equipos_Medicos eq ON e.id_equipo = eq.id_equipo
            LEFT JOIN Donantes d ON eq.id_donante = d.id_donante
            WHERE e.fecha_entrega >= NOW() - INTERVAL '30 days'
            ORDER BY e.fecha_entrega DESC
        ''')
        columns = [desc[0] for desc in cursor.description]
        entregas = cursor.fetchall()
        return jsonify([dict(zip(columns, row)) for row in entregas])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        release_db_connection(conn)

if __name__ == '__main__':
    app.run(debug=True)