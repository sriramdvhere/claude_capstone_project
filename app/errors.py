"""
Global error handler for RequestValidationError (IMP-005).

DR-001: All Pydantic / FastAPI validation errors return HTTP 400, never 422.
DR-002: A completely missing request body returns HTTP 400 with the message
        "Request body is required".
DR-003: Custom field-level messages from the Validation Layer are propagated
        verbatim into the "details" array.
"""
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Map of field names whose "missing" Pydantic error should use a
# requirements-defined message string (requirements Section 8).
_MISSING_FIELD_MESSAGES: dict[str, str] = {
    "amount": "amount is required",
    "category": "category is required",
    "date": "date is required",
}


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Convert every RequestValidationError into an HTTP 400 response with shape:
        {"error": "Validation failed", "details": ["<message>", ...]}

    Missing-body detection (DR-002):
        When the error location is exactly ("body",) and type is "missing",
        the entire request body is absent.
    """
    errors = exc.errors()

    # DR-002: Detect a fully absent request body before processing field errors.
    for error in errors:
        loc = error.get("loc", ())
        if error.get("type") == "missing" and loc == ("body",):
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Validation failed",
                    "details": ["Request body is required"],
                },
            )

    details: list[str] = []

    for error in errors:
        loc = error.get("loc", ())
        etype = error.get("type", "")
        msg: str = error.get("msg", "validation error")

        if etype == "missing":
            # loc is typically ("body", "field_name"); take the last segment.
            field_name = str(loc[-1]) if loc else "field"
            custom_msg = _MISSING_FIELD_MESSAGES.get(
                field_name, f"{field_name} is required"
            )
            details.append(custom_msg)
        else:
            # For PydanticCustomError the msg is already the clean requirement
            # string.  For any native Pydantic v2 error that slips through,
            # strip the "Value error, " prefix if present.
            if msg.startswith("Value error, "):
                msg = msg[len("Value error, "):]
            details.append(msg)

    return JSONResponse(
        status_code=400,
        content={"error": "Validation failed", "details": details},
    )
