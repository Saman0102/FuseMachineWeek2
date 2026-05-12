"""
main.py - FastAPI application entry point

Sets up the API, imports all routers, and starts the server.
This is where everything comes together.
"""

from fastapi import FastAPI

from app.router_counts import router as counts_router
from app.routers.customer_routers import router as customer_router
from app.routers.product_routers import router as product_router
from app.routers.productline_routers import router as productline_router
from app.routers.office_routers import router as office_router
from app.routers.employee_routers import router as employee_router
from app.routers.order_routers import router as order_router
from app.routers.orderdetail_routers import router as orderdetail_router
from app.routers.payment_routers import router as payment_router
from app.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="ClassicModels API",
    version="2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add all the routers
app.include_router(counts_router)
app.include_router(product_router, prefix="/products", tags=["Products"])
app.include_router(productline_router, prefix="/productlines", tags=["ProductLines"])
app.include_router(office_router, prefix="/offices", tags=["Offices"])
app.include_router(employee_router, prefix="/employees", tags=["Employees"])
app.include_router(order_router, prefix="/orders", tags=["Orders"])
app.include_router(orderdetail_router, prefix="/orderdetails", tags=["OrderDetails"])
app.include_router(payment_router, prefix="/payments", tags=["Payments"])
app.include_router(customer_router)

logger.info("API started")


@app.get("/", tags=["Health"])
def root():
    """Health check - just verify the API is running."""
    logger.info("Health check")
    return {"message": "ClassicModels API is running!"}