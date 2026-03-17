"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from datetime import datetime, timezone

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


# In-memory gate and vehicle database
gates = {
    "Main Entrance": {
        "description": "Primary vehicle gate at the school main entrance",
        "status": "closed",
        "vehicles_inside": []
    },
    "Staff Parking": {
        "description": "Gate for staff parking area",
        "status": "closed",
        "vehicles_inside": []
    },
    "Service Gate": {
        "description": "Gate for service and delivery vehicles",
        "status": "closed",
        "vehicles_inside": []
    }
}

vehicles = {
    "ABC-1234": {
        "owner": "John Smith",
        "type": "car",
        "authorized": True
    },
    "XYZ-5678": {
        "owner": "Jane Doe",
        "type": "motorcycle",
        "authorized": True
    },
    "SRV-9900": {
        "owner": "City Supplies Co.",
        "type": "truck",
        "authorized": True
    }
}

vehicle_log = []


@app.get("/gates")
def get_gates():
    """Get all gates and their current status"""
    return gates


@app.get("/vehicles")
def get_vehicles():
    """Get all registered vehicles"""
    return vehicles


@app.post("/vehicles")
def register_vehicle(license_plate: str, owner: str, vehicle_type: str):
    """Register a new vehicle"""
    if license_plate in vehicles:
        raise HTTPException(status_code=400, detail="Vehicle already registered")
    vehicles[license_plate] = {
        "owner": owner,
        "type": vehicle_type,
        "authorized": True
    }
    return {"message": f"Vehicle {license_plate} registered successfully"}


@app.post("/gates/{gate_name}/entry")
def vehicle_entry(gate_name: str, license_plate: str):
    """Record a vehicle entering through a gate"""
    if gate_name not in gates:
        raise HTTPException(status_code=404, detail="Gate not found")
    if license_plate not in vehicles:
        raise HTTPException(status_code=404, detail="Vehicle not registered")
    if not vehicles[license_plate]["authorized"]:
        raise HTTPException(status_code=403, detail="Vehicle not authorized")

    gate = gates[gate_name]
    if license_plate in gate["vehicles_inside"]:
        raise HTTPException(status_code=400, detail="Vehicle is already inside")

    gate["vehicles_inside"].append(license_plate)
    gate["status"] = "open"
    event = {
        "gate": gate_name,
        "license_plate": license_plate,
        "action": "entry",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    vehicle_log.append(event)
    return {"message": f"Vehicle {license_plate} entered through {gate_name}", "event": event}


@app.post("/gates/{gate_name}/exit")
def vehicle_exit(gate_name: str, license_plate: str):
    """Record a vehicle exiting through a gate"""
    if gate_name not in gates:
        raise HTTPException(status_code=404, detail="Gate not found")
    if license_plate not in vehicles:
        raise HTTPException(status_code=404, detail="Vehicle not registered")

    gate = gates[gate_name]
    if license_plate not in gate["vehicles_inside"]:
        raise HTTPException(status_code=400, detail="Vehicle is not inside")

    gate["vehicles_inside"].remove(license_plate)
    if not gate["vehicles_inside"]:
        gate["status"] = "closed"
    event = {
        "gate": gate_name,
        "license_plate": license_plate,
        "action": "exit",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    vehicle_log.append(event)
    return {"message": f"Vehicle {license_plate} exited through {gate_name}", "event": event}


@app.get("/gates/{gate_name}/log")
def get_gate_log(gate_name: str):
    """Get the entry/exit log for a specific gate"""
    if gate_name not in gates:
        raise HTTPException(status_code=404, detail="Gate not found")
    gate_events = [e for e in vehicle_log if e["gate"] == gate_name]
    return {"gate": gate_name, "log": gate_events}
