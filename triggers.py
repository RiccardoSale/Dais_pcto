from autoapp import app
from dais_pcto.module_extensions import db
from dais_pcto.settings import DevConfig

db.session.close

# app.config.from_object(DevConfig)
with app.app_context():
    with db.engine.connect() as con:
        # CHECK

        # LESSONS

        # check sull’orario
        db.sessione.execute(
            """
            ALTER TABLE lessons
            ADD CONSTRAINT check_hour_lessons
            CHECK((_start_hour >= '09:00' AND _start_hour <= '20:00') 
                    AND (_end_hour >= '09:00' AND _end_hour <= '20:00') 
                    AND (_end_hour > _start_hour));
            """)

        # check sui possibili valori di '_mode'
        db.sessione.execute(
            """
            ALTER TABLE lessons
            ADD CONSTRAINT check_mode_lessons
            CHECK(_mode = 'presenza' OR _mode = 'online' OR _mode = 'blended');
            """)

        # USERS

        # check sui possibili valori di '_role'
        db.sessione.execute(
            """
            ALTER TABLE users
            ADD CONSTRAINT check_role_users
            CHECK (_role = 'user' OR _role = 'professor' OR _role = 'admin');
            """)

        # _role = 'professor' → _email = @unive.it
        db.sessione.execute(
            """
            ALTER TABLE users
            ADD CONSTRAINT check_role_professor_email_users
            CHECK (NOT(_role = 'professor') OR (_email LIKE '%@unive.it'));
            """)

        # _role = 'admin' → _email = @segunive.it
        db.sessione.execute(
            """
            ALTER TABLE users
            ADD CONSTRAINT ckeck_role_admin_email_users
            CHECK (NOT(_role = 'admin') OR (_email LIKE '%@segunive.it'));
            """)

        # COURSES

        # check sulla data di inizio e fine
        db.sessione.execute(
            """
            ALTER TABLE courses
            ADD CONSTRAINT check_date_courses
            CHECK(_start_date < _end_date);
            """)

        # check sui possibili valori di '_mode'
        db.sessione.execute(
            """
            ALTER TABLE courses
            ADD CONSTRAINT check_mode_courses
            CHECK(_mode = 'presenza' OR _mode = 'blended' OR _mode = 'online');
            """)

        # check sul numero di studenti
        db.sessione.execute(
            """
            ALTER TABLE courses
            ADD CONSTRAINT check_num_student_courses
            CHECK(_max_student > _min_student AND _min_student >= '10');
            """)

        # TRIGGERS

        # USER_COURSE & USER_LESSON

        # In user_course e user_lesson sono ammessi solo studenti (_role = 'user')
        db.sessione.execute(
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
                BEFORE INSERT OR UPDATE ON user_course
                FOR EACH ROW 
                EXECUTE FUNCTION only_user();

                CREATE TRIGGER OnlyUserLesson
                BEFORE INSERT OR UPDATE ON user_lesson
                FOR EACH ROW 
                EXECUTE FUNCTION only_user();
            """)

        # USER_COURSE

        # Controllare che non si superi il massimo numero di studenti
        db.sessione.execute(
            """
            CREATE FUNCTION no_over_max() RETURNS trigger AS $$
            BEGIN
                IF((SELECT _max_student
                  FROM courses
                  WHERE _course_id = NEW.course_id)
                  <=
                  (SELECT count(*)
                  FROM user_course
                  WHERE course_id = NEW.course_id)) THEN
            RETURN NULL;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

                CREATE TRIGGER NoOverMax
                BEFORE INSERT ON user_course
                FOR EACH ROW
                EXECUTE FUNCTION no_over_max();
            """)

        # USER_LESSON

        # Non ci possono essere studenti in lezioni di corsi che non frequentano
        db.sessione.execute(
            """
            CREATE FUNCTION no_user_in_course() RETURNS trigger AS $$
            BEGIN
                IF( (SELECT course
                   FROM lessons
                   WHERE _lesson_id = NEW.lesson_id) NOT IN (SELECT course_id
            FROM user_course
            WHERE user_id = NEW.user_id)) THEN
                    RETURN NULL;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

                CREATE TRIGGER NoUserInCourse
                BEFORE INSERT ON user_lesson
                FOR EACH ROW
                EXECUTE FUNCTION no_user_in_course();
            """)

        # LESSONS

        # Non si possono aggiungere lezioni se si sta superando l’ammontare di ore prestabilito
        db.sessione.execute(
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

        # Non si possono modificare gli orari delle lezioni se si sta superando l’ammontare di ore prestabilito
        db.sessione.execute(
            """
            CREATE FUNCTION no_lesson_over_m() RETURNS trigger AS $$
            BEGIN
                IF((select sum(l._end_hour-l._start_hour) 
                   from lessons as l 
                   where l.course = NEW.course)
                   > 
                   (select make_interval(hours => co._n_hour) 
                   from courses as co 
                   where co._course_id = NEW.course)) THEN
                    IF(NEW._start_hour <> OLD._start_hour) THEN
                    UPDATE lessons
                    SET _start_hour = OLD._start_hour
                    WHERE _lesson_id = NEW._lesson_id;
                END IF;
                IF(NEW._end_hour <> OLD._end_hour) THEN
                    UPDATE lessons
                        SET _end_hour = OLD._end_hour
                        WHERE _lesson_id = NEW._lesson_id;
                END IF;
                END IF;
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;

                CREATE TRIGGER NoLessonOverM
                AFTER UPDATE ON lessons
                FOR EACH ROW
                EXECUTE FUNCTION no_lesson_over_m();
            """)

        # La data della lezione deve essere dopo la data di inizio e prima della data di fine corso
        db.sessione.execute(
            """
            CREATE FUNCTION correct_dates() RETURNS trigger AS $$
            BEGIN
                IF(NEW._date < (SELECT _start_date FROM courses WHERE NEW.course = _course_id) OR 
                   NEW._date > (SELECT _end_date FROM courses WHERE NEW.course = _course_id) OR
            NEW._date <= current_date) THEN
                    RETURN NULL;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

                CREATE TRIGGER CorrectDates
                BEFORE INSERT OR UPDATE ON lessons
                FOR EACH ROW
                EXECUTE FUNCTION correct_dates();
            """)

        # Non ci possono essere lezioni sovrapposte
        db.sessione.execute(
            """
            CREATE FUNCTION no_lessons_overlying() RETURNS trigger AS $$
            BEGIN
                IF(NEW._date = ANY (SELECT _date
                                     FROM lessons
                                     WHERE (NEW._start_hour <= _start_hour AND NEW._end_hour <= _end_hour AND NEW._end_hour >= _start_hour) OR
                                     (NEW._start_hour >= _start_hour AND NEW._start_hour <= _end_hour AND NEW._end_hour >= _end_hour) OR
                                     (NEW._start_hour >= _start_hour AND NEW._end_hour <= _end_hour) OR
                                     (NEW._start_hour <= _start_hour AND NEW._end_hour >= _end_hour))) THEN
                    RETURN NULL;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

                CREATE TRIGGER NoLessonsOverlying
                BEFORE INSERT ON lessons
                FOR EACH ROW
                EXECUTE FUNCTION no_lessons_overlying();
            """)

        # Una lezione non può superare le 6 ore
        db.sessione.execute(
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

        # Una lezione deve durare almeno un’ora
        db.sessione.execute(
            """
            CREATE FUNCTION limit_min_hours() RETURNS trigger AS $$
            BEGIN
                IF(NEW._end_hour - NEW._start_hour < '01:00') THEN
                    RETURN NULL;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER LimitMinHours
            BEFORE INSERT OR UPDATE ON lessons
            FOR EACH ROW
            EXECUTE FUNCTION limit_min_hours();
            """)

        # La modifica non è valida se almeno una delle condizioni seguenti è vera
        db.sessione.execute(
            """
            CREATE FUNCTION lesson_update() RETURNS trigger AS $$
            BEGIN
                IF(((NEW._mode <> 'presenza' OR NEW._link <> '' OR NEW._structure = '') AND 
                    NEW.course IN (SELECT _course_id FROM courses WHERE _mode = 'presenza'))
                  OR
                  ((NEW._mode <> 'online' OR NEW._link = '' OR NEW._structure <> '') AND 
                    NEW.course IN (SELECT _course_id FROM courses WHERE _mode = 'online'))
                  OR
                  (NEW._mode = 'blended' AND (NEW._link = '' OR NEW._structure = '') AND 
                    NEW.course IN (SELECT _course_id FROM courses WHERE _mode = 'blended'))
                  OR
                  (NEW._mode = 'presenza' AND (NEW._link <> '' OR NEW._structure = '') AND 
                    NEW.course IN (SELECT _course_id FROM courses WHERE _mode = 'blended'))
                  OR
                  (NEW._mode = 'online' AND (NEW._link = '' OR NEW._structure <> '') AND 
                    NEW.course IN (SELECT _course_id FROM courses WHERE _mode = 'blended'))
                  OR 
                  OLD._date <= current_date
                  OR
                  NEW._date <= current_date
                  OR
                  NEW._date < (SELECT _start_date
                              FROM courses
                              WHERE _course_id = NEW.course)
                   OR
                  NEW._date > (SELECT _end_date
                              FROM courses
                              WHERE _course_id = NEW.course)
                  OR
                  NEW._date IN (SELECT _date
                                     FROM lessons AS l
                                     WHERE NEW._lesson_id <> l._lesson_id AND
                                    ((NEW._start_hour <= l._start_hour AND NEW._end_hour <= l._end_hour AND NEW._end_hour >= l._start_hour) OR
                                     (NEW._start_hour >= l._start_hour AND NEW._start_hour <= l._end_hour AND NEW._end_hour >= l._end_hour) OR
                                     (NEW._start_hour >= l._start_hour AND NEW._end_hour <= l._end_hour) OR
                                     (NEW._start_hour <= l._start_hour AND NEW._end_hour >= l._end_hour))))THEN
                    RETURN NULL;
                END IF;
                RETURN NEW;
            END;

            $$ LANGUAGE plpgsql;

                CREATE TRIGGER LessonUpdate
                BEFORE UPDATE ON lessons
                FOR EACH ROW
                EXECUTE FUNCTION lesson_update();
                """)

        # COURSES

        # L’utente associato può essere solo un professore
        db.sessione.execute(
            """
            CREATE FUNCTION only_professor() RETURNS trigger AS $$
            BEGIN
                IF(NEW._professor NOT IN (SELECT _user_id FROM users WHERE _role = 'professor')) THEN
                    RETURN NULL;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER OnlyProfessor
            BEFORE INSERT OR UPDATE ON courses
            FOR EACH ROW
            EXECUTE FUNCTION only_professor();
            """)

        # Il numero massimo di studenti si può solo aumentare
        db.sessione.execute(
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

        # Le ore del corso si possono solo aumentare
        db.sessione.execute(
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

        # La modalità di un corso non si può cambiare
        db.sessione.execute(
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

        # Non è possibile porre la data di inizio del corso prima della data di oggi
        db.sessione.execute(
            """
            CREATE FUNCTION insert_dates() RETURNS trigger AS $$
            BEGIN
                IF(NEW._start_date <= current_date)THEN
                RETURN NULL;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER InsertDates
            BEFORE INSERT ON courses
            FOR EACH ROW
            EXECUTE FUNCTION insert_dates();
            """)

        # Si modifica la data di inizio o di fine solo se non è già passato e se va bene
        db.sessione.execute(
            """
            CREATE FUNCTION modify_dates_update() RETURNS trigger AS $$
            BEGIN
                IF(OLD._start_date <= current_date OR OLD._end_date <= current_date
                OR NEW._start_date <= current_date OR NEW._end_date <= current_date
                OR NEW._start_date > (SELECT min(_date)
                                      FROM lessons
                                      WHERE course = NEW._course_id)
                OR NEW._end_date < (SELECT max(_date)
                                    FROM lessons
                                    WHERE course = NEW._course_id)) THEN
                    RETURN NULL;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

               CREATE TRIGGER ModifyDatesUpdate
               BEFORE UPDATE ON courses
               FOR EACH ROW
               EXECUTE FUNCTION modify_dates_update();
            """)

        db.session.commit()