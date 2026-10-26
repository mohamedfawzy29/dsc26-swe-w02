# AI usage

Keep all three headings exactly as they are. If this file is missing or any heading is
missing, the grader stops and gives 0 ("AI_USAGE.md missing or incomplete"). The content
is not scored, but your Track Mentor reads it and the W8 defence can ask about it.

## Tools

- claude : used it as a mentor to epxplain python , fastapi , pydantic , dataclasses , enums and reviewed my code

- What I wrote myself : app/domain.py the transition table and apply_event , the create_parcel , get_parcel and record_event endpoints , and the ADRs and AI usage

## What AI got wrong

- Its first FastAPI example was missing the app = FastAPI() line so uvicorn failed with Attribute app not found

## In my own words


1. Why does `listParcels` need a cursor rather than an offset?
- the cursor pagination uses a key in the last item showen so the pagination will continue from this key so even if there is a parcels out of the filter while the user browsing the pagination will start from the last item with the key 

2. Which of your four operations would break the courier app if you renamed one field, and who would have to approve that change?
- if we rename a field like state to status and actully this is already happend with me in this task the operation recordParcelEvent will be broke , the courier app team should approve the change first and know about it 

