"""
API router for LinkedIn Analyzer Agent
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import logging

from ..core.scraping import scraping_engine
from ..models.profile import ProfileData, ProfileAnalysis
from ..services.analyzer import ProfileAnalyzer
from ..services.export import ExportService

logger = logging.getLogger(__name__)

# Create main API router
api_router = APIRouter()

# Initialize services
profile_analyzer = ProfileAnalyzer()
export_service = ExportService()


@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "LinkedIn Analyzer Agent",
        "version": "1.0.0"
    }


@api_router.post("/profiles/scrape")
async def scrape_profile(
    profile_url: str,
    background_tasks: BackgroundTasks
):
    """Scrape a LinkedIn profile"""
    try:
        logger.info(f"Received scraping request for: {profile_url}")
        
        # Validate URL
        if not profile_url.startswith("https://www.linkedin.com/in/"):
            raise HTTPException(
                status_code=400,
                detail="Invalid LinkedIn profile URL. Must start with 'https://www.linkedin.com/in/'"
            )
        
        # Start scraping process
        profile_data = await scraping_engine.scrape_linkedin_profile(profile_url)
        
        if not profile_data:
            raise HTTPException(
                status_code=404,
                detail="Could not scrape profile. Profile may be private or URL invalid."
            )
        
        # Add background analysis task
        background_tasks.add_task(analyze_profile_background, profile_data)
        
        return {
            "status": "success",
            "message": "Profile scraped successfully",
            "data": profile_data.to_dict(),
            "analysis_status": "queued"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping profile {profile_url}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@api_router.get("/profiles/analyze/{profile_id}")
async def analyze_profile(profile_id: str):
    """Analyze a scraped profile"""
    try:
        # This would typically fetch from database
        # For now, return mock analysis
        
        analysis = ProfileAnalysis(
            profile_id=profile_id,
            career_level="Senior",
            industry_focus=["Technology", "Software Development"],
            profile_completeness_score=85,
            skill_relevance_score=78,
            experience_value_score=92,
            market_competitiveness_score=88
        )
        
        return {
            "status": "success",
            "data": analysis.__dict__
        }
        
    except Exception as e:
        logger.error(f"Error analyzing profile {profile_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@api_router.post("/profiles/batch-scrape")
async def batch_scrape_profiles(
    profile_urls: List[str],
    background_tasks: BackgroundTasks
):
    """Scrape multiple LinkedIn profiles"""
    try:
        if len(profile_urls) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 profiles allowed per batch request"
            )
        
        results = []
        
        for url in profile_urls:
            try:
                if not url.startswith("https://www.linkedin.com/in/"):
                    results.append({
                        "url": url,
                        "status": "error",
                        "error": "Invalid LinkedIn URL"
                    })
                    continue
                
                profile_data = await scraping_engine.scrape_linkedin_profile(url)
                
                if profile_data:
                    results.append({
                        "url": url,
                        "status": "success",
                        "data": profile_data.to_dict()
                    })
                    
                    # Queue for analysis
                    background_tasks.add_task(analyze_profile_background, profile_data)
                else:
                    results.append({
                        "url": url,
                        "status": "error",
                        "error": "Could not scrape profile"
                    })
                    
            except Exception as e:
                results.append({
                    "url": url,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "status": "completed",
            "total_profiles": len(profile_urls),
            "successful": len([r for r in results if r["status"] == "success"]),
            "failed": len([r for r in results if r["status"] == "error"]),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch scraping: {e}")
        raise HTTPException(status_code=500, detail=f"Batch scraping error: {str(e)}")


@api_router.get("/market/skills-analysis")
async def analyze_market_skills():
    """Analyze current market skill trends"""
    try:
        # Mock data for demonstration
        skills_analysis = {
            "trending_skills": [
                {"skill": "Artificial Intelligence", "growth": "+35%", "demand": "Very High"},
                {"skill": "Cloud Computing", "growth": "+28%", "demand": "High"},
                {"skill": "Data Science", "growth": "+22%", "demand": "High"},
                {"skill": "Cybersecurity", "growth": "+31%", "demand": "Very High"},
                {"skill": "DevOps", "growth": "+25%", "demand": "High"}
            ],
            "skill_categories": {
                "technical": ["Python", "JavaScript", "AWS", "Docker", "Kubernetes"],
                "soft_skills": ["Leadership", "Communication", "Problem Solving"],
                "emerging": ["Machine Learning", "Blockchain", "IoT"]
            },
            "salary_impact": {
                "high_value_skills": ["Machine Learning", "Cloud Architecture", "Data Engineering"],
                "average_salary_increase": "15-30%"
            }
        }
        
        return {
            "status": "success",
            "data": skills_analysis
        }
        
    except Exception as e:
        logger.error(f"Error analyzing market skills: {e}")
        raise HTTPException(status_code=500, detail=f"Market analysis error: {str(e)}")


@api_router.get("/export/profile/{profile_id}")
async def export_profile(
    profile_id: str,
    format: str = "json"
):
    """Export profile data in various formats"""
    try:
        if format not in ["json", "csv", "pdf"]:
            raise HTTPException(
                status_code=400,
                detail="Unsupported format. Use 'json', 'csv', or 'pdf'"
            )
        
        # This would fetch actual profile data from database
        # For now, return mock export
        
        if format == "json":
            return JSONResponse(content={
                "profile_id": profile_id,
                "exported_at": "2025-07-25T10:00:00Z",
                "format": format,
                "download_url": f"/downloads/{profile_id}.json"
            })
        
        return {
            "status": "success",
            "profile_id": profile_id,
            "format": format,
            "download_url": f"/downloads/{profile_id}.{format}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting profile {profile_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")


@api_router.get("/stats/dashboard")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        stats = {
            "total_profiles_scraped": 1247,
            "profiles_today": 23,
            "average_analysis_time": "2.3 seconds",
            "success_rate": "94.2%",
            "top_industries": [
                {"name": "Technology", "count": 423},
                {"name": "Finance", "count": 298},
                {"name": "Healthcare", "count": 187},
                {"name": "Education", "count": 156},
                {"name": "Marketing", "count": 183}
            ],
            "popular_skills": [
                {"skill": "Python", "frequency": 67},
                {"skill": "JavaScript", "frequency": 54},
                {"skill": "Project Management", "frequency": 48},
                {"skill": "Data Analysis", "frequency": 43},
                {"skill": "Leadership", "frequency": 39}
            ]
        }
        
        return {
            "status": "success",
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")


async def analyze_profile_background(profile_data: ProfileData):
    """Background task for profile analysis"""
    try:
        logger.info(f"Starting background analysis for profile: {profile_data.name}")
        
        # Perform AI analysis
        analysis = await profile_analyzer.analyze_profile(profile_data)
        
        # Save analysis results (would save to database)
        logger.info(f"Analysis completed for profile: {profile_data.name}")
        
    except Exception as e:
        logger.error(f"Error in background analysis: {e}")
