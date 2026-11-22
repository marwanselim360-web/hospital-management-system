-- =====================================================
-- HOSPITAL MANAGEMENT SYSTEM DATABASE
-- Clean, consistent, professor-ready version
-- =====================================================
-- This script rebuilds the whole hospital database from scratch.
-- It includes:
-- 1) Clean tables and constraints
-- 2) Realistic sample data
-- 3) Doctor working days and days off
-- 4) Valid appointments that match doctor days and shifts
-- 5) Room/admission consistency
-- 6) Views for reports
-- 7) Triggers to prevent future invalid data
-- 8) Practice queries for project discussion
-- =====================================================

DROP DATABASE IF EXISTS hospital;
CREATE DATABASE hospital;
USE hospital;

-- =====================================================
-- BLOCK 1: CORE TABLES
-- This block creates the main hospital entities.
-- =====================================================

CREATE TABLE department (
    dep_id SMALLINT UNSIGNED NOT NULL,
    name VARCHAR(40) NOT NULL UNIQUE,
    location VARCHAR(50),
    head_doctor VARCHAR(50),
    PRIMARY KEY (dep_id)
);

CREATE TABLE staff (
    ssn SMALLINT UNSIGNED NOT NULL,
    name VARCHAR(50) NOT NULL,
    phone_num VARCHAR(15),
    dep_id SMALLINT UNSIGNED,
    PRIMARY KEY (ssn),
    FOREIGN KEY (dep_id) REFERENCES department(dep_id)
);

CREATE TABLE doctor (
    essn SMALLINT UNSIGNED NOT NULL,
    email VARCHAR(80) NOT NULL UNIQUE,
    specialization VARCHAR(80) NOT NULL DEFAULT 'General',
    shift ENUM('morning','afternoon','night') NOT NULL,
    PRIMARY KEY (essn),
    FOREIGN KEY (essn) REFERENCES staff(ssn)
);

CREATE TABLE nurse (
    essn SMALLINT UNSIGNED NOT NULL,
    shift ENUM('morning','afternoon','night') NOT NULL,
    PRIMARY KEY (essn),
    FOREIGN KEY (essn) REFERENCES staff(ssn)
);

CREATE TABLE patient (
    patient_id SMALLINT UNSIGNED NOT NULL,
    name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    blood_type ENUM('A+','A-','B+','B-','AB+','AB-','O+','O-') NOT NULL,
    phone_num VARCHAR(15),
    gender ENUM('male','female') NOT NULL,
    address VARCHAR(100),
    PRIMARY KEY (patient_id)
);

CREATE TABLE medication (
    med_id SMALLINT UNSIGNED NOT NULL,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(120),
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    PRIMARY KEY (med_id)
);

CREATE TABLE room (
    room_id SMALLINT UNSIGNED NOT NULL,
    room_cost DECIMAL(10,2) NOT NULL CHECK (room_cost > 0),
    capacity INT NOT NULL CHECK (capacity > 0),
    room_num INT NOT NULL UNIQUE,
    status ENUM('Available','Occupied','Reserved','Under Maintenance') NOT NULL DEFAULT 'Available',
    PRIMARY KEY (room_id)
);

CREATE TABLE admin (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(50) NOT NULL
);

-- =====================================================
-- BLOCK 2: OPERATIONAL TABLES
-- These tables store appointments, tests, prescriptions, payments, and admissions.
-- =====================================================

CREATE TABLE appointment (
    appointment_id INT AUTO_INCREMENT,
    patient_id SMALLINT UNSIGNED NOT NULL,
    doctor_id SMALLINT UNSIGNED NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status ENUM('Pending','Completed','Cancelled','Scheduled') NOT NULL DEFAULT 'Scheduled',
    PRIMARY KEY (appointment_id),
    UNIQUE (doctor_id, appointment_date, appointment_time),
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctor(essn)
);

CREATE TABLE payment (
    payment_id SMALLINT UNSIGNED AUTO_INCREMENT,
    patient_id SMALLINT UNSIGNED NOT NULL,
    payment_date DATE NOT NULL,
    status ENUM('Paid','Pending','Unpaid') NOT NULL,
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    method ENUM('Cash','Card','Insurance','Online') NOT NULL,
    PRIMARY KEY (payment_id),
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id)
);

CREATE TABLE test (
    test_id SMALLINT UNSIGNED AUTO_INCREMENT,
    test_type VARCHAR(50) NOT NULL,
    test_date DATE NOT NULL,
    result VARCHAR(80),
    appointment_id INT NOT NULL,
    PRIMARY KEY (test_id),
    FOREIGN KEY (appointment_id) REFERENCES appointment(appointment_id)
);

CREATE TABLE prescribed (
    patient_id SMALLINT UNSIGNED NOT NULL,
    med_id SMALLINT UNSIGNED NOT NULL,
    amount INT NOT NULL CHECK (amount > 0),
    PRIMARY KEY (patient_id, med_id),
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (med_id) REFERENCES medication(med_id)
);

CREATE TABLE admission (
    admission_id SMALLINT UNSIGNED NOT NULL,
    admit_date DATE NOT NULL,
    discharged_date DATE NULL,
    notes VARCHAR(120),
    patient_id SMALLINT UNSIGNED NOT NULL,
    room_id SMALLINT UNSIGNED NOT NULL,
    PRIMARY KEY (admission_id),
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (room_id) REFERENCES room(room_id),
    CHECK (discharged_date IS NULL OR discharged_date >= admit_date)
);

CREATE TABLE nurse_patient (
    nurse_id SMALLINT UNSIGNED NOT NULL,
    patient_id SMALLINT UNSIGNED NOT NULL,
    assigned_by SMALLINT UNSIGNED NOT NULL,
    assigned_date DATE NOT NULL,
    PRIMARY KEY (nurse_id, patient_id),
    FOREIGN KEY (nurse_id) REFERENCES nurse(essn),
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (assigned_by) REFERENCES doctor(essn)
);


-- =====================================================
-- BLOCK 3: SCHEDULING AND PRICING TABLES
-- These tables make appointment booking realistic.
-- =====================================================

CREATE TABLE doctor_working_day (
    doctor_id SMALLINT UNSIGNED NOT NULL,
    day_name ENUM('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday') NOT NULL,
    PRIMARY KEY (doctor_id, day_name),
    FOREIGN KEY (doctor_id) REFERENCES doctor(essn)
);

CREATE TABLE doctor_day_off (
    off_id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_id SMALLINT UNSIGNED NOT NULL,
    off_date DATE NOT NULL,
    reason VARCHAR(150),
    UNIQUE (doctor_id, off_date),
    FOREIGN KEY (doctor_id) REFERENCES doctor(essn)
);

CREATE TABLE patient_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id SMALLINT UNSIGNED NOT NULL,
    doctor_id SMALLINT UNSIGNED NULL,
    record_date DATE NOT NULL,
    diagnosis VARCHAR(150),
    treatment VARCHAR(150),
    notes VARCHAR(255),
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctor(essn)
);

CREATE TABLE test_price (
    test_type VARCHAR(50) PRIMARY KEY,
    price DECIMAL(10,2) NOT NULL CHECK (price > 0)
);

-- =====================================================
-- BLOCK 4: DEPARTMENTS
-- This block inserts hospital departments.
-- =====================================================

INSERT INTO department (dep_id, name, location, head_doctor) VALUES
(1, 'Cardiology', 'First Floor', 'Dr. Ahmed Hassan'),
(2, 'Neurology', 'Second Floor', 'Dr. Salma Adel'),
(3, 'Pediatrics', 'Third Floor', 'Dr. Mona Youssef'),
(4, 'Orthopedics', 'Fourth Floor', 'Dr. Karim Nabil'),
(5, 'Emergency', 'Ground Floor', 'Dr. Omar Tarek'),
(6, 'Dermatology', 'Fifth Floor', 'Dr. Noura Gamal'),
(7, 'Ophthalmology', 'Sixth Floor', 'Dr. Sherif Lotfy'),
(8, 'ENT', 'Seventh Floor', 'Dr. Mai Hossam'),
(9, 'Dentistry', 'Eighth Floor', 'Dr. Yara Fathy'),
(10, 'Psychiatry', 'Ninth Floor', 'Dr. Basel Samir'),
(11, 'Gynecology', 'Tenth Floor', 'Dr. Rania Fouad'),
(12, 'Urology', 'Eleventh Floor', 'Dr. Mostafa Galal');

-- =====================================================
-- BLOCK 5: STAFF, DOCTORS, AND NURSES
-- Doctors and nurses are staff members first, then specialized into roles.
-- =====================================================

INSERT INTO staff (ssn, name, phone_num, dep_id) VALUES
(101, 'Ahmed Hassan', '01011111111', 1),
(102, 'Salma Adel', '01022222222', 2),
(103, 'Mona Youssef', '01033333333', 3),
(104, 'Karim Nabil', '01044444444', 4),
(105, 'Omar Tarek', '01055555555', 5),
(106, 'Nour Emad', '01066666666', 1),
(107, 'Laila Mostafa', '01077777777', 2),
(108, 'Heba Samir', '01088888888', 3),
(109, 'Yasmine Ali', '01099999999', 4),
(110, 'Farah Hany', '01100000000', 5),
(111, 'Hany Magdy', '01111111111', 1),
(112, 'Reem Ashraf', '01122222222', 2),
(113, 'Tamer Fouad', '01133333333', 3),
(114, 'Dina Sherif', '01144444444', 4),
(115, 'Mahmoud Saeed', '01155555555', 5),
(116, 'Nada Sameh', '01166666666', 1),
(117, 'Aya Nasser', '01177777777', 2),
(118, 'Maged Adel', '01188888888', 3),
(119, 'Rana Yasser', '01199999999', 4),
(120, 'Khaled Mostafa', '01200000000', 5),
(121, 'Noura Gamal', '01211111111', 6),
(122, 'Sherif Lotfy', '01222222222', 7),
(123, 'Mai Hossam', '01233333333', 8),
(124, 'Yara Fathy', '01244444444', 9),
(125, 'Basel Samir', '01255555555', 10),
(126, 'Rania Fouad', '01266666666', 11),
(127, 'Mostafa Galal', '01277777777', 12),
(128, 'Heba Mourad', '01288888888', 6),
(129, 'Tarek Amin', '01299999999', 7),
(130, 'Lobna Adel', '01500000000', 8),
(131, 'Mona Fawzy', '01511111111', 1),
(132, 'Omar Shalaby', '01522222222', 1),
(133, 'Heba Younis', '01533333333', 2),
(134, 'Karim Samir', '01544444444', 2),
(135, 'Nadine Farouk', '01555555555', 3),
(136, 'Youssef Maher', '01566666666', 3),
(137, 'Salma Raouf', '01577777777', 4),
(138, 'Mostafa Nader', '01588888888', 4),
(139, 'Farah Galal', '01599999999', 5),
(140, 'Hossam Reda', '01010101010', 5),
(141, 'Noha Adel', '01020202020', 6),
(142, 'Amr Fouad', '01030303030', 6),
(143, 'Laila Hassan', '01040404040', 7),
(144, 'Sherif Amin', '01050505050', 7),
(145, 'Dina Mourad', '01060606060', 8),
(146, 'Tarek Saad', '01070707070', 8),
(147, 'Rana Osama', '01080808080', 9),
(148, 'Ahmed Gamal', '01090909090', 10),
(149, 'Mai Ezz', '01110101010', 11),
(150, 'Khaled Salem', '01120202020', 12);

INSERT INTO doctor (essn, email, specialization, shift) VALUES
(101, 'ahmed.hassan@hospital.com', 'Cardiology', 'morning'),
(102, 'salma.adel@hospital.com', 'Neurology', 'afternoon'),
(103, 'mona.youssef@hospital.com', 'Pediatrics', 'morning'),
(104, 'karim.nabil@hospital.com', 'Orthopedics', 'night'),
(105, 'omar.tarek@hospital.com', 'Emergency Medicine', 'night'),
(111, 'hany.magdy@hospital.com', 'Cardiology', 'afternoon'),
(112, 'reem.ashraf@hospital.com', 'Neurology', 'morning'),
(113, 'tamer.fouad@hospital.com', 'Pediatrics', 'night'),
(114, 'dina.sherif@hospital.com', 'Orthopedics', 'afternoon'),
(115, 'mahmoud.saeed@hospital.com', 'Emergency Medicine', 'morning'),
(121, 'noura.gamal@hospital.com', 'Dermatology', 'morning'),
(122, 'sherif.lotfy@hospital.com', 'Ophthalmology', 'afternoon'),
(123, 'mai.hossam@hospital.com', 'ENT', 'morning'),
(124, 'yara.fathy@hospital.com', 'Dentistry', 'afternoon'),
(125, 'basel.samir@hospital.com', 'Psychiatry', 'night'),
(126, 'rania.fouad@hospital.com', 'Gynecology', 'morning'),
(127, 'mostafa.galal@hospital.com', 'Urology', 'afternoon'),
(128, 'heba.mourad@hospital.com', 'Dermatology', 'night'),
(129, 'tarek.amin@hospital.com', 'Ophthalmology', 'morning'),
(130, 'lobna.adel@hospital.com', 'ENT', 'night'),
(131, 'mona.fawzy@hospital.com', 'Cardiology', 'morning'),
(132, 'omar.shalaby@hospital.com', 'Cardiology', 'night'),
(133, 'heba.younis@hospital.com', 'Neurology', 'afternoon'),
(134, 'karim.samir@hospital.com', 'Neurology', 'night'),
(135, 'nadine.farouk@hospital.com', 'Pediatrics', 'morning'),
(136, 'youssef.maher@hospital.com', 'Pediatrics', 'afternoon'),
(137, 'salma.raouf@hospital.com', 'Orthopedics', 'morning'),
(138, 'mostafa.nader@hospital.com', 'Orthopedics', 'night'),
(139, 'farah.galal@hospital.com', 'Emergency Medicine', 'afternoon'),
(140, 'hossam.reda@hospital.com', 'Emergency Medicine', 'night'),
(141, 'noha.adel@hospital.com', 'Dermatology', 'afternoon'),
(142, 'amr.fouad@hospital.com', 'Dermatology', 'morning'),
(143, 'laila.hassan@hospital.com', 'Ophthalmology', 'night'),
(144, 'sherif.amin@hospital.com', 'Ophthalmology', 'afternoon'),
(145, 'dina.mourad@hospital.com', 'ENT', 'afternoon'),
(146, 'tarek.saad@hospital.com', 'ENT', 'morning'),
(147, 'rana.osama@hospital.com', 'Dentistry', 'morning'),
(148, 'ahmed.gamal@hospital.com', 'Psychiatry', 'afternoon'),
(149, 'mai.ezz@hospital.com', 'Gynecology', 'afternoon'),
(150, 'khaled.salem@hospital.com', 'Urology', 'morning');

INSERT INTO nurse (essn, shift) VALUES
(106, 'morning'),
(107, 'afternoon'),
(108, 'night'),
(109, 'morning'),
(110, 'night'),
(116, 'morning'),
(117, 'afternoon'),
(118, 'night'),
(119, 'morning'),
(120, 'night');

-- =====================================================
-- BLOCK 6: DOCTOR WORKING DAYS AND DAYS OFF
-- These rows must be inserted BEFORE appointments so triggers can validate schedules.
-- =====================================================

-- Most core doctors work Sunday to Thursday.
INSERT INTO doctor_working_day (doctor_id, day_name)
SELECT essn, 'Sunday' FROM doctor WHERE essn BETWEEN 101 AND 130
UNION ALL SELECT essn, 'Monday' FROM doctor WHERE essn BETWEEN 101 AND 130
UNION ALL SELECT essn, 'Tuesday' FROM doctor WHERE essn BETWEEN 101 AND 130
UNION ALL SELECT essn, 'Wednesday' FROM doctor WHERE essn BETWEEN 101 AND 130
UNION ALL SELECT essn, 'Thursday' FROM doctor WHERE essn BETWEEN 101 AND 130;

-- Extra doctors have varied schedules to make availability/load-balancing realistic.
INSERT INTO doctor_working_day (doctor_id, day_name) VALUES
(131,'Monday'),(131,'Tuesday'),(131,'Wednesday'),(131,'Thursday'),(131,'Saturday'),
(132,'Sunday'),(132,'Monday'),(132,'Wednesday'),(132,'Thursday'),(132,'Friday'),
(133,'Monday'),(133,'Tuesday'),(133,'Thursday'),(133,'Saturday'),
(134,'Sunday'),(134,'Tuesday'),(134,'Wednesday'),(134,'Friday'),
(135,'Sunday'),(135,'Monday'),(135,'Tuesday'),(135,'Wednesday'),(135,'Thursday'),
(136,'Monday'),(136,'Wednesday'),(136,'Thursday'),(136,'Saturday'),
(137,'Sunday'),(137,'Tuesday'),(137,'Wednesday'),(137,'Thursday'),
(138,'Monday'),(138,'Tuesday'),(138,'Friday'),(138,'Saturday'),
(139,'Sunday'),(139,'Monday'),(139,'Tuesday'),(139,'Wednesday'),(139,'Thursday'),(139,'Friday'),
(140,'Sunday'),(140,'Monday'),(140,'Wednesday'),(140,'Friday'),(140,'Saturday'),
(141,'Monday'),(141,'Tuesday'),(141,'Thursday'),(141,'Saturday'),
(142,'Sunday'),(142,'Monday'),(142,'Wednesday'),(142,'Thursday'),
(143,'Monday'),(143,'Wednesday'),(143,'Friday'),(143,'Saturday'),
(144,'Sunday'),(144,'Tuesday'),(144,'Wednesday'),(144,'Thursday'),
(145,'Monday'),(145,'Tuesday'),(145,'Thursday'),(145,'Saturday'),
(146,'Sunday'),(146,'Monday'),(146,'Wednesday'),(146,'Friday'),
(147,'Sunday'),(147,'Tuesday'),(147,'Thursday'),(147,'Saturday'),
(148,'Monday'),(148,'Wednesday'),(148,'Thursday'),(148,'Friday'),
(149,'Sunday'),(149,'Monday'),(149,'Tuesday'),(149,'Wednesday'),
(150,'Monday'),(150,'Tuesday'),(150,'Thursday'),(150,'Saturday');

-- Days off are chosen so they do NOT conflict with sample appointments.
INSERT INTO doctor_day_off (doctor_id, off_date, reason) VALUES
(101, '2026-05-12', 'Cardiology conference'),
(112, '2026-05-13', 'Personal leave'),
(124, '2026-05-15', 'Dental training day'),
(139, '2026-05-20', 'Emergency workshop');

-- =====================================================
-- BLOCK 7: TRIGGERS FOR DATA INTEGRITY
-- These triggers stop invalid appointments and room overbooking.
-- =====================================================

DELIMITER //

CREATE TRIGGER check_doctor_schedule_before_insert
BEFORE INSERT ON appointment
FOR EACH ROW
BEGIN
    DECLARE doctor_shift VARCHAR(20);
    DECLARE valid_day INT DEFAULT 0;
    DECLARE day_off_count INT DEFAULT 0;

    SELECT shift INTO doctor_shift
    FROM doctor
    WHERE essn = NEW.doctor_id;

    SELECT COUNT(*) INTO valid_day
    FROM doctor_working_day
    WHERE doctor_id = NEW.doctor_id
      AND day_name = DAYNAME(NEW.appointment_date);

    IF valid_day = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid appointment: doctor does not work on this day';
    END IF;

    SELECT COUNT(*) INTO day_off_count
    FROM doctor_day_off
    WHERE doctor_id = NEW.doctor_id
      AND off_date = NEW.appointment_date;

    IF day_off_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid appointment: doctor is on day off';
    END IF;

    IF doctor_shift = 'morning' AND NOT (NEW.appointment_time BETWEEN '08:00:00' AND '12:59:59') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid appointment: time is outside morning shift';
    END IF;

    IF doctor_shift = 'afternoon' AND NOT (NEW.appointment_time BETWEEN '13:00:00' AND '17:59:59') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid appointment: time is outside afternoon shift';
    END IF;

    IF doctor_shift = 'night' AND NOT (NEW.appointment_time BETWEEN '18:00:00' AND '23:00:00') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid appointment: time is outside night shift';
    END IF;
END //

CREATE TRIGGER check_doctor_schedule_before_update
BEFORE UPDATE ON appointment
FOR EACH ROW
BEGIN
    DECLARE doctor_shift VARCHAR(20);
    DECLARE valid_day INT DEFAULT 0;
    DECLARE day_off_count INT DEFAULT 0;

    SELECT shift INTO doctor_shift
    FROM doctor
    WHERE essn = NEW.doctor_id;

    SELECT COUNT(*) INTO valid_day
    FROM doctor_working_day
    WHERE doctor_id = NEW.doctor_id
      AND day_name = DAYNAME(NEW.appointment_date);

    IF valid_day = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid update: doctor does not work on this day';
    END IF;

    SELECT COUNT(*) INTO day_off_count
    FROM doctor_day_off
    WHERE doctor_id = NEW.doctor_id
      AND off_date = NEW.appointment_date;

    IF day_off_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid update: doctor is on day off';
    END IF;

    IF doctor_shift = 'morning' AND NOT (NEW.appointment_time BETWEEN '08:00:00' AND '12:59:59') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid update: time is outside morning shift';
    END IF;

    IF doctor_shift = 'afternoon' AND NOT (NEW.appointment_time BETWEEN '13:00:00' AND '17:59:59') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid update: time is outside afternoon shift';
    END IF;

    IF doctor_shift = 'night' AND NOT (NEW.appointment_time BETWEEN '18:00:00' AND '23:00:00') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid update: time is outside night shift';
    END IF;
END //

CREATE TRIGGER prevent_room_overbooking_before_insert
BEFORE INSERT ON admission
FOR EACH ROW
BEGIN
    DECLARE current_patients INT DEFAULT 0;
    DECLARE max_capacity INT DEFAULT 0;
    DECLARE room_current_status VARCHAR(30);

    SELECT capacity, status INTO max_capacity, room_current_status
    FROM room
    WHERE room_id = NEW.room_id;

    IF room_current_status = 'Under Maintenance' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid admission: room is under maintenance';
    END IF;

    SELECT COUNT(*) INTO current_patients
    FROM admission
    WHERE room_id = NEW.room_id
      AND discharged_date IS NULL;

    IF current_patients >= max_capacity THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid admission: room is already full';
    END IF;
END //

CREATE TRIGGER set_room_occupied_after_admission_insert
AFTER INSERT ON admission
FOR EACH ROW
BEGIN
    UPDATE room
    SET status = 'Occupied'
    WHERE room_id = NEW.room_id;
END //

CREATE TRIGGER update_room_status_after_admission_update
AFTER UPDATE ON admission
FOR EACH ROW
BEGIN
    IF NEW.discharged_date IS NOT NULL THEN
        IF (SELECT COUNT(*) FROM admission WHERE room_id = NEW.room_id AND discharged_date IS NULL) = 0 THEN
            UPDATE room
            SET status = 'Available'
            WHERE room_id = NEW.room_id;
        END IF;
    END IF;
END //

DELIMITER ;

-- =====================================================
-- BLOCK 8: PATIENTS
-- This block inserts realistic patients with valid blood types and contact data.
-- =====================================================

INSERT INTO patient (patient_id, name, date_of_birth, blood_type, phone_num, gender, address) VALUES
(201, 'Sara Mohamed', '2002-05-14', 'A+', '01012345678', 'female', 'Nasr City, Cairo'),
(202, 'Youssef Khaled', '1998-11-02', 'O+', '01123456789', 'male', 'Heliopolis, Cairo'),
(203, 'Mariam Adel', '2005-03-21', 'B+', '01234567890', 'female', 'Mokattam, Cairo'),
(204, 'Omar Samy', '1995-07-09', 'AB-', '01545678901', 'male', 'Maadi, Cairo'),
(205, 'Lina Tamer', '2010-12-30', 'A-', '01056789012', 'female', 'Zamalek, Cairo'),
(206, 'Hassan Wael', '1987-09-17', 'O-', '01167890123', 'male', 'Dokki, Giza'),
(207, 'Nadine Fathy', '2001-01-25', 'B-', '01278901234', 'female', 'Shoubra, Cairo'),
(208, 'Mostafa Nader', '1993-04-18', 'AB+', '01589012345', 'male', '6th October, Giza'),
(209, 'Habiba Mostafa', '2000-06-12', 'A+', '01011112222', 'female', 'New Cairo, Cairo'),
(210, 'Ali Hossam', '1997-02-19', 'O+', '01122223333', 'male', 'Madinaty, Cairo'),
(211, 'Malak Yasser', '2004-08-05', 'B+', '01233334444', 'female', 'Rehab, Cairo'),
(212, 'Seif Amr', '1992-10-14', 'AB+', '01544445555', 'male', 'Nasr City, Cairo'),
(213, 'Jana Kareem', '2012-01-03', 'A-', '01055556666', 'female', 'Heliopolis, Cairo'),
(214, 'Yassin Tarek', '1989-09-25', 'O-', '01166667777', 'male', 'Maadi, Cairo'),
(215, 'Laila Ashraf', '2001-04-30', 'B-', '01277778888', 'female', 'Mokattam, Cairo'),
(216, 'Adam Sherif', '1995-12-11', 'AB-', '01588889999', 'male', 'Dokki, Giza'),
(217, 'Nourhan Adel', '1999-07-22', 'A+', '01099990000', 'female', 'Zamalek, Cairo'),
(218, 'Omar Hisham', '2003-03-17', 'O+', '01100001111', 'male', '6th October, Giza'),
(219, 'Farida Nabil', '2006-11-09', 'B+', '01211110000', 'female', 'Shoubra, Cairo'),
(220, 'Ziad Wael', '1994-05-29', 'A-', '01522221111', 'male', 'El Shorouk, Cairo'),
(221, 'Mariam Tarek', '2002-03-15', 'A+', '01012341234', 'female', 'New Cairo, Cairo'),
(222, 'Youssef Adel', '1998-11-20', 'O+', '01123452345', 'male', 'Nasr City, Cairo'),
(223, 'Salma Hany', '2005-07-09', 'B+', '01234563456', 'female', 'Heliopolis, Cairo'),
(224, 'Karim Nabil', '1993-02-28', 'AB+', '01545674567', 'male', 'Maadi, Cairo'),
(225, 'Nadine Omar', '2001-09-12', 'A-', '01056785678', 'female', 'Zamalek, Cairo'),
(226, 'Hassan Ali', '1987-05-05', 'O-', '01167896789', 'male', 'Giza'),
(227, 'Farah Sameh', '2004-12-01', 'B-', '01278907890', 'female', 'Shorouk, Cairo'),
(228, 'Mostafa Khaled', '1990-08-22', 'AB-', '01589018901', 'male', '6th October, Giza'),
(229, 'Dalia Ibrahim', '1996-04-18', 'A+', '01090129012', 'female', 'Mokattam, Cairo'),
(230, 'Amr Fathy', '1985-10-30', 'O+', '01101230123', 'male', 'Dokki, Giza');

-- =====================================================
-- BLOCK 9: APPOINTMENTS
-- Every appointment below matches the doctor's working day and shift.
-- Morning: 08:00-12:59 | Afternoon: 13:00-17:59 | Night: 18:00-23:00
-- =====================================================

INSERT INTO appointment (appointment_id, patient_id, doctor_id, appointment_date, appointment_time, status) VALUES
(1, 201, 101, '2026-05-10', '09:00:00', 'Completed'),
(2, 202, 102, '2026-05-10', '13:30:00', 'Completed'),
(3, 203, 103, '2026-05-11', '10:00:00', 'Pending'),
(4, 204, 104, '2026-05-11', '19:00:00', 'Completed'),
(5, 205, 103, '2026-05-12', '11:00:00', 'Cancelled'),
(6, 206, 105, '2026-05-12', '20:00:00', 'Completed'),
(7, 207, 101, '2026-05-13', '10:30:00', 'Pending'),
(8, 208, 104, '2026-05-13', '20:30:00', 'Scheduled'),
(9, 209, 111, '2026-05-10', '14:00:00', 'Scheduled'),
(10, 210, 112, '2026-05-10', '09:30:00', 'Scheduled'),
(11, 211, 113, '2026-05-11', '18:30:00', 'Pending'),
(12, 212, 114, '2026-05-11', '15:00:00', 'Completed'),
(13, 213, 113, '2026-05-12', '19:30:00', 'Scheduled'),
(14, 214, 115, '2026-05-12', '09:00:00', 'Completed'),
(15, 215, 111, '2026-05-13', '14:30:00', 'Pending'),
(16, 216, 114, '2026-05-13', '16:00:00', 'Scheduled'),
(17, 217, 121, '2026-05-14', '09:00:00', 'Completed'),
(18, 218, 122, '2026-05-14', '13:30:00', 'Scheduled'),
(19, 219, 123, '2026-05-14', '11:00:00', 'Pending'),
(20, 220, 105, '2026-05-14', '21:00:00', 'Completed'),
(21, 221, 121, '2026-05-10', '10:00:00', 'Scheduled'),
(22, 222, 128, '2026-05-11', '19:00:00', 'Scheduled'),
(23, 223, 122, '2026-05-11', '13:00:00', 'Scheduled'),
(24, 224, 129, '2026-05-12', '10:00:00', 'Scheduled'),
(25, 225, 123, '2026-05-12', '09:00:00', 'Scheduled'),
(26, 226, 130, '2026-05-13', '18:00:00', 'Scheduled'),
(27, 227, 124, '2026-05-13', '14:00:00', 'Scheduled'),
(28, 228, 125, '2026-05-13', '20:00:00', 'Scheduled'),
(29, 229, 126, '2026-05-14', '09:00:00', 'Scheduled'),
(30, 230, 127, '2026-05-14', '13:00:00', 'Scheduled'),
(31, 209, 131, '2026-05-16', '09:30:00', 'Scheduled'),
(32, 210, 132, '2026-05-15', '18:30:00', 'Scheduled'),
(33, 211, 133, '2026-05-16', '13:30:00', 'Scheduled'),
(34, 212, 134, '2026-05-15', '19:30:00', 'Pending'),
(35, 213, 135, '2026-05-17', '10:30:00', 'Scheduled'),
(36, 214, 137, '2026-05-17', '11:30:00', 'Completed'),
(37, 215, 141, '2026-05-18', '14:30:00', 'Scheduled'),
(38, 216, 145, '2026-05-18', '15:30:00', 'Scheduled'),
(39, 217, 147, '2026-05-19', '09:30:00', 'Pending'),
(40, 218, 150, '2026-05-19', '10:30:00', 'Scheduled');

-- Reset auto-increment so future GUI-created appointments continue after sample IDs.
ALTER TABLE appointment AUTO_INCREMENT = 41;

-- =====================================================
-- BLOCK 10: TESTS AND TEST PRICES
-- Tests are linked only to real appointments.
-- No tests are linked to cancelled appointments.
-- =====================================================

INSERT INTO test_price (test_type, price) VALUES
('Blood Test', 180.00),
('X-Ray', 350.00),
('MRI', 1500.00),
('CT Scan', 1200.00),
('Urine Test', 150.00),
('ECG', 400.00),
('Blood Sugar', 120.00),
('Skin Test', 300.00),
('Eye Exam', 250.00),
('Hearing Test', 280.00),
('Dental X-Ray', 450.00),
('Ultrasound', 700.00);

INSERT INTO test (test_type, test_date, result, appointment_id) VALUES
('ECG', '2026-05-10', 'Normal', 1),
('MRI', '2026-05-10', 'Minor Issue', 2),
('X-Ray', '2026-05-11', 'Fracture Detected', 4),
('Blood Sugar', '2026-05-12', 'High', 6),
('Blood Test', '2026-05-13', 'Normal', 7),
('ECG', '2026-05-14', 'Normal', 20),
('Skin Test', '2026-05-10', 'Allergy detected', 21),
('Eye Exam', '2026-05-11', 'Weak vision', 23),
('Hearing Test', '2026-05-12', 'Normal', 25),
('Dental X-Ray', '2026-05-13', 'Clear', 27),
('Blood Test', '2026-05-16', 'Normal', 31),
('CT Scan', '2026-05-17', 'Minor Issue', 36);

-- =====================================================
-- BLOCK 11: MEDICATIONS AND PRESCRIPTIONS
-- Medication names are in English so AI can translate Arabic queries into English DB values.
-- =====================================================

INSERT INTO medication (med_id, name, description, price) VALUES
(301, 'Paracetamol', 'Pain reliever and fever reducer', 25.00),
(302, 'Amoxicillin', 'Antibiotic for bacterial infections', 80.00),
(303, 'Ibuprofen', 'Anti-inflammatory painkiller', 45.00),
(304, 'Omeprazole', 'Reduces stomach acid', 60.00),
(305, 'Insulin', 'Used to control blood sugar', 150.00),
(306, 'Vitamin D', 'Supplement for vitamin D deficiency', 70.00),
(307, 'Cough Syrup', 'Used for cough relief', 55.00),
(308, 'Aspirin', 'Pain reliever and blood thinner', 35.00),
(309, 'Cetirizine', 'Allergy medication', 40.00),
(310, 'Metformin', 'Used for diabetes control', 95.00),
(311, 'Calcium', 'Bone health supplement', 65.00),
(312, 'Azithromycin', 'Antibiotic medication', 120.00);

INSERT INTO prescribed (patient_id, med_id, amount) VALUES
(201, 301, 2),
(202, 304, 1),
(203, 306, 1),
(204, 303, 3),
(205, 301, 1),
(206, 305, 2),
(207, 302, 1),
(208, 303, 2),
(209, 308, 1),
(210, 309, 2),
(211, 307, 1),
(212, 311, 2),
(213, 301, 1),
(214, 310, 2),
(215, 302, 1),
(216, 303, 2),
(217, 304, 1),
(218, 305, 1),
(219, 306, 2),
(220, 312, 1),
(221, 307, 1),
(223, 309, 2),
(225, 308, 1),
(227, 301, 1),
(228, 310, 2),
(229, 311, 1),
(230, 312, 1);

-- =====================================================
-- BLOCK 12: ROOMS AND ADMISSIONS
-- Active admissions automatically mark rooms as Occupied through the trigger.
-- Rooms under maintenance are never used for admission.
-- =====================================================

INSERT INTO room (room_id, room_cost, capacity, room_num, status) VALUES
(401, 1500.00, 1, 101, 'Available'),
(402, 1200.00, 2, 102, 'Available'),
(403, 1800.00, 1, 103, 'Available'),
(404, 1000.00, 3, 104, 'Available'),
(405, 2000.00, 1, 105, 'Under Maintenance'),
(406, 1300.00, 2, 106, 'Available'),
(407, 1100.00, 2, 107, 'Available'),
(408, 900.00, 3, 108, 'Available'),
(409, 1600.00, 1, 109, 'Reserved'),
(410, 1400.00, 2, 110, 'Available'),
(411, 1000.00, 2, 111, 'Available'),
(412, 1000.00, 2, 112, 'Available'),
(413, 1000.00, 2, 113, 'Available'),
(414, 1500.00, 1, 114, 'Available'),
(415, 1200.00, 2, 115, 'Available'),
(416, 1800.00, 1, 116, 'Available'),
(417, 1000.00, 3, 117, 'Available'),
(418, 2200.00, 1, 118, 'Reserved'),
(419, 900.00, 3, 119, 'Available'),
(420, 1400.00, 2, 120, 'Available');

INSERT INTO admission (admission_id, admit_date, discharged_date, notes, patient_id, room_id) VALUES
(501, '2026-05-10', NULL, 'Chest pain observation', 201, 401),
(502, '2026-05-10', '2026-05-12', 'Neurological monitoring, discharged stable', 202, 402),
(503, '2026-05-11', NULL, 'Leg fracture treatment', 204, 406),
(504, '2026-05-12', NULL, 'Diabetes monitoring', 206, 402),
(505, '2026-05-14', NULL, 'Cardiology observation', 209, 416),
(506, '2026-05-14', NULL, 'Bone injury follow-up', 212, 415);

-- =====================================================
-- BLOCK 13: PAYMENTS
-- Payment values are varied and realistic.
-- =====================================================

INSERT INTO payment (patient_id, payment_date, status, amount, method) VALUES
(201, '2026-05-10', 'Paid', 845.00, 'Cash'),
(202, '2026-05-10', 'Paid', 1375.00, 'Card'),
(203, '2026-05-11', 'Pending', 385.00, 'Insurance'),
(204, '2026-05-11', 'Paid', 2210.00, 'Online'),
(205, '2026-05-12', 'Unpaid', 475.00, 'Cash'),
(206, '2026-05-12', 'Paid', 965.00, 'Insurance'),
(207, '2026-05-13', 'Pending', 620.00, 'Card'),
(208, '2026-05-13', 'Paid', 1540.00, 'Online'),
(209, '2026-05-10', 'Paid', 880.00, 'Cash'),
(210, '2026-05-10', 'Pending', 530.00, 'Card'),
(211, '2026-05-11', 'Unpaid', 315.00, 'Insurance'),
(212, '2026-05-11', 'Paid', 1275.00, 'Online'),
(213, '2026-05-12', 'Pending', 455.00, 'Cash'),
(214, '2026-05-12', 'Paid', 990.00, 'Insurance'),
(215, '2026-05-13', 'Unpaid', 730.00, 'Card'),
(216, '2026-05-13', 'Paid', 1125.00, 'Online'),
(221, '2026-05-10', 'Pending', 640.00, 'Cash'),
(223, '2026-05-11', 'Paid', 770.00, 'Card'),
(225, '2026-05-12', 'Paid', 695.00, 'Insurance'),
(229, '2026-05-14', 'Unpaid', 820.00, 'Online');

-- =====================================================
-- BLOCK 14: NURSE ASSIGNMENTS AND ADMIN LOGIN
-- This block connects nurses to treated patients and creates the admin account used by the GUI.
-- =====================================================

INSERT INTO nurse_patient (nurse_id, patient_id, assigned_by, assigned_date) VALUES
(106, 201, 101, '2026-05-10'),
(107, 202, 102, '2026-05-10'),
(108, 204, 104, '2026-05-11'),
(109, 206, 105, '2026-05-12'),
(116, 209, 111, '2026-05-10'),
(117, 210, 112, '2026-05-10'),
(118, 211, 113, '2026-05-11'),
(119, 212, 114, '2026-05-11'),
(120, 214, 115, '2026-05-12');


INSERT INTO admin (username, password) VALUES
('admin', 'admin123');

-- =====================================================
-- BLOCK 15: PATIENT HISTORY
-- This block gives the project richer medical history data.
-- =====================================================

INSERT INTO patient_history (patient_id, doctor_id, record_date, diagnosis, treatment, notes) VALUES
(201, 101, '2026-05-10', 'Chest pain', 'ECG and observation', 'Patient stable'),
(202, 102, '2026-05-10', 'Headache and dizziness', 'MRI requested', 'Follow-up needed'),
(204, 104, '2026-05-11', 'Leg fracture', 'X-Ray and cast', 'Avoid walking for two weeks'),
(206, 105, '2026-05-12', 'High blood sugar', 'Insulin and monitoring', 'Daily glucose check'),
(209, 111, '2026-05-10', 'Irregular heartbeat', 'Cardiology follow-up', 'Monitor blood pressure'),
(221, 121, '2026-05-10', 'Skin allergy', 'Skin test and medication', 'Avoid allergens'),
(223, 122, '2026-05-11', 'Weak vision', 'Eye exam', 'Glasses recommended'),
(225, 123, '2026-05-12', 'Ear discomfort', 'Hearing test', 'No infection detected');

-- =====================================================
-- BLOCK 16: VIEWS
-- Views simplify reporting and make the project easier to explain.
-- =====================================================

CREATE VIEW appointment_details AS
SELECT 
    a.appointment_id,
    p.patient_id,
    p.name AS patient_name,
    s.name AS doctor_name,
    d.specialization,
    d.shift,
    a.appointment_date,
    TIME_FORMAT(a.appointment_time, '%H:%i') AS appointment_time,
    DAYNAME(a.appointment_date) AS appointment_day,
    a.status
FROM appointment a
JOIN patient p ON a.patient_id = p.patient_id
JOIN doctor d ON a.doctor_id = d.essn
JOIN staff s ON d.essn = s.ssn;

CREATE VIEW pending_payments AS
SELECT 
    p.patient_id,
    p.name AS patient_name,
    pay.amount,
    pay.payment_date,
    pay.status,
    pay.method
FROM payment pay
JOIN patient p ON pay.patient_id = p.patient_id
WHERE pay.status IN ('Pending', 'Unpaid');

CREATE VIEW admitted_patients AS
SELECT 
    p.patient_id,
    p.name AS patient_name,
    r.room_num,
    r.room_cost,
    ad.admit_date,
    ad.discharged_date,
    ad.notes
FROM admission ad
JOIN patient p ON ad.patient_id = p.patient_id
JOIN room r ON ad.room_id = r.room_id;

CREATE VIEW doctor_appointment_count AS
SELECT 
    d.essn AS doctor_id,
    s.name AS doctor_name,
    d.specialization,
    COUNT(a.appointment_id) AS total_appointments
FROM doctor d
JOIN staff s ON d.essn = s.ssn
LEFT JOIN appointment a ON d.essn = a.doctor_id
GROUP BY d.essn, s.name, d.specialization;

CREATE VIEW patient_medications AS
SELECT 
    p.patient_id,
    p.name AS patient_name,
    m.name AS medication,
    m.price,
    pr.amount,
    (m.price * pr.amount) AS total_medication_cost
FROM prescribed pr
JOIN patient p ON pr.patient_id = p.patient_id
JOIN medication m ON pr.med_id = m.med_id;

CREATE VIEW doctor_schedule_view AS
SELECT
    d.essn AS doctor_id,
    s.name AS doctor_name,
    d.specialization,
    d.shift,
    wd.day_name
FROM doctor d
JOIN staff s ON d.essn = s.ssn
JOIN doctor_working_day wd ON d.essn = wd.doctor_id;

-- =====================================================
-- BLOCK 17: INDEXES
-- Indexes improve search performance and look professional in discussion.
-- =====================================================

CREATE INDEX idx_appointment_date ON appointment(appointment_date);
CREATE INDEX idx_appointment_doctor_date ON appointment(doctor_id, appointment_date);
CREATE INDEX idx_doctor_specialization ON doctor(specialization);
CREATE INDEX idx_payment_status ON payment(status);
CREATE INDEX idx_patient_name ON patient(name);
CREATE INDEX idx_medication_name ON medication(name);
CREATE INDEX idx_room_status ON room(status);

-- =====================================================
-- BLOCK 18: VALIDATION QUERIES
-- These queries should return ZERO rows if the database is consistent.
-- Use them during preparation to prove your data is clean.
-- =====================================================

-- 18.1 Doctors with appointments on non-working days. Expected result: zero rows.
SELECT 
    a.appointment_id,
    s.name AS doctor_name,
    a.appointment_date,
    DAYNAME(a.appointment_date) AS appointment_day
FROM appointment a
JOIN doctor d ON a.doctor_id = d.essn
JOIN staff s ON d.essn = s.ssn
LEFT JOIN doctor_working_day wd
    ON wd.doctor_id = d.essn
   AND wd.day_name = DAYNAME(a.appointment_date)
WHERE wd.day_name IS NULL;

-- 18.2 Doctors with appointments on approved days off. Expected result: zero rows.
SELECT 
    a.appointment_id,
    s.name AS doctor_name,
    a.appointment_date,
    offd.reason
FROM appointment a
JOIN staff s ON a.doctor_id = s.ssn
JOIN doctor_day_off offd
    ON offd.doctor_id = a.doctor_id
   AND offd.off_date = a.appointment_date;

-- 18.3 Appointments outside doctor shift time. Expected result: zero rows.
SELECT 
    a.appointment_id,
    s.name AS doctor_name,
    d.shift,
    a.appointment_time
FROM appointment a
JOIN doctor d ON a.doctor_id = d.essn
JOIN staff s ON d.essn = s.ssn
WHERE
    (d.shift = 'morning' AND NOT (a.appointment_time BETWEEN '08:00:00' AND '12:59:59'))
 OR (d.shift = 'afternoon' AND NOT (a.appointment_time BETWEEN '13:00:00' AND '17:59:59'))
 OR (d.shift = 'night' AND NOT (a.appointment_time BETWEEN '18:00:00' AND '23:00:00'));

-- 18.4 Rooms marked Available but having active admissions. Expected result: zero rows.
SELECT 
    r.room_id,
    r.room_num,
    r.status,
    COUNT(ad.admission_id) AS active_admissions
FROM room r
JOIN admission ad ON r.room_id = ad.room_id
WHERE ad.discharged_date IS NULL
GROUP BY r.room_id, r.room_num, r.status
HAVING r.status = 'Available';

-- 18.5 Active admissions exceeding room capacity. Expected result: zero rows.
SELECT 
    r.room_id,
    r.room_num,
    r.capacity,
    COUNT(ad.admission_id) AS active_patients
FROM room r
JOIN admission ad ON r.room_id = ad.room_id
WHERE ad.discharged_date IS NULL
GROUP BY r.room_id, r.room_num, r.capacity
HAVING COUNT(ad.admission_id) > r.capacity;

-- =====================================================
-- BLOCK 19: PRACTICE QUERIES FOR PROJECT DISCUSSION
-- These are useful queries to show the professor.
-- =====================================================

-- Show unpaid or pending patients.
SELECT name, phone_num
FROM patient
WHERE patient_id IN (
    SELECT patient_id 
    FROM payment 
    WHERE status IN ('Unpaid', 'Pending')
);

-- Show the busiest doctor.
SELECT s.name AS doctor_name, d.specialization, COUNT(a.appointment_id) AS total_appointments
FROM staff s
JOIN doctor d ON s.ssn = d.essn
JOIN appointment a ON d.essn = a.doctor_id
GROUP BY s.name, d.specialization
ORDER BY total_appointments DESC
LIMIT 1;

-- Show all doctors with their specialization and shift.
SELECT d.essn AS doctor_id, s.name AS doctor_name, d.specialization, d.shift
FROM doctor d
JOIN staff s ON d.essn = s.ssn
ORDER BY d.specialization, s.name;

-- Show Paracetamol usage count.
SELECT 
    m.name AS medication_name,
    SUM(pr.amount) AS total_times_used
FROM prescribed pr
JOIN medication m ON pr.med_id = m.med_id
WHERE LOWER(m.name) = LOWER('Paracetamol')
GROUP BY m.name;

-- Show patient medication details for Sara Mohamed.
SELECT 
    p.name AS patient_name,
    m.name AS medication,
    m.description,
    m.price,
    pr.amount
FROM prescribed pr
JOIN patient p ON pr.patient_id = p.patient_id
JOIN medication m ON pr.med_id = m.med_id
WHERE p.name = 'Sara Mohamed';

-- Show appointments for Dr. Ahmed Hassan.
SELECT 
    p.name AS patient_name,
    p.blood_type,
    p.phone_num,
    a.appointment_date,
    TIME_FORMAT(a.appointment_time, '%H:%i') AS appointment_time,
    a.status
FROM appointment a
JOIN patient p ON a.patient_id = p.patient_id
JOIN staff s ON a.doctor_id = s.ssn
WHERE s.name = 'Ahmed Hassan';

-- Show available rooms.
SELECT room_num, room_cost, capacity
FROM room
WHERE status = 'Available';

-- Show complete medical history for one patient.
SELECT *
FROM patient_history
WHERE patient_id = 201;


-- =====================================================
-- BLOCK 20: EXTRA PATIENTS
-- Adds more realistic hospital traffic.
-- =====================================================

INSERT INTO patient
(patient_id, name, date_of_birth, blood_type, phone_num, gender, address)
VALUES
(231, 'Layla Mahmoud', '2000-02-14', 'A+', '01031313131', 'female', 'Nasr City, Cairo'),
(232, 'Hussein Magdy', '1996-06-22', 'O+', '01032323232', 'male', 'Maadi, Cairo'),
(233, 'Nour Ahmed', '2004-09-10', 'B+', '01033333331', 'female', 'Mokattam, Cairo'),
(234, 'Tarek Wael', '1988-12-04', 'AB-', '01034343434', 'male', 'Heliopolis, Cairo'),
(235, 'Judy Samir', '2015-05-19', 'A-', '01035353535', 'female', 'New Cairo, Cairo'),
(236, 'Youssef Medhat', '1991-01-30', 'O-', '01036363636', 'male', 'Dokki, Giza'),
(237, 'Hana Mostafa', '2003-03-12', 'B-', '01037373737', 'female', 'Zamalek, Cairo'),
(238, 'Omar Adel', '1997-08-25', 'AB+', '01038383838', 'male', '6th October, Giza'),
(239, 'Malak Hossam', '2006-11-03', 'A+', '01039393939', 'female', 'Shoubra, Cairo'),
(240, 'Seif Nader', '1994-04-18', 'O+', '01040404041', 'male', 'Madinaty, Cairo');

-- =====================================================
-- BLOCK 21: EXTRA APPOINTMENTS
-- Clean realistic appointments with no duplicate slots.
-- =====================================================

INSERT INTO appointment
(patient_id, doctor_id, appointment_date, appointment_time, status)
VALUES

(231, 101, '2026-05-17', '09:00:00', 'Scheduled'),
(232, 101, '2026-05-17', '09:30:00', 'Scheduled'),

(233, 102, '2026-05-17', '13:00:00', 'Scheduled'),
(234, 102, '2026-05-17', '13:30:00', 'Scheduled'),

(235, 103, '2026-05-18', '10:00:00', 'Scheduled'),
(236, 104, '2026-05-18', '18:30:00', 'Scheduled'),

(237, 111, '2026-05-18', '14:00:00', 'Scheduled'),
(238, 112, '2026-05-18', '11:00:00', 'Scheduled'),

(239, 121, '2026-05-19', '09:00:00', 'Scheduled'),
(240, 122, '2026-05-19', '13:30:00', 'Scheduled');

-- =====================================================
-- BLOCK 22: AUTOMATIC APPOINTMENT STATUS SYSTEM
-- Scheduled = future
-- Pending = currently happening
-- Completed = finished
-- =====================================================

SET time_zone = '+03:00';

SET SQL_SAFE_UPDATES = 0;

UPDATE appointment
SET status =
    CASE
        WHEN STR_TO_DATE(CONCAT(appointment_date, ' ', appointment_time), '%Y-%m-%d %H:%i:%s') > NOW()
            THEN 'Scheduled'

        WHEN NOW() >= STR_TO_DATE(CONCAT(appointment_date, ' ', appointment_time), '%Y-%m-%d %H:%i:%s')
         AND NOW() < DATE_ADD(
                STR_TO_DATE(CONCAT(appointment_date, ' ', appointment_time), '%Y-%m-%d %H:%i:%s'),
                INTERVAL 30 MINUTE
            )
            THEN 'Pending'

        WHEN NOW() >= DATE_ADD(
                STR_TO_DATE(CONCAT(appointment_date, ' ', appointment_time), '%Y-%m-%d %H:%i:%s'),
                INTERVAL 30 MINUTE
            )
            THEN 'Completed'
    END
WHERE status <> 'Cancelled';

DROP EVENT IF EXISTS auto_update_appointment_status;

SET GLOBAL event_scheduler = ON;

CREATE EVENT auto_update_appointment_status
ON SCHEDULE EVERY 1 MINUTE
DO
UPDATE appointment
SET status =
    CASE
        WHEN STR_TO_DATE(CONCAT(appointment_date, ' ', appointment_time), '%Y-%m-%d %H:%i:%s') > NOW()
            THEN 'Scheduled'

        WHEN NOW() >= STR_TO_DATE(CONCAT(appointment_date, ' ', appointment_time), '%Y-%m-%d %H:%i:%s')
         AND NOW() < DATE_ADD(
                STR_TO_DATE(CONCAT(appointment_date, ' ', appointment_time), '%Y-%m-%d %H:%i:%s'),
                INTERVAL 30 MINUTE
            )
            THEN 'Pending'

        WHEN NOW() >= DATE_ADD(
                STR_TO_DATE(CONCAT(appointment_date, ' ', appointment_time), '%Y-%m-%d %H:%i:%s'),
                INTERVAL 30 MINUTE
            )
            THEN 'Completed'
    END
WHERE status <> 'Cancelled';

SET SQL_SAFE_UPDATES = 1;

ALTER TABLE appointment
DROP INDEX doctor_id;

ALTER TABLE appointment
ADD COLUMN active_appointment_time TIME
GENERATED ALWAYS AS (
    CASE 
        WHEN status = 'Cancelled' THEN NULL
        ELSE appointment_time
    END
) STORED;

ALTER TABLE appointment
ADD UNIQUE KEY unique_active_doctor_slot
(doctor_id, appointment_date, active_appointment_time);

-- =====================================================
-- END OF SCRIPT
-- =====================================================