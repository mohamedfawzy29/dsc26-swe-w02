# 2. Use offset pagination for listParcels endpoint

## Status

Rejected

## Context

- need to split the parcels list into pages and the status of every parcel may change while the customer browsing the pages 

- the customer get the parcels page by page and he usually using filters when browsing like State=Created

## Decision

We will not use offset pagination and will implement cursor pagination

## Consequences

- We have prevented the occurrence of duplicate parcels and the skipping of any parcel
- now we can't jump from page to a far another page directly 