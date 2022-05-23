from autoapp import app
from dais_pcto.module_extensions import db
from dais_pcto.settings import DevConfig

db.session.close


#app.config.from_object(DevConfig)
with app.app_context():
    with db.engine.connect() as con:

        db.session.execute(
            """
            CREATE FUNCTION only_users() RETURNS trigger AS $$
            BEGIN
                IF(NEW._user_id NOT IN 
                   (SELECT id FROM users WHERE role = 'user')) THEN
                    RETURN NULL;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            CREATE TRIGGER OnlyUsers
            BEFORE INSERT OR UPDATE ON user_corse
            FOR EACH ROW 
            EXECUTE FUNCTION only_users();
            """)

        db.session.execute(
            """
            CREATE FUNCTION no_lesson_over() RETURNS trigger AS $$
            BEGIN
                IF((select sum(l.end_hour-l.start_hour) 
                   from lessons as l 
                   where l.course = NEW.course
                   group by NEW.course)
                   > 
                   (select make_interval(hours => co.n_hour) 
                   from courses as co 
                   where co.id = NEW.course)) THEN
                    DELETE FROM lessons WHERE id = NEW.id;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            CREATE TRIGGER NoLessonOver
            AFTER INSERT ON lessons
            FOR EACH ROW
            EXECUTE FUNCTION no_lesson_over();
            """)

        db.session.execute(
            """
            CREATE FUNCTION no_start_lesson_over_m() RETURNS trigger AS $$
            BEGIN
                IF((select sum(l.end_hour-l.start_hour) 
                   from lessons as l 
                   where l.course = NEW.course
                   group by NEW.course)
                   > 
                   (select make_interval(hours => co.n_hour) 
                   from courses as co 
                   where co.id = NEW.course)) THEN
                    UPDATE lessons
                    SET start_hour = OLD.start_hour
                    WHERE id = NEW.id;
                END IF;
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;
            CREATE TRIGGER nostartlessonoverm
            AFTER UPDATE OF start_hour
            ON lessons
            FOR EACH ROW
            EXECUTE FUNCTION no_start_lesson_over_m();
            """)

        db.session.execute(
            """
            CREATE FUNCTION no_end_lesson_over_m() RETURNS trigger AS $$
            BEGIN
                IF((select sum(l.end_hour-l.start_hour) 
                   from lessons as l 
                   where l.course = NEW.course
                   group by NEW.course)
                   > 
                   (select make_interval(hours => co.n_hour) 
                   from courses as co 
                   where co.id = NEW.course)) THEN
                    UPDATE lessons
                    SET end_hour = OLD.end_hour
                    WHERE id = NEW.id;
                END IF;
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;
            CREATE TRIGGER noendlessonoverm
            AFTER UPDATE OF end_hour
            ON lessons
            FOR EACH ROW
            EXECUTE FUNCTION no_end_lesson_over_m();
            """)

        db.session.execute(
            """
            CREATE FUNCTION correct_dates() RETURNS trigger AS $$
            BEGIN
                IF(NEW.date < (SELECT start_month FROM courses WHERE NEW.course = id) OR 
                   NEW.date > (SELECT end_month FROM courses WHERE NEW.course = id)) THEN
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

        db.session.execute(
            """
            CREATE FUNCTION correct_dates_m() RETURNS trigger AS $$
            BEGIN
                IF(NEW.date < (SELECT start_month FROM courses WHERE NEW.course = id) OR 
                   NEW.date > (SELECT end_month FROM courses WHERE NEW.course = id)) THEN
                    UPDATE lessons
                    SET date = OLD.date
                    WHERE id = NEW.id;
                END IF;
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;
            CREATE TRIGGER correctdatesm
            AFTER UPDATE ON lessons
            FOR EACH ROW
            EXECUTE FUNCTION correct_dates_m();
            """)

        db.session.execute(
            """
            CREATE FUNCTION no_lessons_overlying() RETURNS trigger AS $$
            BEGIN
                IF(NEW.date = ANY (SELECT date
                                     FROM lessons
                                     WHERE (NEW.start_hour <= start_hour AND NEW.end_hour <= end_hour) OR
                                     (NEW.start_hour >= start_hour AND NEW.end_hour >= end_hour) OR
                                     (NEW.start_hour >= start_hour AND NEW.end_hour <= end_hour) OR
                                     (NEW.start_hour <= start_hour AND NEW.end_hour >= end_hour))) THEN
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

        db.session.execute(
            """
            CREATE FUNCTION only_professor() RETURNS trigger AS $$
            BEGIN
                IF(NEW.professor NOT IN (SELECT id FROM users WHERE role = 'professor')) THEN
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

        db.session.execute(
            """
            ALTER TABLE lessons
            ADD CHECK((mode = '2' AND structure = 'vuoto') OR
                     ((mode = '1' OR mode = '3') AND structure <> 'vuoto'));
            """)

        db.session.execute(
            """
            ALTER TABLE lessons
            ADD CHECK((mode = '1' AND link = 'vuoto') OR
                     ((mode = '2' OR mode = '3') AND link <> 'vuoto'));
            """)

        db.session.execute(
            """
            ALTER TABLE lessons
            ADD CHECK(start_hour >= '09:00' AND start_hour <= '20:00' 
                                 AND end_hour >= '09:00' AND end_hour <= '20:00' 
                                 AND end_hour > start_hour);
            """)

        db.session.execute(
            """
            ALTER TABLE lessons
            ADD CHECK(mode = '1' OR mode = '2' OR mode = '3');
            """)

        db.session.execute(
            """
            ALTER TABLE lessons
            ADD CHECK(date > current_date);
            """)

        db.session.execute(
            """
            ALTER TABLE users
            ADD CHECK (role = 'user' OR role = 'professor' OR role = 'admin');
            """)

        db.session.execute(
            """
           ALTER TABLE courses
            ADD CHECK((start_month <= '2022/06/30' OR start_month >= '2022/09/01') 
                      AND (end_month <= '2022/06/30' OR end_month >= '2022/09/01') 
                      AND (start_month < end_month) AND 
                      NOT (start_month < '2022/07/01' AND end_month > '2022/08/31'));
            """)

        db.session.execute(
            """
            ALTER TABLE courses
            ADD CHECK(mode = 'presenza' OR mode = 'blended' OR mode = 'online');
            """)

        db.session.execute(
            """
            ALTER TABLE courses
            ADD CHECK(max_student > min_student);
            """)

        db.session.execute(
            """
            ALTER TABLE courses
            ADD CHECK(min_student >= '10');
            """)

        db.session.execute(
            """
            ALTER TABLE courses
            ADD CHECK(start_month > current_date);
            """)

        db.session.commit()