"""
Profile data models for LinkedIn Analyzer Agent
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class ProfileStatus(Enum):
    """Profile processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ExperienceItem:
    """Individual work experience item"""
    title: str = ""
    company: str = ""
    duration: str = ""
    location: str = ""
    description: str = ""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_current: bool = False


@dataclass
class EducationItem:
    """Individual education item"""
    institution: str = ""
    degree: str = ""
    field_of_study: str = ""
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    grade: str = ""
    activities: str = ""


@dataclass
class SkillItem:
    """Individual skill item with endorsements"""
    name: str = ""
    endorsements: int = 0
    category: str = ""


@dataclass
class CertificationItem:
    """Individual certification item"""
    name: str = ""
    issuing_organization: str = ""
    issue_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    credential_id: str = ""
    credential_url: str = ""


@dataclass
class ProjectItem:
    """Individual project item"""
    name: str = ""
    description: str = ""
    url: str = ""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    associated_with: str = ""  # Company or organization


@dataclass
class LanguageItem:
    """Individual language item"""
    name: str = ""
    proficiency: str = ""  # Native, Professional, Limited, etc.


@dataclass
class ProfileData:
    """Complete LinkedIn profile data structure"""
    
    # Basic Information
    name: str = ""
    headline: str = ""
    location: str = ""
    industry: str = ""
    summary: str = ""
    profile_url: str = ""
    profile_image_url: str = ""
    background_image_url: str = ""
    
    # Contact Information
    email: str = ""
    phone: str = ""
    website: str = ""
    
    # Professional Information
    current_position: str = ""
    current_company: str = ""
    connection_count: str = ""
    follower_count: str = ""
    
    # Experience and Education
    experience: List[ExperienceItem] = field(default_factory=list)
    education: List[EducationItem] = field(default_factory=list)
    
    # Skills and Endorsements
    skills: List[SkillItem] = field(default_factory=list)
    top_skills: List[str] = field(default_factory=list)
    
    # Additional Sections
    certifications: List[CertificationItem] = field(default_factory=list)
    projects: List[ProjectItem] = field(default_factory=list)
    languages: List[LanguageItem] = field(default_factory=list)
    volunteer_experience: List[Dict[str, Any]] = field(default_factory=list)
    publications: List[Dict[str, Any]] = field(default_factory=list)
    patents: List[Dict[str, Any]] = field(default_factory=list)
    honors_awards: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    scraped_at: datetime = field(default_factory=datetime.now)
    status: ProfileStatus = ProfileStatus.PENDING
    processing_time: Optional[float] = None
    error_message: Optional[str] = None
    
    # Raw data
    raw_html: str = ""
    raw_json: Dict[str, Any] = field(default_factory=dict)
    
    # Analysis results
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    ai_insights: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile data to dictionary"""
        return {
            'name': self.name,
            'headline': self.headline,
            'location': self.location,
            'industry': self.industry,
            'summary': self.summary,
            'profile_url': self.profile_url,
            'current_position': self.current_position,
            'current_company': self.current_company,
            'connection_count': self.connection_count,
            'experience': [exp.__dict__ for exp in self.experience],
            'education': [edu.__dict__ for edu in self.education],
            'skills': [skill.__dict__ if isinstance(skill, SkillItem) else skill for skill in self.skills],
            'certifications': [cert.__dict__ for cert in self.certifications],
            'projects': [proj.__dict__ for proj in self.projects],
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
            'status': self.status.value if isinstance(self.status, ProfileStatus) else self.status,
            'analysis_results': self.analysis_results,
            'ai_insights': self.ai_insights
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProfileData':
        """Create ProfileData from dictionary"""
        profile = cls()
        
        # Basic fields
        for field_name in ['name', 'headline', 'location', 'industry', 'summary', 
                          'profile_url', 'current_position', 'current_company', 'connection_count']:
            if field_name in data:
                setattr(profile, field_name, data[field_name])
        
        # Experience
        if 'experience' in data:
            profile.experience = [
                ExperienceItem(**exp) if isinstance(exp, dict) else exp 
                for exp in data['experience']
            ]
        
        # Education
        if 'education' in data:
            profile.education = [
                EducationItem(**edu) if isinstance(edu, dict) else edu 
                for edu in data['education']
            ]
        
        # Skills
        if 'skills' in data:
            profile.skills = [
                SkillItem(**skill) if isinstance(skill, dict) and 'name' in skill else SkillItem(name=str(skill))
                for skill in data['skills']
            ]
        
        # Status
        if 'status' in data:
            profile.status = ProfileStatus(data['status']) if isinstance(data['status'], str) else data['status']
        
        # Scraped at
        if 'scraped_at' in data:
            if isinstance(data['scraped_at'], str):
                profile.scraped_at = datetime.fromisoformat(data['scraped_at'])
            else:
                profile.scraped_at = data['scraped_at']
        
        # Analysis results
        profile.analysis_results = data.get('analysis_results', {})
        profile.ai_insights = data.get('ai_insights', {})
        
        return profile
    
    def get_years_of_experience(self) -> int:
        """Calculate total years of professional experience"""
        total_years = 0
        
        for exp in self.experience:
            if exp.start_date and exp.end_date:
                years = (exp.end_date - exp.start_date).days / 365.25
                total_years += years
            elif exp.start_date and exp.is_current:
                years = (datetime.now() - exp.start_date).days / 365.25
                total_years += years
        
        return int(total_years)
    
    def get_skill_names(self) -> List[str]:
        """Get list of skill names"""
        return [
            skill.name if isinstance(skill, SkillItem) else str(skill) 
            for skill in self.skills
        ]
    
    def get_companies_worked(self) -> List[str]:
        """Get list of companies worked at"""
        return [exp.company for exp in self.experience if exp.company]
    
    def get_education_institutions(self) -> List[str]:
        """Get list of educational institutions"""
        return [edu.institution for edu in self.education if edu.institution]
    
    def has_minimum_data(self) -> bool:
        """Check if profile has minimum required data for analysis"""
        return bool(self.name and (self.headline or self.experience or self.skills))


@dataclass
class ProfileAnalysis:
    """Analysis results for a LinkedIn profile"""
    
    profile_id: str = ""
    
    # Career Analysis
    career_level: str = ""  # Entry, Mid, Senior, Executive
    industry_focus: List[str] = field(default_factory=list)
    skill_categories: Dict[str, List[str]] = field(default_factory=dict)
    
    # Market Analysis
    salary_estimate: Dict[str, Any] = field(default_factory=dict)
    market_demand: str = ""  # High, Medium, Low
    skill_gaps: List[str] = field(default_factory=list)
    trending_skills: List[str] = field(default_factory=list)
    
    # Recommendations
    career_recommendations: List[str] = field(default_factory=list)
    skill_recommendations: List[str] = field(default_factory=list)
    learning_path: List[Dict[str, Any]] = field(default_factory=list)
    
    # Scores (0-100)
    profile_completeness_score: int = 0
    skill_relevance_score: int = 0
    experience_value_score: int = 0
    market_competitiveness_score: int = 0
    
    # Analysis metadata
    analyzed_at: datetime = field(default_factory=datetime.now)
    analysis_version: str = "1.0"
    confidence_score: float = 0.0
