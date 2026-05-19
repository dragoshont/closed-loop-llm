# Demo Script

## Startup
- Start LM Studio
- Load Phi-4-mini
- Reset feedback.json
- Run debug mode

## Step 1
User:
Suggest something fun for this weekend.

Expected:
Outdoor activities suggested.

Narration:
“The system currently has no memory.”

## Step 2
Feedback:
I dislike outdoor activities.

Expected logs:
[MEMORY UPDATED]
dislikes = ["outdoor activities"]

## Step 3
Repeat prompt.

Expected:
Indoor recommendations.

Narration:
“The system behavior evolved without retraining.”