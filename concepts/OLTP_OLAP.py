# OLTP = Online Transaction Processing
# It is the database that your application directly uses every day.
# Think like
'''
User opens app
↓
User creates todo
↓
User updates todo
↓
User deletes todo
'''
'''
Purpose: Handle fast transactions
├─ Create todo (1 second)
├─ Update todo (1 second)
├─ Delete todo (1 second)
└─ Many users doing this simultaneously

Characteristics:
├─ Many small writes
├─ Few reads
├─ Real-time
├─ Normalized database (avoid duplicates)
└─ Fast inserts/updates

Tools: PostgreSQL, MySQL, MongoDB
'''
# OLAP = Online Analytical Processing
# OLAP is used for analyzing data, not running the application.
'''
Think:
- Manager wants reports
- Business wants insights
- Analyst wants trends

Instead of serving users, OLAP helps answer business questions.
'''
'''
Purpose: Analyze historical data
├─ "How many todos per user?"
├─ "What's most common category?"
├─ "Trend over 6 months?"
└─ Can take minutes to hours

Characteristics:
├─ Few writes (batched nightly)
├─ Many reads (queries scan millions of rows)
├─ Historical data
├─ Denormalized database (lots of duplicates for speed)
└─ Slow inserts, fast queries

Tools: Data Warehouse (Snowflake, BigQuery), OLAP cubes
'''


# Separation
'''
Problem:
├─ Run analytics query on OLTP database
├─ Scans 1 billion rows
├─ Locks database
└─ Users can't create todos for 5 minutes!

Solution:
├─ Keep OLTP database fast (small, indexed)
├─ Copy data nightly to OLAP warehouse
├─ Run analytics on warehouse (can afford to be slow)
└─ Users unaffected
'''