from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, date
from enum import Enum
import shutil
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums for status management
class ToolStatus(str, Enum):
    AVAILABLE = "available"
    CHECKED_OUT = "checked_out"
    IN_MAINTENANCE = "in_maintenance"
    NEEDS_CALIBRATION = "needs_calibration"
    LOST = "lost"
    DAMAGED = "damaged"

class ProjectStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"

class CheckoutStatus(str, Enum):
    ACTIVE = "active"
    RETURNED = "returned"
    OVERDUE = "overdue"

# Data Models
class Tool(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    category: str
    serial_number: Optional[str] = None
    status: ToolStatus = ToolStatus.AVAILABLE
    image_url: Optional[str] = None
    calibration_due: Optional[date] = None
    location: Optional[str] = "Storage"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ToolCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    serial_number: Optional[str] = None
    calibration_due: Optional[date] = None
    location: Optional[str] = "Storage"

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    required_tools: List[str] = []  # List of tool IDs
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    required_tools: List[str] = []

class Worker(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    department: str
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class WorkerCreate(BaseModel):
    name: str
    email: str
    department: str
    phone: Optional[str] = None

class CheckoutRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tool_id: str
    project_id: str
    worker_id: str
    checkout_date: datetime = Field(default_factory=datetime.utcnow)
    expected_return: Optional[date] = None
    actual_return: Optional[datetime] = None
    status: CheckoutStatus = CheckoutStatus.ACTIVE
    notes: Optional[str] = None

class CheckoutCreate(BaseModel):
    tool_id: str
    project_id: str
    worker_id: str
    expected_return: Optional[date] = None
    notes: Optional[str] = None

class ReturnTool(BaseModel):
    checkout_id: str
    notes: Optional[str] = None

# Dashboard Stats Model
class DashboardStats(BaseModel):
    total_tools: int
    available_tools: int
    checked_out_tools: int
    maintenance_tools: int
    active_projects: int
    total_workers: int
    recent_checkouts: List[dict]

# Tool endpoints
@api_router.get("/tools", response_model=List[Tool])
async def get_tools():
    tools = await db.tools.find().to_list(1000)
    return [Tool(**tool) for tool in tools]

@api_router.post("/tools", response_model=Tool)
async def create_tool(tool: ToolCreate):
    tool_dict = tool.dict()
    tool_obj = Tool(**tool_dict)
    
    # Convert Tool object to dict and handle date serialization
    tool_data = tool_obj.dict()
    
    # Convert date objects to ISO format strings for MongoDB
    if tool_data.get('calibration_due'):
        tool_data['calibration_due'] = tool_data['calibration_due'].isoformat()
    if tool_data.get('created_at'):
        tool_data['created_at'] = tool_data['created_at'].isoformat()
    if tool_data.get('updated_at'):
        tool_data['updated_at'] = tool_data['updated_at'].isoformat()
    
    await db.tools.insert_one(tool_data)
    return tool_obj

@api_router.get("/tools/{tool_id}", response_model=Tool)
async def get_tool(tool_id: str):
    tool = await db.tools.find_one({"id": tool_id})
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return Tool(**tool)

@api_router.put("/tools/{tool_id}", response_model=Tool)
async def update_tool(tool_id: str, tool_update: ToolCreate):
    existing_tool = await db.tools.find_one({"id": tool_id})
    if not existing_tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    update_data = tool_update.dict()
    update_data["updated_at"] = datetime.utcnow()
    
    await db.tools.update_one({"id": tool_id}, {"$set": update_data})
    updated_tool = await db.tools.find_one({"id": tool_id})
    return Tool(**updated_tool)

@api_router.delete("/tools/{tool_id}")
async def delete_tool(tool_id: str):
    result = await db.tools.delete_one({"id": tool_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Tool not found")
    return {"message": "Tool deleted successfully"}

# Project endpoints
@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    projects = await db.projects.find().to_list(1000)
    return [Project(**project) for project in projects]

@api_router.post("/projects", response_model=Project)
async def create_project(project: ProjectCreate):
    project_dict = project.dict()
    project_obj = Project(**project_dict)
    
    # Convert Project object to dict and handle date serialization
    project_data = project_obj.dict()
    
    # Convert date objects to ISO format strings for MongoDB
    if project_data.get('start_date'):
        project_data['start_date'] = project_data['start_date'].isoformat()
    if project_data.get('end_date'):
        project_data['end_date'] = project_data['end_date'].isoformat()
    if project_data.get('created_at'):
        project_data['created_at'] = project_data['created_at'].isoformat()
    if project_data.get('updated_at'):
        project_data['updated_at'] = project_data['updated_at'].isoformat()
    
    await db.projects.insert_one(project_data)
    return project_obj

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return Project(**project)

@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, project_update: ProjectCreate):
    existing_project = await db.projects.find_one({"id": project_id})
    if not existing_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_update.dict()
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    # Convert date objects to ISO format strings for MongoDB
    if update_data.get('start_date'):
        if isinstance(update_data['start_date'], date):
            update_data['start_date'] = update_data['start_date'].isoformat()
    if update_data.get('end_date'):
        if isinstance(update_data['end_date'], date):
            update_data['end_date'] = update_data['end_date'].isoformat()
    
    await db.projects.update_one({"id": project_id}, {"$set": update_data})
    updated_project = await db.projects.find_one({"id": project_id})
    return Project(**updated_project)

# Worker endpoints
@api_router.get("/workers", response_model=List[Worker])
async def get_workers():
    workers = await db.workers.find().to_list(1000)
    return [Worker(**worker) for worker in workers]

@api_router.post("/workers", response_model=Worker)
async def create_worker(worker: WorkerCreate):
    worker_dict = worker.dict()
    worker_obj = Worker(**worker_dict)
    
    # Convert Worker object to dict and handle date serialization
    worker_data = worker_obj.dict()
    
    # Convert datetime objects to ISO format strings for MongoDB
    if worker_data.get('created_at'):
        worker_data['created_at'] = worker_data['created_at'].isoformat()
    
    await db.workers.insert_one(worker_data)
    return worker_obj

@api_router.get("/workers/{worker_id}", response_model=Worker)
async def get_worker(worker_id: str):
    worker = await db.workers.find_one({"id": worker_id})
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return Worker(**worker)

# Checkout endpoints
@api_router.post("/checkout", response_model=CheckoutRecord)
async def checkout_tool(checkout: CheckoutCreate):
    # Check if tool exists and is available
    tool = await db.tools.find_one({"id": checkout.tool_id})
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    if tool["status"] != ToolStatus.AVAILABLE:
        raise HTTPException(status_code=400, detail="Tool is not available for checkout")
    
    # Check if project exists
    project = await db.projects.find_one({"id": checkout.project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if worker exists
    worker = await db.workers.find_one({"id": checkout.worker_id})
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    # Create checkout record
    checkout_dict = checkout.dict()
    checkout_obj = CheckoutRecord(**checkout_dict)
    
    # Convert CheckoutRecord object to dict and handle date serialization
    checkout_data = checkout_obj.dict()
    
    # Convert datetime/date objects to ISO format strings for MongoDB
    if checkout_data.get('checkout_date'):
        checkout_data['checkout_date'] = checkout_data['checkout_date'].isoformat()
    if checkout_data.get('expected_return'):
        checkout_data['expected_return'] = checkout_data['expected_return'].isoformat()
    if checkout_data.get('actual_return'):
        checkout_data['actual_return'] = checkout_data['actual_return'].isoformat()
    
    await db.checkout_records.insert_one(checkout_data)
    
    # Update tool status
    await db.tools.update_one(
        {"id": checkout.tool_id},
        {"$set": {"status": ToolStatus.CHECKED_OUT, "updated_at": datetime.utcnow().isoformat()}}
    )
    
    return checkout_obj

@api_router.post("/return")
async def return_tool(return_data: ReturnTool):
    # Find the checkout record
    checkout = await db.checkout_records.find_one({"id": return_data.checkout_id})
    if not checkout:
        raise HTTPException(status_code=404, detail="Checkout record not found")
    
    if checkout["status"] != CheckoutStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Tool is already returned")
    
    # Update checkout record
    return_time = datetime.utcnow()
    await db.checkout_records.update_one(
        {"id": return_data.checkout_id},
        {"$set": {
            "actual_return": return_time.isoformat(),
            "status": CheckoutStatus.RETURNED,
            "notes": return_data.notes
        }}
    )
    
    # Update tool status back to available
    await db.tools.update_one(
        {"id": checkout["tool_id"]},
        {"$set": {"status": ToolStatus.AVAILABLE, "updated_at": return_time.isoformat()}}
    )
    
    return {"message": "Tool returned successfully"}

@api_router.get("/checkouts", response_model=List[CheckoutRecord])
async def get_checkouts(status: Optional[CheckoutStatus] = None):
    query = {}
    if status:
        query["status"] = status
    
    checkouts = await db.checkout_records.find(query).to_list(1000)
    return [CheckoutRecord(**checkout) for checkout in checkouts]

@api_router.get("/checkouts/active")
async def get_active_checkouts():
    # Get active checkouts with tool, project, and worker details
    checkouts = await db.checkout_records.find({"status": CheckoutStatus.ACTIVE}).to_list(1000)
    
    result = []
    for checkout in checkouts:
        tool = await db.tools.find_one({"id": checkout["tool_id"]})
        project = await db.projects.find_one({"id": checkout["project_id"]})
        worker = await db.workers.find_one({"id": checkout["worker_id"]})
        
        result.append({
            "checkout": CheckoutRecord(**checkout),
            "tool": Tool(**tool) if tool else None,
            "project": Project(**project) if project else None,
            "worker": Worker(**worker) if worker else None
        })
    
    return result

# Dashboard endpoint
@api_router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard():
    # Get counts
    total_tools = await db.tools.count_documents({})
    available_tools = await db.tools.count_documents({"status": ToolStatus.AVAILABLE})
    checked_out_tools = await db.tools.count_documents({"status": ToolStatus.CHECKED_OUT})
    maintenance_tools = await db.tools.count_documents({"status": ToolStatus.IN_MAINTENANCE})
    active_projects = await db.projects.count_documents({"status": ProjectStatus.ACTIVE})
    total_workers = await db.workers.count_documents({})
    
    # Get recent checkouts
    recent_checkouts = await db.checkout_records.find().sort("checkout_date", -1).limit(5).to_list(5)
    recent_checkouts_with_details = []
    
    for checkout in recent_checkouts:
        tool = await db.tools.find_one({"id": checkout["tool_id"]})
        project = await db.projects.find_one({"id": checkout["project_id"]})
        worker = await db.workers.find_one({"id": checkout["worker_id"]})
        
        recent_checkouts_with_details.append({
            "checkout": checkout,
            "tool_name": tool["name"] if tool else "Unknown Tool",
            "project_name": project["name"] if project else "Unknown Project",
            "worker_name": worker["name"] if worker else "Unknown Worker"
        })
    
    return DashboardStats(
        total_tools=total_tools,
        available_tools=available_tools,
        checked_out_tools=checked_out_tools,
        maintenance_tools=maintenance_tools,
        active_projects=active_projects,
        total_workers=total_workers,
        recent_checkouts=recent_checkouts_with_details
    )

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()