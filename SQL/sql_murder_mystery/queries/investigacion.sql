-- ============================================
-- SQL MURDER MYSTERY - Investigation Log
-- Autor: Juan Jose Carrascal Pinzón
-- Fecha del crimen: 15 de enero de 2018, SQL City
-- ============================================

-- PASO 1: Obtener el reporte del crimen
-- Buscamos el reporte de tipo "murder" ocurrido el 15/01/2018 en SQL City
SELECT
    date
    ,type
    ,description
    ,city
FROM crime_scene_report
WHERE date = 20180115
    AND type LIKE 'murder'
    AND city LIKE 'SQL City';

-- Resultado: el reporte menciona 2 testigos:
-- 1) El primero vive en la última casa de "Northwestern Dr"
-- 2) Annabel, que vive en "Franklin Ave"


-- PASO 2: Identificar al primer testigo (última casa de Northwestern Dr)
SELECT *
FROM person
WHERE address_street_name = 'Northwestern Dr'
ORDER BY address_number DESC
LIMIT 1;

-- Resultado: Morty Schapiro (person_id 14887)


-- PASO 3: Identificar a la segunda testigo (Annabel en Franklin Ave)
SELECT *
FROM person
WHERE address_street_name = 'Franklin Ave'
    AND name LIKE '%Annabel%';

-- Resultado: Annabel Miller (person_id 16371)


-- PASO 4: Consultar los testimonios de ambos testigos
SELECT *
FROM interview
WHERE person_id IN (14887, 16371);

-- Resultado clave:
-- - El asesino es hombre, miembro "gold" de Get Fit Now Gym
-- - Su membresía empieza con "48Z"
-- - Su placa de carro incluye "H42W"
-- - Estuvo en el gimnasio el 9 de enero de 2018


-- PASO 5: Buscar sospechosos por membresía de gimnasio (gold, prefijo 48Z)
SELECT *
FROM get_fit_now_member
WHERE id LIKE '48Z%'
    AND membership_status = 'gold';

-- Resultado: 2 sospechosos -> Joe Germuska (28819) y Jeremy Bowers (67318)


-- PASO 6: Cruzar sospechosos con la placa del carro (contiene "H42W", género masculino)
SELECT
    p.name
    ,p.license_id
    ,l.plate_number
    ,l.gender
FROM person p
JOIN drivers_license l ON p.license_id = l.id
WHERE l.gender = 'male'
    AND l.plate_number LIKE '%H42W%';

-- Resultado: Tushar Chandra y Jeremy Bowers
-- Jeremy Bowers se repite en ambas búsquedas (gimnasio + placa)


-- PASO 7: Verificar el check-in del gimnasio el 9 de enero (antes/durante el de Annabel)
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

-- Resultado: Joe Germuska y Jeremy Bowers coinciden en el check-in
-- Jeremy Bowers aparece en las 3 pistas (membresía, placa, check-in) -> sospechoso confirmado


-- PASO 8: Confesión de Jeremy Bowers
SELECT *
FROM interview
WHERE person_id = 67318;

-- Resultado: Jeremy confiesa que fue contratado por una mujer:
-- rica, entre 65" y 67" de altura, pelo rojo, maneja un Tesla Model S,
-- asistió al "SQL Symphony Concert" 3 veces en diciembre de 2017


-- PASO 9: Identificar a la contratante del asesinato
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
-- RESULTADO FINAL: Miranda Priestly (person_id 99716)
-- contrató a Jeremy Bowers para cometer el asesinato.
-- ============================================