from autoapp import app
from dais_pcto.module_extensions import db
from dais_pcto.settings import DevConfig

db.session.close


#app.config.from_object(DevConfig)
with app.app_context():
    with db.engine.connect() as con:

       #CHECK SU LESSONS
       #Correttezza delle modalità e dei campi rispettivi
       db.session.execute(
           """
           ALTER TABLE lessons
            ADD CHECK((_mode = 'presenza' AND _structure <> 'vuoto' AND _link = 'vuoto') OR
                (_mode = 'online' AND _structure = 'vuoto' AND _link <> 'vuoto') OR
                (_mode = 'blended' AND _structure <> 'vuoto' AND _link <> 'vuoto'));
           """)
    
       #CHECK SU LESSONS
       #Correttezza delle ore di inizio e di fine
        db.session.execute(
            """
            ALTER TABLE lessons
                ADD CHECK((_start_hour >= '09:00' AND _start_hour <= '20:00') 
                        AND (_end_hour >= '09:00' AND _end_hour <= '20:00') 
                        AND (_end_hour > _start_hour));
            """)
        
        #CHECK SU LESSONS
        #_mode può assumere solo 3 possibili valori
        db.session.execute(
            """
            ALTER TABLE lessons
                ADD CHECK(_mode = 'presenza' OR _mode = 'online' OR _mode = 'blended');
            """)
        
        #CHECK SU LESSONS
        #Correttezza della data rispetto alla data odierna
        db.session.execute(
            """
            ALTER TABLE lessons
                ADD CHECK(_date > current_date);
            """)
        
        #CHECK SU USERS
        #_role può assumere solo 3 possibili valori
        db.session.execute(
            """
            ALTER TABLE users
                ADD CHECK (_role = 'user' OR _role = 'professor' OR _role = 'admin');
            """)
        
        #CHECK SU COURSES
        #Correttezza del mese di inzio e fine
        db.session.execute(
            """
            ALTER TABLE courses
                ADD CHECK(_start_month < _end_month AND _start_month > current_date);
            """)
        
        #CHECK SU COURSES
        #_mode può assumere solo 3 possibili valori
        db.session.execute(
            """
            ALTER TABLE courses
                ADD CHECK(_mode = 'presenza' OR _mode = 'blended' OR _mode = 'online');
            """)
        
        #CHECK SU COURSES
        #Correttezza del numero minimo e massimo di studenti
        db.session.execute(
            """
            ALTER TABLE courses
                ADD CHECK(_max_student > _min_student AND _min_student >= '10');
            """)
        
        #TRIGGER SU USER_CORSE E USER_LESSON
        #Lo user_id deve essere asscociato solamente a studenti (_role = user)
        db.session.execute(
            """
            CREATE FUNCTION only_user() RETURNS trigger AS $$
             BEGIN
                IF(NEW.user_id NOT IN 
                (SELECT _user_id FROM users WHERE _role = 'user')) THEN
                    RETURN NULL;
                END IF;
                RETURN NEW;
              END;
              $$ LANGUAGE plpgsql;

                CREATE TRIGGER OnlyUserCourse
                BEFORE INSERT OR UPDATE ON user_corse
                FOR EACH ROW 
                EXECUTE FUNCTION only_user();

                CREATE TRIGGER OnlyUserLesson
                BEFORE INSERT OR UPDATE ON user_lesson
                FOR EACH ROW 
                EXECUTE FUNCTION only_user();
            """)
        
        #TRIGGER SU USER_LESSON
        #Non ci possono essere studenti in lezioni di corsi che non frequentano
        db.session.execute(
            """
            CREATE FUNCTION no_user_in_course() RETURNS trigger AS $$
            BEGIN
                IF( (SELECT course
                   FROM lessons
                   WHERE _lesson_id = NEW.lesson_id) NOT IN (SELECT course_id
                                                            FROM user_corse
                                                            WHERE user_id = NEW.user_id)) THEN
                    RETURN NULL;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER NoUserInCourse
            BEFORE INSERT OR UPDATE ON user_lesson
            FOR EACH ROW
            EXECUTE FUNCTION no_user_in_course();
            """)
        
        #TRIGGER SU USER_CORSE
        #Non si può superare il massimo numero di studenti di un corso
        db.session.execute(
            """
            CREATE FUNCTION no_over_max() RETURNS trigger AS $$
            BEGIN
                IF((SELECT _max_student
                  FROM courses
                  WHERE _course_id = NEW.course_id)
                  <
                  (SELECT count(*)
                  FROM user_corse
                  WHERE course_id = NEW.course_id)) THEN
                  DELETE FROM user_corse 
                  WHERE NEW.course_id = course_id AND NEW.user_id = user_id;
                END IF;
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER NoOverMax
            BEFORE INSERT ON user_corse
            FOR EACH ROW
            EXECUTE FUNCTION no_over_max();
            """)
        
        #TRIGGER SU LESSONS
        #Non si possono aggiungere lezioni se si sta superando l’ammontare di ore prestabilito
        db.session.execute(
            """
            CREATE FUNCTION no_lesson_over() RETURNS trigger AS $$
            BEGIN
                IF((select sum(l._end_hour-l._start_hour) 
                   from lessons as l 
                   where l.course = NEW.course)
                   > 
                   (select make_interval(hours => co._n_hour) 
                   from courses as co 
                   where co._course_id = NEW.course)) THEN
                    DELETE FROM lessons WHERE _lesson_id = NEW._lesson_id;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER NoLessonOver
            AFTER INSERT ON lessons
            FOR EACH ROW
            EXECUTE FUNCTION no_lesson_over();
            """)
        
        #TRIGGER SU LESSONS
        #Non si può modificare l'ora di inzio delle lezioni se si sta superando l’ammontare di ore prestabilito
        db.session.execute(
            """
            CREATE FUNCTION no_start_lesson_over_m() RETURNS trigger AS $$
            BEGIN
                IF((select sum(l._end_hour-l._start_hour) 
                   from lessons as l 
                   where l.course = NEW.course)
                   > 
                   (select make_interval(hours => co._n_hour) 
                   from courses as co 
                   where co._course_id = NEW.course)) THEN
                    UPDATE lessons
                    SET _start_hour = OLD._start_hour
                    WHERE _lesson_id = NEW._lesson_id;
                END IF;
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER nostartlessonoverm
            AFTER UPDATE OF _start_hour
            ON lessons
            FOR EACH ROW
            EXECUTE FUNCTION no_start_lesson_over_m();
            """)

        #TRIGGER SU LESSONS
        #Non si può modificare l'ora di fine delle lezioni se si sta superando l’ammontare di ore prestabilito
        db.session.execute(
            """
            CREATE FUNCTION no_end_lesson_over_m() RETURNS trigger AS $$
            BEGIN
                IF((select sum(l._end_hour-l._start_hour) 
                   from lessons as l 
                   where l.course = NEW.course)
                   > 
                   (select make_interval(hours => co._n_hour) 
                   from courses as co 
                   where co._course_id = NEW.course)) THEN
                    UPDATE lessons
                    SET _end_hour = OLD._end_hour
                    WHERE _lesson_id = NEW._lesson_id;
                END IF;
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER noendlessonoverm
            AFTER UPDATE OF _end_hour
            ON lessons
            FOR EACH ROW
            EXECUTE FUNCTION no_end_lesson_over_m();
            """)
        
        #TRIGGER SU LESSONS
        #La data della lezione deve essere dopo il mese di inizio e prima del mese di fine del corso a cui si riferisce
        db.session.execute(
            """
            CREATE FUNCTION correct_dates() RETURNS trigger AS $$
            BEGIN
                IF(NEW._date < (SELECT _start_month FROM courses WHERE NEW.course = _course_id) OR 
                   NEW._date > (SELECT _end_month FROM courses WHERE NEW.course = _course_id)) THEN
                    RETURN NULL;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER correctdates
            BEFORE INSERT ON lessons
            FOR EACH ROW
            EXECUTE FUNCTION correct_dates();
            """)
        
        #TRIGGER SU LESSONS
        #Non ci possono essere lezioni sovrapposte
        db.session.execute(
            """
            CREATE FUNCTION no_lessons_overlying() RETURNS trigger AS $$
            BEGIN
                IF(NEW._date = ANY (SELECT _date
                                    FROM lessons
                                    WHERE (NEW._start_hour <= _start_hour AND NEW._end_hour <= _end_hour) OR
                                    (NEW._start_hour >= _start_hour AND NEW._end_hour >= _end_hour) OR
                                    (NEW._start_hour >= _start_hour AND NEW._end_hour <= _end_hour) OR
                                    (NEW._start_hour <= _start_hour AND NEW._end_hour >= _end_hour))) THEN
                    RETURN NULL;
                 END IF;
                 RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER NoLessonsOverlying
            BEFORE INSERT OR UPDATE ON lessons
            FOR EACH ROW
            EXECUTE FUNCTION no_lessons_overlying();
            """)
            
        #TRIGGER SU LESSONS
        #Una lezione non può superare le 6 ore
        db.session.execute(
            """
            CREATE FUNCTION limit_hours() RETURNS trigger AS $$
            BEGIN
                IF(NEW._end_hour - NEW._start_hour > '06:00') THEN
                    RETURN NULL;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER LimitHours
            BEFORE INSERT OR UPDATE ON lessons
            FOR EACH ROW
            EXECUTE FUNCTION limit_hours();
            """)
            
        #TRIGGER SU LESSONS
        #La lezione non può essere modificata se:
            #è già avvenuta
            #si vuole modificare il suo id
            #si vuole modificare il corso a cui si riferisce
        db.session.execute(
            """
            CREATE FUNCTION modify_lesson() RETURNS trigger AS $$
            BEGIN
                IF(NEW._date <= current_date OR 
                   NEW._date < (SELECT _start_month
                                FROM courses
                                WHERE _course_id = NEW.course) OR 
                   NEW._date > (SELECT _end_month
                                FROM courses
                                WHERE _course_id = NEW.course) OR 
                   NEW._lesson_id <> OLD._lesson_id OR 
                   NEW.course <> OLD.course) THEN
                        RETURN NULL;
                 END IF;
                 RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER ModifyLesson
            BEFORE UPDATE ON lessons
            FOR EACH ROW
            EXECUTE FUNCTION modify_lesson();
            """)
           
        #TRIGGER SU COURSES
        #L’utente associato può essere solo un professore
        db.session.execute(
            """
            CREATE FUNCTION only_professor() RETURNS trigger AS $$
            BEGIN
                IF(NEW._professor NOT IN (SELECT _user_id FROM users WHERE _role = 'professor')) THEN
                    RETURN NULL;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER onlyprofessor
            BEFORE INSERT OR UPDATE ON courses
            FOR EACH ROW
            EXECUTE FUNCTION only_professor();
            """)
            
        #TRIGGER SU COURSES
        #Il numero massimo di studenti si può solo aumentare
        db.session.execute(
            """
            CREATE FUNCTION max_student_sup() RETURNS trigger AS $$
            BEGIN
                 IF(NEW._max_student < OLD._max_student) THEN
                    RETURN NULL;
                 END IF;
                 RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER MaxStudentSup
            BEFORE UPDATE ON courses
            FOR EACH ROW
            EXECUTE FUNCTION max_student_sup();
            """)
            
        #TRIGGER SU COURSES
        #Le ore del corso si possono solo aumentare
        db.session.execute(
            """
            CREATE FUNCTION n_hour_sup() RETURNS trigger AS $$
            BEGIN
                  IF(NEW._n_hour < OLD._n_hour) THEN
                      RETURN NULL;
                  END IF;
                  RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER NHourSup
            BEFORE UPDATE ON courses
            FOR EACH ROW
            EXECUTE FUNCTION n_hour_sup();
            """)
            
        #TRIGGER SU COURSES
        #La modalità di un corso non si può cambiare
        db.session.execute(
            """
            CREATE FUNCTION no_modify_mode_course() RETURNS trigger AS $$
            BEGIN
                  IF(OLD._mode <> NEW._mode) THEN
                     RETURN NULL;
                  END IF;
                  RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER NoModifyModeCourse
            BEFORE UPDATE ON courses
            FOR EACH ROW
            EXECUTE FUNCTION no_modify_mode_course();
            """)
            
        #TRIGGER SU COURSES
        #Non è possibile modificare il mese di inizio o di fine se lo si vuole mettere prima o uguale alla data di oggi
        db.session.execute(
            """
            CREATE FUNCTION modify_months() RETURNS trigger AS $$
            BEGIN
                IF(NEW._start_month <= current_date OR NEW._end_month <= current_date)THEN
                    RETURN NULL;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER ModifyMonths
            BEFORE UPDATE ON courses
            FOR EACH ROW
            EXECUTE FUNCTION modify_months();
            """)
            
        db.session.commit()
