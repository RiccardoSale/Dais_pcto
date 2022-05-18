from asyncio import sleep

from dais_pcto.module_extensions import db

with db.engine.connect() as con:
    try:
        print("CREAZIONE SCHEMA 'Palestra' : ")
        db.session.execute('CREATE SCHEMA "Palestra";') #todo vedere come fare
        db.session.commit()

        print("CREAZIONE TABELLE : ")
        db.create_all()

        print("[RUOLI]Creazione Ruoli nel Database .... ")
        db.session.execute("CREATE USER admin WITH password 'admin';")
        db.session.execute("CREATE USER segreteria WITH password 'segreteria';")
        db.session.execute("CREATE USER professor WITH password 'professor';")

        db.session.execute('GRANT USAGE ON SCHEMA "Pcto" TO admin; ')

        db.session.execute('GRANT USAGE ON SCHEMA "Pcto" TO segreteria;')

        db.session.execute('GRANT USAGE ON SCHEMA "Pcto" TO professor;')

        db.session.commit()
        print("Permessi concessi !")

        # PERMESSI TABELLA Users
        db.session.execute('GRANT DELETE, INSERT, UPDATE, SELECT ON TABLE "Pcto".users TO admin;')

        db.session.execute(' GRANT SELECT, INSERT ,UPDATE  ON TABLE "Pcto".users TO segreteria;')

        db.session.execute(' GRANT SELECT, INSERT ,UPDATE ON TABLE "Pcto".users TO professor;')

        # PERMESSI TABELLA Courses
        db.session.execute('GRANT DELETE, SELECT, INSERT, UPDATE ON TABLE "Pcto".courses TO admin;')

        db.session.execute('GRANT DELETE, SELECT, INSERT, UPDATE ON TABLE "Pcto".courses TO segreteria;')

        db.session.execute(' GRANT DELETE, SELECT, INSERT, UPDATE ON TABLE "Palestra".time_slots TO professor;')

        # PERMESSI TABELLA Schools
        db.session.execute('GRANT DELETE, SELECT, INSERT, UPDATE ON TABLE "Pcto".h_schools TO admin;')

        db.session.execute('GRANT DELETE, SELECT, INSERT, UPDATE ON TABLE "Pcto".h_schools TO segreteria;')

        db.session.execute('GRANT  SELECT ON TABLE "Pcto".h_schools TO professor;')

        # PERMESSI TABELLA LESSONS
        db.session.execute(' GRANT DELETE, SELECT, INSERT, UPDATE ON TABLE "Pcto".lessons TO admin;')

        db.session.execute('GRANT SELECT, INSERT, UPDATE , DELETE ON TABLE "Pcto".lessons TO segreteria;')

        db.session.execute('GRANT SELECT, INSERT, UPDATE , DELETE ON TABLE "Pcto".lessons TO professor;')
    except:
        db.session.rollback()


