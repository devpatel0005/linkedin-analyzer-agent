"""
Profile Analysis Service for LinkedIn Analyzer Agent
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..models.profile import ProfileData, ProfileAnalysis, SkillItem

logger = logging.getLogger(__name__)


class ProfileAnalyzer:
    """Advanced profile analysis service"""
    
    def __init__(self):
        self.skill_categories = {
            'technical': [
                'Python', 'JavaScript', 'Java', 'C++', 'React', 'Node.js',
                'AWS', 'Docker', 'Kubernetes', 'Git', 'SQL', 'MongoDB',
                'Machine Learning', 'Data Science', 'AI', 'DevOps'
            ],
            'soft_skills': [
                'Leadership', 'Communication', 'Project Management',
                'Team Management', 'Problem Solving', 'Strategic Planning',
                'Negotiation', 'Presentation', 'Critical Thinking'
            ],
            'domain_specific': [
                'Digital Marketing', 'SEO', 'Content Marketing',
                'Financial Analysis', 'Business Analysis', 'Sales',
                'Customer Service', 'Product Management', 'UX Design'
            ]
        }
        
        self.trending_skills_2025 = [
            'Artificial Intelligence', 'Machine Learning', 'Cloud Computing',
            'Cybersecurity', 'Data Engineering', 'DevOps', 'Blockchain',
            'IoT', 'Edge Computing', 'Quantum Computing', 'AR/VR'
        ]
    
    async def analyze_profile(self, profile_data: ProfileData) -> ProfileAnalysis:
        """Perform comprehensive profile analysis"""
        logger.info(f"Starting analysis for profile: {profile_data.name}")
        
        analysis = ProfileAnalysis(profile_id=profile_data.profile_url)
        
        # Perform various analyses
        analysis.career_level = self._determine_career_level(profile_data)
        analysis.industry_focus = self._analyze_industry_focus(profile_data)
        analysis.skill_categories = self._categorize_skills(profile_data)
        
        # Calculate scores
        analysis.profile_completeness_score = self._calculate_completeness_score(profile_data)
        analysis.skill_relevance_score = self._calculate_skill_relevance(profile_data)
        analysis.experience_value_score = self._calculate_experience_value(profile_data)
        analysis.market_competitiveness_score = self._calculate_market_competitiveness(profile_data)
        
        # Generate recommendations
        analysis.skill_recommendations = self._generate_skill_recommendations(profile_data)
        analysis.career_recommendations = self._generate_career_recommendations(profile_data)
        analysis.skill_gaps = self._identify_skill_gaps(profile_data)
        
        # Market analysis
        analysis.market_demand = self._assess_market_demand(profile_data)
        analysis.salary_estimate = self._estimate_salary_range(profile_data)
        
        analysis.confidence_score = self._calculate_confidence_score(analysis)
        
        logger.info(f"Analysis completed for profile: {profile_data.name}")
        return analysis
    
    def _determine_career_level(self, profile: ProfileData) -> str:
        """Determine career level based on experience"""
        years_experience = profile.get_years_of_experience()
        
        # Check for leadership indicators in titles
        leadership_keywords = ['director', 'manager', 'lead', 'head', 'chief', 'vp', 'cto', 'ceo']
        has_leadership = any(
            keyword in exp.title.lower() 
            for exp in profile.experience 
            for keyword in leadership_keywords
        )
        
        if years_experience >= 15 or has_leadership:
            return "Executive"
        elif years_experience >= 8:
            return "Senior"
        elif years_experience >= 3:
            return "Mid-Level"
        else:
            return "Entry-Level"
    
    def _analyze_industry_focus(self, profile: ProfileData) -> List[str]:
        """Analyze industry focus from experience and skills"""
        industries = []
        
        # Common industry keywords
        industry_keywords = {
            'Technology': ['software', 'tech', 'development', 'programming', 'IT', 'digital'],
            'Finance': ['finance', 'banking', 'investment', 'trading', 'fintech'],
            'Healthcare': ['healthcare', 'medical', 'hospital', 'pharma', 'biotech'],
            'Education': ['education', 'university', 'school', 'teaching', 'training'],
            'Marketing': ['marketing', 'advertising', 'brand', 'social media', 'SEO'],
            'Consulting': ['consulting', 'advisory', 'strategy', 'management consulting'],
            'Retail': ['retail', 'e-commerce', 'sales', 'merchandising'],
            'Manufacturing': ['manufacturing', 'production', 'operations', 'supply chain']
        }
        
        # Analyze experience titles and company names
        experience_text = ' '.join([
            f"{exp.title} {exp.company}".lower() 
            for exp in profile.experience
        ])
        
        # Analyze skills
        skills_text = ' '.join(profile.get_skill_names()).lower()
        
        # Combine for analysis
        combined_text = f"{experience_text} {skills_text} {profile.headline.lower()}"
        
        for industry, keywords in industry_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                industries.append(industry)
        
        return industries[:3]  # Return top 3 industries
    
    def _categorize_skills(self, profile: ProfileData) -> Dict[str, List[str]]:
        """Categorize skills into technical, soft skills, etc."""
        skill_names = [
            skill.name.lower() if isinstance(skill, SkillItem) else str(skill).lower()
            for skill in profile.skills
        ]
        
        categorized = {
            'technical': [],
            'soft_skills': [],
            'domain_specific': [],
            'trending': [],
            'other': []
        }
        
        for skill in skill_names:
            categorized_skill = False
            
            # Check each category
            for category, category_skills in self.skill_categories.items():
                if any(cat_skill.lower() in skill for cat_skill in category_skills):
                    categorized[category].append(skill)
                    categorized_skill = True
                    break
            
            # Check trending skills
            if any(trending.lower() in skill for trending in self.trending_skills_2025):
                categorized['trending'].append(skill)
                categorized_skill = True
            
            # If not categorized, add to other
            if not categorized_skill:
                categorized['other'].append(skill)
        
        return categorized
    
    def _calculate_completeness_score(self, profile: ProfileData) -> int:
        """Calculate profile completeness score (0-100)"""
        score = 0
        
        # Basic information (30 points)
        if profile.name: score += 5
        if profile.headline: score += 5
        if profile.summary: score += 10
        if profile.location: score += 5
        if profile.profile_image_url: score += 5
        
        # Experience (25 points)
        if profile.experience:
            score += min(25, len(profile.experience) * 5)
        
        # Skills (20 points)
        if profile.skills:
            score += min(20, len(profile.skills) * 2)
        
        # Education (15 points)
        if profile.education:
            score += min(15, len(profile.education) * 7)
        
        # Additional sections (10 points)
        if profile.certifications: score += 3
        if profile.projects: score += 3
        if profile.languages: score += 2
        if profile.volunteer_experience: score += 2
        
        return min(100, score)
    
    def _calculate_skill_relevance(self, profile: ProfileData) -> int:
        """Calculate how relevant skills are to current market (0-100)"""
        if not profile.skills:
            return 0
        
        skill_names = profile.get_skill_names()
        trending_count = sum(
            1 for skill in skill_names
            for trending in self.trending_skills_2025
            if trending.lower() in skill.lower()
        )
        
        technical_count = sum(
            1 for skill in skill_names
            for tech_skill in self.skill_categories['technical']
            if tech_skill.lower() in skill.lower()
        )
        
        total_skills = len(skill_names)
        relevance_ratio = (trending_count * 2 + technical_count) / total_skills
        
        return min(100, int(relevance_ratio * 50))
    
    def _calculate_experience_value(self, profile: ProfileData) -> int:
        """Calculate experience value score (0-100)"""
        if not profile.experience:
            return 0
        
        score = 0
        years = profile.get_years_of_experience()
        
        # Years of experience (40 points)
        score += min(40, years * 3)
        
        # Quality of companies (30 points)
        companies = profile.get_companies_worked()
        well_known_companies = [
            'google', 'microsoft', 'apple', 'amazon', 'facebook', 'meta',
            'netflix', 'tesla', 'ibm', 'oracle', 'salesforce', 'adobe'
        ]
        
        quality_score = sum(
            10 for company in companies
            if any(known in company.lower() for known in well_known_companies)
        )
        score += min(30, quality_score)
        
        # Career progression (30 points)
        titles = [exp.title.lower() for exp in profile.experience]
        progression_keywords = ['senior', 'lead', 'manager', 'director', 'head', 'chief']
        progression_score = sum(5 for title in titles if any(kw in title for kw in progression_keywords))
        score += min(30, progression_score)
        
        return min(100, score)
    
    def _calculate_market_competitiveness(self, profile: ProfileData) -> int:
        """Calculate market competitiveness score (0-100)"""
        # Combine other scores with weights
        completeness = self._calculate_completeness_score(profile)
        skill_relevance = self._calculate_skill_relevance(profile)
        experience_value = self._calculate_experience_value(profile)
        
        # Weighted average
        competitiveness = (
            completeness * 0.3 +
            skill_relevance * 0.4 +
            experience_value * 0.3
        )
        
        return int(competitiveness)
    
    def _generate_skill_recommendations(self, profile: ProfileData) -> List[str]:
        """Generate skill recommendations based on profile analysis"""
        recommendations = []
        
        current_skills = [skill.lower() for skill in profile.get_skill_names()]
        
        # Recommend trending skills not present
        for trending_skill in self.trending_skills_2025:
            if not any(trending_skill.lower() in skill for skill in current_skills):
                recommendations.append(f"Learn {trending_skill} - High market demand")
        
        # Industry-specific recommendations
        industries = self._analyze_industry_focus(profile)
        if 'Technology' in industries:
            tech_recommendations = [
                'Cloud Computing (AWS/Azure)',
                'DevOps and CI/CD',
                'Data Science and Analytics',
                'Cybersecurity Fundamentals'
            ]
            recommendations.extend(tech_recommendations[:2])
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _generate_career_recommendations(self, profile: ProfileData) -> List[str]:
        """Generate career path recommendations"""
        recommendations = []
        
        career_level = self._determine_career_level(profile)
        years_exp = profile.get_years_of_experience()
        
        if career_level == "Entry-Level":
            recommendations.extend([
                "Focus on building core technical skills",
                "Seek mentorship opportunities",
                "Contribute to open-source projects",
                "Build a portfolio of projects"
            ])
        elif career_level == "Mid-Level":
            recommendations.extend([
                "Develop leadership and team management skills",
                "Consider specializing in a niche area",
                "Start mentoring junior colleagues",
                "Pursue relevant certifications"
            ])
        elif career_level == "Senior":
            recommendations.extend([
                "Focus on strategic thinking and business impact",
                "Build cross-functional collaboration skills",
                "Consider moving into management roles",
                "Expand your professional network"
            ])
        
        return recommendations[:4]
    
    def _identify_skill_gaps(self, profile: ProfileData) -> List[str]:
        """Identify skill gaps based on industry standards"""
        gaps = []
        
        current_skills = [skill.lower() for skill in profile.get_skill_names()]
        industries = self._analyze_industry_focus(profile)
        
        # Industry-specific skill gaps
        if 'Technology' in industries:
            required_tech_skills = [
                'cloud computing', 'data analysis', 'cybersecurity',
                'agile methodology', 'version control'
            ]
            
            for skill in required_tech_skills:
                if not any(skill in current_skill for current_skill in current_skills):
                    gaps.append(skill.title())
        
        return gaps[:5]
    
    def _assess_market_demand(self, profile: ProfileData) -> str:
        """Assess market demand for the profile"""
        skill_relevance = self._calculate_skill_relevance(profile)
        experience_value = self._calculate_experience_value(profile)
        
        average_score = (skill_relevance + experience_value) / 2
        
        if average_score >= 80:
            return "Very High"
        elif average_score >= 60:
            return "High"
        elif average_score >= 40:
            return "Medium"
        else:
            return "Low"
    
    def _estimate_salary_range(self, profile: ProfileData) -> Dict[str, Any]:
        """Estimate salary range based on profile data"""
        years_exp = profile.get_years_of_experience()
        career_level = self._determine_career_level(profile)
        industries = self._analyze_industry_focus(profile)
        
        # Base salary estimates (simplified)
        base_ranges = {
            "Entry-Level": {"min": 45000, "max": 70000},
            "Mid-Level": {"min": 70000, "max": 110000},
            "Senior": {"min": 110000, "max": 160000},
            "Executive": {"min": 160000, "max": 300000}
        }
        
        base_range = base_ranges.get(career_level, base_ranges["Mid-Level"])
        
        # Industry multipliers
        industry_multipliers = {
            "Technology": 1.2,
            "Finance": 1.15,
            "Healthcare": 1.1,
            "Consulting": 1.1
        }
        
        multiplier = 1.0
        for industry in industries:
            if industry in industry_multipliers:
                multiplier = max(multiplier, industry_multipliers[industry])
        
        return {
            "currency": "USD",
            "min_salary": int(base_range["min"] * multiplier),
            "max_salary": int(base_range["max"] * multiplier),
            "confidence": "Medium",
            "factors": {
                "experience_years": years_exp,
                "career_level": career_level,
                "primary_industry": industries[0] if industries else "General",
                "market_multiplier": multiplier
            }
        }
    
    def _calculate_confidence_score(self, analysis: ProfileAnalysis) -> float:
        """Calculate confidence score for the analysis"""
        # Base confidence on data availability and completeness
        base_confidence = analysis.profile_completeness_score / 100
        
        # Adjust based on analysis depth
        if analysis.industry_focus:
            base_confidence += 0.1
        
        if analysis.skill_categories.get('technical'):
            base_confidence += 0.1
        
        if analysis.experience_value_score > 50:
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
