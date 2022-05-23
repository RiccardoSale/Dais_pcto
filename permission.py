from autoapp import app
from dais_pcto.module_extensions import db
with app.app_context():
    with db.engine.connect() as con:
        try:
            print("[RUOLI]Creazione Ruoli nel Database .... ")
            db.session.execute("CREATE USER admin WITH password 'admin';")
            db.session.execute("CREATE USER segreteria WITH password 'segreteria';")
            db.session.execute("CREATE USER professor WITH password 'professor';")
            db.session.execute('GRANT USAGE ON SCHEMA "Pcto" TO admin; ')
            print("Permessi concessi !")
            # PERMESSI TABELLA Users
            db.session.execute('GRANT DELETE, INSERT, UPDATE, SELECT ON TABLE users TO admin;')
            db.session.execute('GRANT SELECT, INSERT ,UPDATE  ON TABLE users TO segreteria;')
            db.session.execute('GRANT SELECT ON TABLE users TO professor;')
            # # PERMESSI TABELLA Courses
            db.session.execute('GRANT DELETE, SELECT, INSERT, UPDATE ON TABLE courses TO admin;')
            db.session.execute('GRANT DELETE, SELECT, INSERT, UPDATE ON TABLE courses TO segreteria;')
            db.session.execute('GRANT DELETE, SELECT, INSERT, UPDATE ON TABLE courses TO professor;')
            # # PERMESSI TABELLA Schools
            db.session.execute('GRANT DELETE, SELECT, INSERT, UPDATE ON TABLE h_schools TO admin;')
            db.session.execute('GRANT DELETE, SELECT, INSERT, UPDATE ON TABLE h_schools TO segreteria;')
            db.session.execute('GRANT  SELECT ON TABLE h_schools TO professor;')
            # # PERMESSI TABELLA LESSONS
            db.session.execute('GRANT DELETE, SELECT, INSERT, UPDATE ON TABLE lessons TO admin;')
            db.session.execute('GRANT SELECT, INSERT, UPDATE , DELETE ON TABLE lessons TO segreteria;')
            db.session.execute('GRANT SELECT, INSERT, UPDATE , DELETE ON TABLE lessons TO professor;')
            db.session.commit()
        except:
            print("errore")
            db.session.rollback()
