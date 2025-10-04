# Event Tracking Plan v1

## Overview
This document defines the structure and properties of all client-side tracked events.

---

## Event: page_view
- Description: User visits a page.
- Properties:
  - url (string): visited page URL
  - referrer (string): referring page URL
  - timestamp (ISO8601 string): event UTC timestamp
  - user_id (string|nullable): anonymized user identifier
  - session_id (string): current user session ID

---

## Event: button_click
- Description: User clicks a button.
- Properties:
  - button_id (string): HTML id or semantic name of the button
  - page_url (string): page where button was clicked
  - timestamp (ISO8601 string)
  - user_id (string|nullable)
  - session_id (string)

---

## Event: form_submit
- Description: User submits a form.
- Properties:
  - form_id (string): id/name of the form
  - page_url (string)
  - fields_filled (object): key-value pairs of filled form fields, respecting privacy/sensitivity
  - timestamp (ISO8601 string)
  - user_id (string|nullable)
  - session_id (string)

---

## Versioning
Please update this document and increment version for any schema changes.
