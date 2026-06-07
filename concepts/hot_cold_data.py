# Hot Data vs Cold Data
'''
# Hot data = Accessed frequently
Last 7 days of todos
├─ Users view often
├─ Must be fast (1ms)
└─ Keep in fast SSD database


# Cold data = Accessed rarely
Todos from 1 year ago
├─ Users view rarely
├─ Can be slow (1 second ok)
└─ Keep in cheap disk storage

WHY SEPARATE?
Problem:
├─ 1 billion todos in database
├─ 99% are old (not accessed)
├─ But slow down queries for recent todos
└─ Database is HUGE (expensive storage)

Solution:
├─ Recent todos (hot): Fast SSD, indexed
├─ Old todos (cold): Cheap archival storage
└─ Queries on hot data are fast again
'''

# SQL CODE
'''
Hot table (last 7 days):
CREATE TABLE todos_hot (
    id INT,
    user_id INT,
    title VARCHAR,
    created_at TIMESTAMP
);
CREATE INDEX idx_user_id ON todos_hot(user_id);

Cold table/archive (older data):
CREATE TABLE todos_cold (
    id INT,
    user_id INT,
    title VARCHAR,
    created_at TIMESTAMP
);
-- No indexes (rarely queried)

When archiving (daily job):
DELETE FROM todos_hot WHERE created_at < 7 days ago;
INSERT INTO todos_cold SELECT * FROM todos_hot WHERE created_at < 7 days ago;
'''

# How did we decide to index user_id?
'''
Look at the queries the application runs most often.

Suppose your API is:
SELECT * FROM todos_hot
WHERE user_id = 5;

or

SELECT * FROM todos_hot
WHERE user_id = 10;

or

SELECT * FROM todos_hot
WHERE user_id = 25;

Notice something?
- user_id is used in WHERE clause repeatedly
- Since the database searches by user_id all the time, we create:
- CREATE INDEX idx_user_id ON todos_hot(user_id);

Now the database can find a user's todos quickly.
--------------------------------------------
Rule #1
If a column is frequently used in WHERE, consider indexing it.

Example:
SELECT * FROM users
WHERE email = 'abc@gmail.com';

Index:
CREATE INDEX idx_email ON users(email);
Because searches happen by email.
---------------------------------------------
Rule #2
If a column is frequently used in JOIN, index it.

Example:
SELECT *
FROM users u
JOIN todos t
ON u.id = t.user_id;

Index:
CREATE INDEX idx_user_id ON todos(user_id);
Because database matches rows using user_id.
---------------------------------------------
Rule #3
If a column is frequently used in ORDER BY, index it.

Example:
SELECT *
FROM todos
ORDER BY created_at DESC;

Index:
CREATE INDEX idx_created_at ON todos(created_at);
Because sorting happens on created_at.
'''