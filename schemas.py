"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

# Example schemas (you can keep these if needed by other tools):

class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Plot visit website schemas

class Plot(BaseModel):
    """
    Collection: "plot"
    Represents a land plot that users can visit.
    """
    title: str = Field(..., description="Plot title")
    location: str = Field(..., description="Location/address of the plot")
    size_sqft: int = Field(..., gt=0, description="Size in square feet")
    price_per_sqft: float = Field(..., gt=0, description="Price per square foot")
    image_url: Optional[str] = Field(None, description="Thumbnail image URL")
    description: Optional[str] = Field(None, description="Short description")

class VisitRequest(BaseModel):
    """
    Collection: "visitrequest"
    A user's request to schedule a plot visit.
    """
    plot_id: str = Field(..., description="ID of the plot to visit")
    name: str = Field(..., min_length=2, description="Visitor full name")
    email: Optional[EmailStr] = Field(None, description="Visitor email")
    phone: str = Field(..., min_length=7, description="Contact phone number")
    preferred_date: str = Field(..., description="Preferred visit date (YYYY-MM-DD)")
    preferred_time: str = Field(..., description="Preferred time (e.g., 10:30 AM)")
    guests: int = Field(1, ge=1, le=10, description="Number of attendees")
    notes: Optional[str] = Field(None, description="Additional notes")
    status: str = Field("pending", description="Status of the request")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# Note: The Flames database viewer can use these schemas for validation and CRUD.
