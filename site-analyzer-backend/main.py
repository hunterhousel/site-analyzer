from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from typing import Optional
import numpy as np
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import base64

app = FastAPI()

# Allow frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AddressRequest(BaseModel):
    address: str

class SiteReport(BaseModel):
    address: str
    latitude: float
    longitude: float
    elevation_min: float
    elevation_max: float
    elevation_avg: float
    slope_analysis: dict
    access_score: str
    report_pdf: Optional[str] = None  # Base64 encoded PDF

# You'll need to get a free API key from Google Cloud Platform
# For now, we'll use a placeholder
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

@app.get("/")
async def root():
    return {"message": "Site Analyzer API - Send POST to /analyze with address"}

@app.post("/analyze")
async def analyze_site(request: AddressRequest) -> SiteReport:
    """
    Main endpoint: Takes an address and returns site analysis
    """
    try:
        print(f"Analyzing address: {request.address}")
        
        # Step 1: Geocode the address
        print("Step 1: Geocoding...")
        lat, lng = await geocode_address(request.address)
        print(f"Coordinates: {lat}, {lng}")
        
        # Step 2: Get elevation data
        print("Step 2: Getting elevation...")
        elevation_data = await get_elevation_data(lat, lng)
        print(f"Elevation data: {elevation_data}")
        
        # Step 3: Analyze terrain
        print("Step 3: Analyzing slopes...")
        slope_analysis = analyze_slopes(elevation_data)
        
        # Step 4: Assess access
        print("Step 4: Assessing access...")
        access_score = assess_access(lat, lng)
        
        # Step 5: Generate PDF report
        print("Step 5: Generating PDF...")
        pdf_base64 = generate_pdf_report(
            request.address, 
            lat, 
            lng, 
            elevation_data,
            slope_analysis,
            access_score
        )
        print("PDF generated successfully")
        
        return SiteReport(
            address=request.address,
            latitude=lat,
            longitude=lng,
            elevation_min=elevation_data['min'],
            elevation_max=elevation_data['max'],
            elevation_avg=elevation_data['avg'],
            slope_analysis=slope_analysis,
            access_score=access_score,
            report_pdf=pdf_base64
        )
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
async def geocode_address(address: str) -> tuple[float, float]:
    """Convert address to latitude/longitude using Google Geocoding API"""
    
    # For MVP, we'll use a free alternative: Nominatim (OpenStreetMap)
    async with httpx.AsyncClient() as client:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address + ", Salt Lake City, Utah",
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "SiteAnalyzer/1.0"
        }
        
        response = await client.get(url, params=params, headers=headers)
        data = response.json()
        
        if not data:
            raise ValueError(f"Could not geocode address: {address}")
        
        lat = float(data[0]["lat"])
        lng = float(data[0]["lon"])
        
        return lat, lng

async def get_elevation_data(lat: float, lng: float) -> dict:
    """
    Get elevation data from USGS or Open-Elevation API
    For MVP, we'll sample a grid around the point
    """
    
    # Sample points in a grid around the location (roughly 200m x 200m)
    grid_size = 5
    offset = 0.001  # roughly 100m at this latitude
    
    elevations = []
    
    async with httpx.AsyncClient() as client:
        for i in range(grid_size):
            for j in range(grid_size):
                sample_lat = lat + (i - grid_size//2) * offset
                sample_lng = lng + (j - grid_size//2) * offset
                
                # Using Open-Elevation API (free, no key needed)
                url = "https://api.open-elevation.com/api/v1/lookup"
                params = {
                    "locations": f"{sample_lat},{sample_lng}"
                }
                
                try:
                    response = await client.get(url, params=params, timeout=10.0)
                    data = response.json()
                    if data.get("results"):
                        elevations.append(data["results"][0]["elevation"])
                except:
                    continue
    
    if not elevations:
        # Fallback: single point elevation
        async with httpx.AsyncClient() as client:
            url = "https://api.open-elevation.com/api/v1/lookup"
            params = {"locations": f"{lat},{lng}"}
            response = await client.get(url, params=params, timeout=10.0)
            data = response.json()
            elevation = data["results"][0]["elevation"]
            elevations = [elevation]
    
    return {
        "min": min(elevations),
        "max": max(elevations),
        "avg": sum(elevations) / len(elevations),
        "samples": elevations
    }

def analyze_slopes(elevation_data: dict) -> dict:
    """Analyze slope characteristics"""
    
    elevation_range = elevation_data['max'] - elevation_data['min']
    
    # Simple slope classification
    if elevation_range < 3:
        slope_class = "Flat (< 5%)"
        buildability = "Excellent - minimal grading required"
    elif elevation_range < 8:
        slope_class = "Gentle (5-15%)"
        buildability = "Good - standard grading techniques"
    elif elevation_range < 15:
        slope_class = "Moderate (15-25%)"
        buildability = "Fair - may require retaining walls"
    else:
        slope_class = "Steep (> 25%)"
        buildability = "Challenging - significant earthwork required"
    
    return {
        "elevation_change_meters": round(elevation_range, 2),
        "slope_classification": slope_class,
        "buildability_assessment": buildability
    }

def assess_access(lat: float, lng: float) -> str:
    """Simple access assessment based on location"""
    
    # For MVP, we'll do a basic assessment
    # In full version, this would query road networks
    
    return "Good - within Salt Lake City metro area with road access"

def generate_pdf_report(address: str, lat: float, lng: float, 
                       elevation_data: dict, slope_analysis: dict, 
                       access_score: str) -> str:
    """Generate a PDF report and return as base64 string"""
    
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(1*inch, height - 1*inch, "Site Analysis Report")
    
    # Address
    c.setFont("Helvetica", 12)
    c.drawString(1*inch, height - 1.5*inch, f"Location: {address}")
    c.drawString(1*inch, height - 1.8*inch, f"Coordinates: {lat:.6f}, {lng:.6f}")
    
    # Elevation Analysis
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 2.5*inch, "Elevation Analysis")
    
    c.setFont("Helvetica", 11)
    y = height - 2.8*inch
    c.drawString(1.2*inch, y, f"Minimum Elevation: {elevation_data['min']:.1f} meters")
    y -= 0.25*inch
    c.drawString(1.2*inch, y, f"Maximum Elevation: {elevation_data['max']:.1f} meters")
    y -= 0.25*inch
    c.drawString(1.2*inch, y, f"Average Elevation: {elevation_data['avg']:.1f} meters")
    y -= 0.25*inch
    c.drawString(1.2*inch, y, f"Elevation Change: {slope_analysis['elevation_change_meters']:.1f} meters")
    
    # Slope Analysis
    y -= 0.5*inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, y, "Slope Analysis")
    
    y -= 0.3*inch
    c.setFont("Helvetica", 11)
    c.drawString(1.2*inch, y, f"Classification: {slope_analysis['slope_classification']}")
    y -= 0.25*inch
    c.drawString(1.2*inch, y, f"Buildability: {slope_analysis['buildability_assessment']}")
    
    # Access Assessment
    y -= 0.5*inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, y, "Access Assessment")
    
    y -= 0.3*inch
    c.setFont("Helvetica", 11)
    c.drawString(1.2*inch, y, access_score)
    
    # Footer
    c.setFont("Helvetica", 9)
    c.drawString(1*inch, 0.5*inch, "Generated by Site Analyzer - For preliminary planning purposes only")
    c.drawString(1*inch, 0.35*inch, "This report should be verified with professional site surveys")
    
    c.save()
    
    # Convert to base64
    pdf_bytes = buffer.getvalue()
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
    
    return pdf_base64

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
