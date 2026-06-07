# IDEMPOTENCY KEYS
# What is Idempotency?

'''
# Idempotency means that if the same request is sent multiple times,
# the result should be the same as sending it only once.

# Simple idea:
# Same request sent many times
# → Action happens only once
# → No duplicate records

# Why Do We Need It?

# Example:
# User clicks "Create Todo"

# Request is sent
# ↓
# Network becomes slow
# ↓
# User thinks it failed
# ↓
# User clicks again

# Now the server receives the same request twice.

# Without Idempotency:

# Request 1 → Create Todo
# Request 2 → Create Todo

# Result:
# Two identical todos are created.
# Duplicate data appears.

# This is a problem.

# What is an Idempotency Key?

# An idempotency key is a unique identifier attached to a request.

# Think of it like a tracking number.

# Example:
# Request → Key = abc123

# The server remembers this key after processing the request.

# How Does It Work?

# First Request

# Request arrives with key = abc123

# Server checks:
# "Have I seen abc123 before?"

# Answer:
# No

# So the server:
# - Processes the request
# - Creates the todo
# - Stores the response
# - Saves key abc123

# Second Request (Retry)

# Due to network issues or user double-clicking,
# the same request arrives again.

# Key = abc123

# Server checks:
# "Have I seen abc123 before?"

# Answer:
# Yes

# Instead of processing again:
# - Server returns the previous response
# - No new todo is created

# Result:
# Only one todo exists.

# Why Is Idempotency Important?

# It prevents:
# - Duplicate todos
# - Duplicate payments
# - Duplicate money transfers
# - Duplicate bookings
# - Duplicate emails

# It protects against:
# - User double-clicks
# - Network retries
# - Timeouts
# - Application failures

# Without Idempotency:

# Same request
# → Processed multiple times
# → Duplicate actions occur

# With Idempotency:

# Same request
# → Recognized using the idempotency key
# → Processed only once

# Real-World Examples

# Payment Processing:
# User pays ₹100
# Request retried
# Without idempotency → Charged twice
# With idempotency → Charged once

# Money Transfer:
# Transfer ₹1000
# Request retried
# Without idempotency → ₹2000 transferred
# With idempotency → ₹1000 transferred once

# Appointment Booking:
# User books a slot
# Request retried
# Without idempotency → Two bookings created
# With idempotency → One booking created

# Email Sending:
# Request retried
# Without idempotency → Multiple emails sent
# With idempotency → Single email sent

# Interview Definition

# Idempotency is a mechanism that ensures
# the same request can be safely retried multiple times
# without creating duplicate actions.
# This is achieved using a unique idempotency key
# that helps the server identify previously processed requests.
'''