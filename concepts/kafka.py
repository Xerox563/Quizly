# The Moment You Finish Watching
# 8:30 PM: You finish "Wednesday" episode 4.
'''
Without Kafka (Batch - Bad):
System waits 5 minutes for 1000 other users to finish
  ↓
Processes all together
  ↓
Updates recommendations
  ↓
You open app at 8:35 PM → Finally see new suggestions
'''

# How Kafka Works 
'''
1. Producer [netflix app]
- You finished the episode -> app sends event ot the kafka
Event: { user: "you", show: "wednesday_s01e04", watched: true }

2. Topic (Event Stream)
- Kafka stores event in persistent log
  user-watch-events:
    ├─ Event 1: User A watched Breaking Bad
    ├─ Event 2: User B watched Stranger Things
    ├─ Event 3: You watched Wednesday  ← HERE
    └─ Event 4: User C watched The Office

3. Consumers (Services Listening)
- Multiple services read same event independently:
    Kafka Topic
        ↓
    ├─ Recommendation Engine → "You like dark dramas" → Updates cache
    ├─ Analytics Service → "Wednesday views +1" → Updates trending
    ├─ Billing Service → "45 min watched" → Logs usage
    └─ Search Service → "Boost Wednesday popularity"
'''

# How Kafka Stores and Processes Events Internally
'''
You press "Stop" on episode 4
       ↓
Event created:
{
  userId: "netflix_user_001",
  showId: "wednesday_s01e04",
  watchedSeconds: 2700,
  timestamp: "2024-06-09T20:30:00Z"
}
       ↓
Sent to Kafka Topic: "user-watch-events"
'''

# Event Storage (Inside Kafka)
'''
- Kafka doesn't store in db , It uses disk log(fast write, permanent)
  Topic: user-watch-events
Partition 0 (for your user_id hash):

Disk Log File:
┌────────────────────────────────────────┐
│ Offset 5420: Your event                │
│ {userId: "001", showId: "wednesday"... │
│                                         │
│ Offset 5421: Another user's event      │
│ {userId: "002", showId: "breaking"...  │
│                                         │
│ Offset 5422: Another user's event      │
│ {userId: "003", showId: "stranger"...  │
└────────────────────────────────────────┘

Your event = Offset 5420 (permanent, retrievable forever can reply to any event anytime)
'''
# Event Distribution to Consumers
'''
Kafka doesn't push events. Consumers pull them.

Recommendation Consumer (Group: "recommendation-group"):
├─ Current position: Offset 5419
├─ Pulls next event: Offset 5420 (YOUR event)
├─ Reads: { userId: "001", showId: "wednesday_s01e04", ... }
└─ Remembers: "I'm now at Offset 5420"

Analytics Consumer (Group: "analytics-group"):
├─ Current position: Offset 5418
├─ Pulls next events: Offsets 5419, 5420 (YOUR event)
├─ Reads both
└─ Remembers: "I'm now at Offset 5420"

Billing Consumer (Group: "billing-group"):
├─ Current position: Offset 5415
├─ Pulls next events: Offsets 5416-5420 (YOUR event + others)
├─ Reads all
└─ Remembers: "I'm now at Offset 5420"
'''

'''
Kafka doesn't send events to services. Instead, services come and grab events themselves (pull, not push).
Think of it like a library:

Kafka is the bookshelf (has all events/books)
Each service is a student with a bookmark
Each student comes to the shelf, reads from their bookmark, updates their bookmark
'''

# Parallel Processing (What Each Consumer Does) : (All Happening Parallel)
# Recommendation Engine
'''
Reads your event from Offset 5420:
{
  userId: "001",
  showId: "wednesday_s01e04",
  watchedSeconds: 2700
}

Logic:
├─ Extract genre: "wednesday" → "Dark Fantasy"
├─ Update user profile: user_001 likes "Dark Fantasy"
├─ Query: "Find shows similar to Wednesday"
├─ Results: [Stranger Things, The Haunting, Dark]
└─ Store in Redis cache:
   Key: "recommendations:user_001"
   Value: [Stranger Things, The Haunting, Dark]

Time: 50ms
Status: Complete
'''

# Analytics Engine
'''
Reads your event from Offset 5420:
{
  showId: "wednesday_s01e04",
  watchedSeconds: 2700
}

Logic:
├─ Increment: wednesday_views += 1
├─ Calculate: wednesday_totalViewTime += 2700 seconds
├─ Rank shows by views (Redis sorted set):
│  1. Stranger Things: 15M views
│  2. Wednesday: 14.2M views ← YOUR view added
│  3. Breaking Bad: 13.8M views
└─ Store trending list in cache

Time: 80ms
Status: Complete
'''
# Billing Engine
'''
The Billing Engine reads your event and does this:

Converts seconds to hours: 2700 seconds = 0.75 hours
Records in database: Inserts row in PostgreSQL (permanent storage)
Updates monthly bill: Tracks total hours you watched this month
'''
# 
'''
Scenario: At 8:30:00.050, recommendation server dies 💥

8:30:00.000 → Event at Offset 5420 stored in Kafka
8:30:00.050 → Recommendation consumer crashes
             (didn't update Redis yet)

8:30:05 → Server restarts

Restart process:
├─ Check: "Where was I? Last offset processed = 5419"
├─ Kafka: "Give me offset 5420 and beyond"
├─ Replay: Re-reads your event
├─ Execute: Updates recommendations (delayed, but works)
└─ Resume: Continues from new events

Result: Event not lost, recommendations eventually updated
'''

'''
Scenario: Recommendation server crashes while processing your event.
What Kafka does:

Event is safe: Still stored at Offset 5420 (never deleted)
Service remembers position: "I was at Offset 5419"
Service restarts: Checks "What was I doing?"
Service asks for missing events: "Give me from 5420 onwards"
Service replays: Re-reads your event and processes it again
Service resumes: Continues from new events

Why this matters?

No data loss: Event is always safe in Kafka
Automatic recovery: Service can fix itself
Eventually consistent: Event gets processed, just delayed
'''