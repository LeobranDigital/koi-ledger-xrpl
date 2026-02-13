DELIMITER $$

CREATE PROCEDURE generate_100_koi()
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE seq INT;
    DECLARE std_id VARCHAR(60);
    DECLARE new_koi INT;

    WHILE i <= 100 DO

        -- get next sequence number
        SELECT last_seq + 1 INTO seq 
        FROM koi_id_sequence 
        WHERE farm_code='01';

        UPDATE koi_id_sequence 
        SET last_seq = seq 
        WHERE farm_code='01';

        -- build standard koi id
        SET std_id = CONCAT(
            'JPN-KOI-01-',
            DATE_FORMAT(CURDATE(), '%Y%m%d'),
            '-',
            LPAD(seq,4,'0')
        );

        -- insert koi
        INSERT INTO koi
        (
            koi_code,
            name,
            variety,
            gender,
            birth_date,
            breeder_name,
            size_cm,
            weight_kg,
            body_type,
            skin_quality,
            pattern_quality_score,
            current_owner_id,
            status,
            standard_koi_id,
            blockchain_koi_id,
            country_code,
            farm_code,
            last_measured_date,
            health_status,
            pond_location,
            purchase_price,
            current_value
        )
        VALUES
        (
            CONCAT('USER-', i),
            CONCAT('TestKoi-', i),

            ELT(1 + FLOOR(RAND()*10),
                'Kohaku','Showa','Sanke','Asagi','Shusui',
                'Ogon','Bekko','Utsuri','Chagoi','Tancho'
            ),

            IF(RAND() > 0.5, 'MALE', 'FEMALE'),

            DATE_SUB(CURDATE(), INTERVAL FLOOR(RAND()*2000) DAY),

            ELT(1 + FLOOR(RAND()*4),
                'Tanaka Farm','Yamamoto Farm',
                'Kyoto Nishiki','Niigata Breeders'
            ),

            FLOOR(15 + RAND()*70),
            ROUND(0.5 + RAND()*12,2),

            ELT(1 + FLOOR(RAND()*3),'LONG','SHORT','STANDARD'),

            ELT(1 + FLOOR(RAND()*4),'EXCELLENT','GOOD','AVERAGE','POOR'),

            FLOOR(60 + RAND()*40),

            1,

            'ACTIVE',

            std_id,

            NULL,   -- blockchain ID intentionally NULL

            'JPN',

            '01',

            CURDATE(),

            ELT(1 + FLOOR(RAND()*3),'ACTIVE','SICK','QUARANTINE'),

            CONCAT('Pond-', FLOOR(1 + RAND()*10)),

            ROUND(100 + RAND()*900,2),

            ROUND(200 + RAND()*1500,2)
        );

        SET new_koi = LAST_INSERT_ID();

        -- insert ownership history
        INSERT INTO ownership_history
        (
            koi_id,
            from_org_id,
            to_org_id,
            transfer_date,
            transfer_type,
            price
        )
        VALUES
        (
            new_koi,
            1,
            1,
            CURDATE(),
            'SALE',
            ROUND(100 + RAND()*900,2)
        );

        -- insert health record
        INSERT INTO koi_health_records
        (
            koi_id,
            record_date,
            size_cm,
            weight,
            vet_name,
            treatment,
            notes
        )
        VALUES
        (
            new_koi,
            CURDATE(),
            FLOOR(15 + RAND()*70),
            ROUND(0.5 + RAND()*12,2),
            'Dr. Suzuki',
            'Routine Check',
            'Automatically generated record'
        );

        SET i = i + 1;

    END WHILE;

END$$

DELIMITER ;
