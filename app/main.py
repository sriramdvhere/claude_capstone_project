"""
FastAPI application entry point (IMP-008 + IMP-009).

Wires together:
  - Lifespan: initialises the SQLite database on startup (IMP-002).
  - MaxBodySizeMiddleware: enforces the 10 KB body size limit (DR-008 / NFR-004).
  - RequestLoggerMiddleware: structured per-request logging (IMP-009 / NFR-008).
  - Global error handler: overrides RequestValidationError → HTTP 400 (IMP-005).
  - POST /expenses route: delegates to the Expense Service (IMP-008).

Middleware execution order (last added = outermost / first to see the request):
    RequestLoggerMiddleware  [outermost]
    MaxBodySizeMiddleware
    FastAPI route handling + exception handler  [innermost]
"""
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.database import init_db
from app.errors import validation_exception_handler
from app.models import ExpenseCreate, ExpenseResponse
from app import service
from app.repository import DBError, DBUnavailableError

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Initialise the database schema on startup."""
    init_db()
    yield


# ---------------------------------------------------------------------------
# Middleware: 10 KB body size limit (DR-008 / ACH-008)
# ---------------------------------------------------------------------------

_MAX_BODY_BYTES = 10 * 1024  # 10 KB


class MaxBodySizeMiddleware(BaseHTTPMiddleware):
    """
    Returns HTTP 413 when the Content-Length header exceeds 10 KB.
    Using the Content-Length header is the specified approach (impl-plan OQ-2).
    """

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                if int(content_length) > _MAX_BODY_BYTES:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": "Request too large",
                            "details": ["Request body must not exceed 10 KB"],
                        },
                    )
            except ValueError:
                pass  # Malformed Content-Length — let the request proceed
        return await call_next(request)


# ---------------------------------------------------------------------------
# Middleware: Request logger (IMP-009 / NFR-008)
# ---------------------------------------------------------------------------


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Logs every request/response with:
      ISO 8601 timestamp | method | path | status code | latency (ms)

    Log levels:
      INFO  — 2xx / 3xx responses
      WARN  — 4xx responses (validation failures)
      ERROR — 5xx responses or unhandled exceptions (with stack trace)
    """

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        try:
            response = await call_next(request)
            latency_ms = (time.perf_counter() - start) * 1000
            status = response.status_code
            msg = (
                f"{datetime.now(timezone.utc).isoformat()} "
                f"{request.method} {request.url.path} "
                f"{status} {latency_ms:.1f}ms"
            )
            if status >= 500:
                logger.error(msg)
            elif status >= 400:
                logger.warning(msg)
            else:
                logger.info(msg)
            return response
        except Exception:
            latency_ms = (time.perf_counter() - start) * 1000
            msg = (
                f"{datetime.now(timezone.utc).isoformat()} "
                f"{request.method} {request.url.path} "
                f"500 {latency_ms:.1f}ms"
            )
            logger.error(msg, exc_info=True)
            raise


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(lifespan=lifespan)

# Middlewares — MaxBodySizeMiddleware added first so it is inner;
# RequestLoggerMiddleware added second so it is outermost.
app.add_middleware(MaxBodySizeMiddleware)
app.add_middleware(RequestLoggerMiddleware)

# DR-001 / DR-002: Override the default 422 handler with our 400 handler.
app.add_exception_handler(RequestValidationError, validation_exception_handler)


# ---------------------------------------------------------------------------
# POST /expenses (IMP-008)
# ---------------------------------------------------------------------------


@app.post("/expenses", status_code=201)
async def create_expense_endpoint(expense_data: ExpenseCreate):
    """
    Create a new expense record.

    Returns HTTP 201 with the full expense object on success.
    Returns HTTP 503 on transient database failure.
    Returns HTTP 500 on general database failure.
    All validation errors return HTTP 400 (handled by the global error handler).
    """
    try:
        record = service.create_expense(expense_data)
        response = ExpenseResponse(
            id=record.id,
            amount=record.amount,
            category=record.category,
            date=record.date,
            description=record.description,
        )
        # FastAPI's jsonable_encoder converts Decimal → float and UUID → str.
        return response
    except DBUnavailableError:
        return JSONResponse(
            status_code=503,
            content={
                "error": "Service Unavailable",
                "details": ["Data store is temporarily unavailable"],
            },
        )
    except DBError:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "details": ["An internal error occurred"],
            },
        )
