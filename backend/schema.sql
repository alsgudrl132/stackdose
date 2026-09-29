DROP TABLE IF EXISTS slots;
DROP TABLE IF EXISTS presets;
DROP TABLE IF EXISTS preset_items;
DROP TABLE IF EXISTS dispenses;

-- supplement 지금 이 칸에 넣어둔 보충제나 알약의 이름 예:크레아틴
-- kind 종류 예:가루 또는 알약
-- remaining 남은양
CREATE TABLE IF NOT EXISTS slots (
    no INTEGER PRIMARY KEY,
    supplement TEXT,
    kind TEXT,
    remaining INTEGER 
);

INSERT INTO slots VALUES (
    1, '크레아틴', 'powder', 250
);

INSERT INTO slots VALUES (
    2, 'BCAA', 'powder', 40
);

INSERT INTO slots VALUES (
    3, NULL, 'powder', 0
);

INSERT INTO slots VALUES (
    4, NULL, 'powder', 0
);

INSERT INTO slots VALUES (
    5, '오메가3', 'pill', 60
);

INSERT INTO slots VALUES (
    6, '멀티비타민', 'pill', 8
);

INSERT INTO slots VALUES (
    7, NULL, 'pill', 0
);

INSERT INTO slots VALUES (
    8, NULL, 'pill', 0
);



CREATE TABLE IF NOT EXISTS presets (
    no INTEGER PRIMARY KEY,
    name TEXT
);

-- amount 목적 g 또는 몇알
CREATE TABLE IF NOT EXISTS preset_items (
    preset INTEGER,
    slot INTEGER,
    amount INTEGER,
    FOREIGN KEY(preset) REFERENCES presets(no)
        ON DELETE CASCADE
        ON UPDATE CASCADE
    FOREIGN KEY(slot) REFERENCES slots(no)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

INSERT INTO presets VALUES (
    1, '아침'
);

INSERT INTO preset_items VALUES (
    1,1,5
);

INSERT INTO preset_items VALUES (
    1,5,2
);

CREATE TABLE IF NOT EXISTS dispenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    preset INTEGER,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(preset) REFERENCES presets(no)
)