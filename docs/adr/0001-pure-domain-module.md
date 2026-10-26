# 1. parcel buissness logic rules saved in pure domain module

## Status

Accepted 

## Context

- the rules may change over time so if we write it in the http handlers any change will broke the api
- we need to make a stable contract for the other teams too

- writing the rules in the handlers is easier in the first
- if the project will not scale and it's all about a small api project so it might be an over engineering for isolating the buisness logic rules

## Decision

- we will write the buisness rules in app\domain.py and isolate it

## Consequences

- more coding
- the api should translate the response "InvalidTransition" to a status code 409 manually 

- can test the rules without the http layer (just using "apply_event" directly)
- if i need to change a rule like MAX_ATTEMPTS for example just change it in only one place
