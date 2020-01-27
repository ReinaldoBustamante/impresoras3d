#! C:\Users\spun\AppData\Local\Programs\Python\Python37\python.exe
from flask import Flask, render_template, request, url_for, redirect, flash
#importo modulo mysql
from flask_mysqldb import MySQL
import telnetlib
import functools
import time
import ctypes
import webbrowser
import sys


def readm27(mess):
        if b"Not SD printing" in mess:
            return "notp",0.0
        #elif b"T:" in mess :
        #    return "heat",0.0
        elif b"SD printing" in mess:
            text=mess.decode("utf-8")
            percentext=""
            for l in text:
                if (l>='0' and l<='9') or l=="/":
                    percentext+=l
            temp=percentext.split("/")
            return "print",100*int(temp[0])/int(temp[1])
        else:
            return "else",0.0
            

def checkanswer(mess):
        if b"Resend" in mess:
            return True
        elif b"ok" in mess:
            return False
        elif b"T:" in mess :
            print("Actualmente la impresora esta calentando e ignorara otros comandos, espere un minuto")
            for n in range(6):
                time.sleep(10)
                print(str((n+1)*10)+" segundos pasados...")
            print("Listo")
            return True
        else:
            return True


app = Flask(__name__)
#my sql connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flaskimpresoras'

mysql = MySQL(app)

#sesion

app.secret_key = 'mysecretkey'

#ruta para index
@app.route('/')
def Index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM impresoras')
    data = cur.fetchall()
    return render_template('index.html', impresoras = data)

#ruta para formulario
@app.route('/formulario')
def formulario():
    return render_template('formulario.html')

#ruta para agregar una impresora
@app.route('/add_printer', methods = ['POST']) # como agrego ocupa metodo post
def add_printer():
    if request.method == 'POST': # agrega base de datos
        name= request.form['name']
        ip= request.form['ip']
        ip_publica = request.form['ip_publica']
        boquilla = request.form['boquilla']
        cama = request.form['cama']
        filamento = request.form['filamento']
        color_filamento = request.form['color_filamento']
        cur = mysql.connection.cursor()
        if name == '' or ip == '' or ip_publica == '':
            flash('nombre,ip,ip publica necesarios')
            return redirect(url_for('formulario'))

        else:
            cur.execute('INSERT INTO impresoras (name, ip, ip_publica, boquilla, cama, filamento, color_filamento) VALUES (%s, %s, %s, %s, %s, %s, %s)',(name, ip, ip_publica, boquilla, cama, filamento, color_filamento))
            mysql.connection.commit()
            flash('Printer Added successfully')
            return redirect(url_for('Index'))
    

#ruta para obtener id de una impresora una impresora
@app.route('/edit/<id>')
def get_printer(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM impresoras WHERE id = %s', [id])
    data = cur.fetchall()
    return render_template('edit.html', datos = data[0])

@app.route('/printer/<id>')
def isprinter(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM impresoras WHERE id = %s', [id])
    data = cur.fetchall()
    host = data[0][3]
    print(host)
    port = "8888"
    conected=False
    try:
        tn = telnetlib.Telnet(host,port)
        print("conectado")
        conected=True
    except:
        flash("impresora no disponible")
    if conected:
        send=1
        while send:
            print("M27")
            tn.write(b"M27\n")
            msj = tn.read_until(b'ok',timeout=10)
            print(msj)
            send=checkanswer(msj)
        est,per=readm27(msj)
        if est == "notp":
            #flash("No se esta imprimiendo nada\n")
            webbrowser.open_new_tab("http://"+data[0][2])
            return redirect(url_for('Index'))
        elif est == "heat":

            flash("La impresora se esta calentando\n")
        elif est == "print":
            flash("La impresroa esta ocupada: porcentaje impresion: "+str(per)+"%\n")
        else:
            flash("La impresora se esta preparando a imprimir\n")
        #if(msjdecode == "Not SD printing\nok"):
        #    return render_template('redirect.html', datos = data[0][2])
        #else:
        #    flash("Esta Imprimiendo")
        #    return redirect(url_for('Index'))
        tn.close()
    return redirect(url_for('Index'))

    
    
#ruta para editar impresora
@app.route('/update/<id>', methods = ['POST'])
def update_printer(id):
    if request.method == 'POST':
        name = request.form['name']
        ip = request.form['ip']
        ip_publica= request.form['ip_publica']
        boquilla = request.form['boquilla']
        cama = request.form['cama']
        filamento = request.form['filamento']
        color_filamento = request.form ['color_filamento']
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE impresoras
            SET name = %s,
                ip = %s,
                ip_publica = %s,
                boquilla = %s,
                cama = %s,
                filamento = %s,
                color_filamento = %s
            WHERE id = %s
        """, (name, ip, ip_publica, boquilla, cama, filamento, color_filamento, id))
        mysql.connection.commit()
        flash('Printer Updated Successfully')
        return redirect(url_for('Index'))

#ruta para eliminar una impresora
@app.route('/delete/<string:id>')
def delete_printer(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM impresoras WHERE id = {0}'.format(id)) #posicion 0 esta relacionada con la tabla de php
    mysql.connection.commit()
    flash('Printer Removed Successfully')
    return redirect(url_for('Index'))

#ruta para detalles
@app.route('/detalles/<string:id>')
def detalles_printer(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM impresoras WHERE id = %s', [id])
    data = cur.fetchall()
    return render_template("detalles.html", datos = data[0])

#si existe se abre el servidor
if __name__ == '__main__':
    app.run(debug = True, port = 5040, host='0.0.0.0')