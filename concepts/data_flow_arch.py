# flow :
'''
Slow path:
User Request
  ↓
API Server (10ms)
  ↓
Database query (500ms) ← Bottleneck!
  ↓
Return response
  ↓
Total: 510ms

Optimized path:
User Request
  ↓
API Server (10ms)
  ↓
Check Cache (5ms) ← Hit!
  ↓
Return response
  ↓
Total: 15ms

34x faster!
'''

# data pipeline design
'''
Step1: Collect Data 
- user create todo
- server recieves it 
- validates

Step2: Process
- Save to db
- save to cache
- log event

Step3: Distribute
- publish event
- Notify subscribers
- return response
'''

# Batch Processing : Data is accumukated over a period and processed as a graup/batch
'''
Example: Daily analytics report

7:00 PM: Collect all user actions from today
  ↓
7:05 PM: Process (calculate stats)
  ↓
7:10 PM: Generate report
  ↓
Send email to manager

Characteristics:
├─ Not real-time (24-hour delay ok)
├─ Process millions of rows at once
├─ Resource intensive (run at night)
└─ Cheap (can use slower servers)
'''
# real time Processing : Data is processed instantly when it is generated, Suitable when quick decisions or actions are needed.
'''
Example: Stock price updates

Stock price changes
  ↓
Immediately calculate portfolio value
  ↓
Push notification to user
  ↓
User sees update in 100ms

Characteristics:
├─ Real-time (100ms response)
├─ Process one item at a time
├─ Always running
└─ Expensive (dedicated servers)
'''