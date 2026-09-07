"""
Domain constants shared across the system.

The workflow status set grew over the course:
  * Workshop 1 (MVP)            -> NEW, IN_REVIEW
  * Workshop 1 / part 2         -> WAITING_FOR_VALIDATION
  * Workshop 3 (Crisis Load)    -> BUILDING_IN_RESTORATION, RESTORATION_COMPLETED

A new report is created in WAITING_FOR_VALIDATION and, once validated,
moves along:  WAITING_FOR_VALIDATION -> NEW -> IN_REVIEW ->
              BUILDING_IN_RESTORATION -> RESTORATION_COMPLETED
"""

WAITING_FOR_VALIDATION = "WAITING_FOR_VALIDATION"
NEW = "NEW"
IN_REVIEW = "IN_REVIEW"
BUILDING_IN_RESTORATION = "BUILDING_IN_RESTORATION"
RESTORATION_COMPLETED = "RESTORATION_COMPLETED"

# Ordered so the UI can render a sensible default flow.
VALID_STATUSES = [
    WAITING_FOR_VALIDATION,
    NEW,
    IN_REVIEW,
    BUILDING_IN_RESTORATION,
    RESTORATION_COMPLETED,
]

STATUS_LABELS_HE = {
    WAITING_FOR_VALIDATION: "ממתין לאימות",
    NEW: "חדש",
    IN_REVIEW: "בבדיקה",
    BUILDING_IN_RESTORATION: "מבנה בתהליך שיקום",
    RESTORATION_COMPLETED: "תהליך שיקום הסתיים",
}

# Buildings with MORE than this many apartments require a social approval
# before a budget request may be opened (Workshop 2 / Sprint 4).
SOCIAL_APPROVAL_THRESHOLD = 24
