-- SQL MURDER MYSTERY - Investigation Log
-- Author: Juan Jose Carrascal Pinzon
-- Crime date: January 15, 2018, SQL City
-- ============================================

-- STEP 1: Retrieve the crime scene report
-- Looking for a "murder" report that occurred on 01/15/2018 in SQL City
SELECT
    date
    ,type
    ,description
    ,city
FROM crime_scene_report
WHERE date = 20180115
    AND type LIKE 'murder'
    AND city LIKE 'SQL City';

-- Result: the report mentions 2 witnesses:
-- 1) The first one lives at the last house on "Northwestern Dr"
-- 2) Annabel, who lives somewhere on "Franklin Ave"


-- STEP 2: Identify the first witness (last house on Northwestern Dr)
SELECT *
FROM person
WHERE address_street_name = 'Northwestern Dr'
ORDER BY address_number DESC
LIMIT 1;

-- Result: Morty Schapiro (person_id 14887)


-- STEP 3: Identify the second witness (Annabel on Franklin Ave)
SELECT *
FROM person
WHERE address_street_name = 'Franklin Ave'
    AND name LIKE '%Annabel%';

-- Result: Annabel Miller (person_id 16371)


-- STEP 4: Check both witnesses' interviews
SELECT *
FROM interview
WHERE person_id IN (14887, 16371);

-- Key findings:
-- - The killer is male, a gold member of Get Fit Now Gym
-- - His membership number starts with "48Z"
-- - His license plate includes "H42W"
-- - He was at the gym on January 9, 2018


-- STEP 5: Search for gym members matching the clues (gold, prefix 48Z)
SELECT *
FROM get_fit_now_member
WHERE id LIKE '48Z%'
    AND membership_status = 'gold';

-- Result: 2 suspects -> Joe Germuska (28819) and Jeremy Bowers (67318)


-- STEP 6: Cross reference suspects with the license plate (contains "H42W", male)
SELECT
    p.name
    ,p.license_id
    ,l.plate_number
    ,l.gender
FROM person p
JOIN drivers_license l ON p.license_id = l.id
WHERE l.gender = 'male'
    AND l.plate_number LIKE '%H42W%';

-- Result: Tushar Chandra and Jeremy Bowers
-- Jeremy Bowers appears in both searches (gym + license plate)


-- STEP 7: Verify the gym check in on January 9 (before/during Annabel's check in)
SELECT
    m.person_id
    ,m.name
    ,m.id
    ,c.check_in_date
    ,c.check_in_time
    ,c.check_out_time
FROM person p
JOIN get_fit_now_member m ON p.id = m.person_id
JOIN get_fit_now_check_in c ON m.id = c.membership_id
WHERE c.check_in_date = '20180109'
    AND (c.check_in_time <= (
        SELECT ci.check_in_time
        FROM person pin
        JOIN get_fit_now_member mi ON pin.id = mi.person_id
        JOIN get_fit_now_check_in ci ON mi.id = ci.membership_id
        WHERE mi.person_id = 16371
    ))
    AND (c.check_out_time >= (
        SELECT co.check_in_time
        FROM person po
        JOIN get_fit_now_member mo ON po.id = mo.person_id
        JOIN get_fit_now_check_in co ON mo.id = co.membership_id
        WHERE mo.person_id = 16371
    ));

-- Result: Joe Germuska and Jeremy Bowers match the check in window
-- Jeremy Bowers appears in all 3 clues (membership, plate, check in) -> confirmed suspect


-- STEP 8: Jeremy Bowers' confession
SELECT *
FROM interview
WHERE person_id = 67318;

-- Result: Jeremy confesses he was hired by a woman:
-- rich, between 65" and 67" tall, red hair, drives a Tesla Model S,
-- attended the "SQL Symphony Concert" 3 times in December 2017


-- STEP 9: Identify the person who hired the killer
SELECT
    p.id
    ,p.name
    ,l.gender
    ,l.height
    ,l.hair_color
    ,l.car_make
    ,l.car_model
    ,f.event_name
FROM person p
JOIN drivers_license l ON p.license_id = l.id
JOIN income i ON p.ssn = i.ssn
JOIN facebook_event_checkin f ON p.id = f.person_id
WHERE l.gender = 'female'
    AND (l.height BETWEEN 65 AND 67)
    AND l.hair_color = 'red'
    AND car_make = 'Tesla'
    AND car_model = 'Model S'
    AND f.event_name = 'SQL Symphony Concert'
    AND (f.date BETWEEN 20171201 AND 20171231)
GROUP BY
    p.id
    ,p.name
    ,l.gender
    ,l.height
    ,l.hair_color
    ,l.car_make
    ,l.car_model
    ,f.event_name
HAVING count(*) = 3;

-- ============================================
-- FINAL RESULT: Miranda Priestly (person_id 99716)
-- hired Jeremy Bowers to commit the murder.
-- ============================================