# Task queue = Queue specifically for background jobs.
# components

'''
1. Producer (your app):
   ├─ Creates task
   ├─ Puts in queue
   └─ Returns immediately

2. Queue (Redis, RabbitMQ):
   ├─ Stores tasks
   ├─ Durable (doesn't lose if crash)
   └─ Can replay

3. Worker (background process):
   ├─ Listens to queue
   ├─ Picks up task
   ├─ Executes
   └─ Reports success/failure

4. Result backend (optional):
   ├─ Stores task results
   ├─ Check status later
   └─ Return to user
'''

'''
Use for:
├─ Sending emails (slow I/O)
├─ Processing images (CPU intensive)
├─ Generating reports (long running)
├─ Sending notifications
├─ Cleaning up old data
├─ Database backups
└─ Any "fire and forget" task

Example tasks:
├─ Send welcome email: 5-10 seconds
├─ Generate PDF report: 30 seconds
├─ Process video upload: 5 minutes
├─ Delete unused accounts: 1 hour (nightly)
'''