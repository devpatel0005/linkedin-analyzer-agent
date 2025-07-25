"""
Export Service for LinkedIn Analyzer Agent
"""

import json
import csv
import io
import logging
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from ..models.profile import ProfileData, ProfileAnalysis
from ..config import settings

logger = logging.getLogger(__name__)


class ExportService:
    """Service for exporting profile data in various formats"""
    
    def __init__(self):
        self.export_dir = settings.DATA_DIR / "exports"
        self.export_dir.mkdir(exist_ok=True)
    
    def export_to_json(self, profile_data: ProfileData, analysis: ProfileAnalysis = None) -> str:
        """Export profile data to JSON format"""
        try:
            export_data = {
                "profile": profile_data.to_dict(),
                "analysis": analysis.__dict__ if analysis else None,
                "exported_at": datetime.now().isoformat(),
                "export_format": "json",
                "version": "1.0"
            }
            
            # Generate filename
            safe_name = "".join(c for c in profile_data.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.export_dir / filename
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Profile exported to JSON: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            raise
    
    def export_to_csv(self, profiles: List[ProfileData], analyses: List[ProfileAnalysis] = None) -> str:
        """Export multiple profiles to CSV format"""
        try:
            # Generate filename
            filename = f"linkedin_profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = self.export_dir / filename
            
            # Prepare CSV data
            fieldnames = [
                'name', 'headline', 'location', 'industry', 'current_position',
                'current_company', 'years_experience', 'skills_count', 'education_count',
                'profile_url', 'scraped_at'
            ]
            
            # Add analysis fields if available
            if analyses:
                fieldnames.extend([
                    'career_level', 'industry_focus', 'completeness_score',
                    'skill_relevance_score', 'experience_value_score',
                    'market_competitiveness_score', 'market_demand'
                ])
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for i, profile in enumerate(profiles):
                    row = {
                        'name': profile.name,
                        'headline': profile.headline,
                        'location': profile.location,
                        'industry': profile.industry,
                        'current_position': profile.current_position,
                        'current_company': profile.current_company,
                        'years_experience': profile.get_years_of_experience(),
                        'skills_count': len(profile.skills),
                        'education_count': len(profile.education),
                        'profile_url': profile.profile_url,
                        'scraped_at': profile.scraped_at.isoformat() if profile.scraped_at else ''
                    }
                    
                    # Add analysis data if available
                    if analyses and i < len(analyses):
                        analysis = analyses[i]
                        row.update({
                            'career_level': analysis.career_level,
                            'industry_focus': ', '.join(analysis.industry_focus),
                            'completeness_score': analysis.profile_completeness_score,
                            'skill_relevance_score': analysis.skill_relevance_score,
                            'experience_value_score': analysis.experience_value_score,
                            'market_competitiveness_score': analysis.market_competitiveness_score,
                            'market_demand': analysis.market_demand
                        })
                    
                    writer.writerow(row)
            
            logger.info(f"Profiles exported to CSV: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            raise
    
    def export_to_excel(self, profiles: List[ProfileData], analyses: List[ProfileAnalysis] = None) -> str:
        """Export profiles to Excel format with multiple sheets"""
        try:
            import pandas as pd
            
            # Generate filename
            filename = f"linkedin_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath = self.export_dir / filename
            
            # Prepare data for different sheets
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                
                # Main profiles sheet
                profiles_data = []
                for profile in profiles:
                    profiles_data.append({
                        'Name': profile.name,
                        'Headline': profile.headline,
                        'Location': profile.location,
                        'Current Position': profile.current_position,
                        'Current Company': profile.current_company,
                        'Years Experience': profile.get_years_of_experience(),
                        'Skills Count': len(profile.skills),
                        'Education Count': len(profile.education),
                        'Profile URL': profile.profile_url,
                        'Scraped At': profile.scraped_at
                    })
                
                df_profiles = pd.DataFrame(profiles_data)
                df_profiles.to_excel(writer, sheet_name='Profiles', index=False)
                
                # Analysis sheet
                if analyses:
                    analysis_data = []
                    for analysis in analyses:
                        analysis_data.append({
                            'Profile ID': analysis.profile_id,
                            'Career Level': analysis.career_level,
                            'Industry Focus': ', '.join(analysis.industry_focus),
                            'Completeness Score': analysis.profile_completeness_score,
                            'Skill Relevance': analysis.skill_relevance_score,
                            'Experience Value': analysis.experience_value_score,
                            'Market Competitiveness': analysis.market_competitiveness_score,
                            'Market Demand': analysis.market_demand,
                            'Analyzed At': analysis.analyzed_at
                        })
                    
                    df_analysis = pd.DataFrame(analysis_data)
                    df_analysis.to_excel(writer, sheet_name='Analysis', index=False)
                
                # Skills summary sheet
                all_skills = []
                for profile in profiles:
                    for skill in profile.get_skill_names():
                        all_skills.append({
                            'Profile': profile.name,
                            'Skill': skill
                        })
                
                if all_skills:
                    df_skills = pd.DataFrame(all_skills)
                    skill_counts = df_skills['Skill'].value_counts().reset_index()
                    skill_counts.columns = ['Skill', 'Frequency']
                    skill_counts.to_excel(writer, sheet_name='Skills Summary', index=False)
            
            logger.info(f"Profiles exported to Excel: {filepath}")
            return str(filepath)
            
        except ImportError:
            logger.error("pandas and openpyxl are required for Excel export")
            raise
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            raise
    
    def export_profile_report(self, profile_data: ProfileData, analysis: ProfileAnalysis) -> str:
        """Generate a comprehensive profile report in HTML format"""
        try:
            # Generate filename
            safe_name = "".join(c for c in profile_data.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_name}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            filepath = self.export_dir / filename
            
            # Generate HTML report
            html_content = self._generate_html_report(profile_data, analysis)
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Profile report generated: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating profile report: {e}")
            raise
    
    def _generate_html_report(self, profile: ProfileData, analysis: ProfileAnalysis) -> str:
        """Generate HTML content for profile report"""
        
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>LinkedIn Profile Analysis - {profile.name}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    border-bottom: 3px solid #0077b5;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .profile-name {{
                    color: #0077b5;
                    font-size: 2.5em;
                    margin: 0;
                }}
                .headline {{
                    font-size: 1.2em;
                    color: #666;
                    margin: 10px 0;
                }}
                .section {{
                    margin: 30px 0;
                    padding: 20px;
                    border-left: 4px solid #0077b5;
                    background: #f9f9f9;
                }}
                .section h2 {{
                    color: #0077b5;
                    margin-top: 0;
                }}
                .score-card {{
                    display: inline-block;
                    background: #0077b5;
                    color: white;
                    padding: 15px 20px;
                    margin: 10px;
                    border-radius: 8px;
                    text-align: center;
                    min-width: 120px;
                }}
                .score-value {{
                    font-size: 2em;
                    font-weight: bold;
                }}
                .score-label {{
                    font-size: 0.9em;
                }}
                .skills-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }}
                .skill-category {{
                    background: #e8f4fd;
                    padding: 15px;
                    border-radius: 8px;
                }}
                .recommendations {{
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 class="profile-name">{profile.name}</h1>
                    <p class="headline">{profile.headline}</p>
                    <p>{profile.location}</p>
                </div>
                
                <div class="section">
                    <h2>Analysis Scores</h2>
                    <div class="score-card">
                        <div class="score-value">{analysis.profile_completeness_score}</div>
                        <div class="score-label">Completeness</div>
                    </div>
                    <div class="score-card">
                        <div class="score-value">{analysis.skill_relevance_score}</div>
                        <div class="score-label">Skill Relevance</div>
                    </div>
                    <div class="score-card">
                        <div class="score-value">{analysis.experience_value_score}</div>
                        <div class="score-label">Experience Value</div>
                    </div>
                    <div class="score-card">
                        <div class="score-value">{analysis.market_competitiveness_score}</div>
                        <div class="score-label">Market Competitiveness</div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Career Analysis</h2>
                    <p><strong>Career Level:</strong> {analysis.career_level}</p>
                    <p><strong>Industry Focus:</strong> {', '.join(analysis.industry_focus)}</p>
                    <p><strong>Market Demand:</strong> {analysis.market_demand}</p>
                    <p><strong>Years of Experience:</strong> {profile.get_years_of_experience()}</p>
                </div>
                
                <div class="section">
                    <h2>Skills Analysis</h2>
                    <div class="skills-grid">
                        {self._generate_skills_html(analysis.skill_categories)}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Recommendations</h2>
                    <div class="recommendations">
                        <h3>Skill Recommendations</h3>
                        <ul>
                            {self._generate_list_html(analysis.skill_recommendations)}
                        </ul>
                    </div>
                    <div class="recommendations">
                        <h3>Career Recommendations</h3>
                        <ul>
                            {self._generate_list_html(analysis.career_recommendations)}
                        </ul>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Experience Summary</h2>
                    {self._generate_experience_html(profile.experience)}
                </div>
                
                <div class="footer">
                    <p>Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p>LinkedIn Analyzer Agent v1.0</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def _generate_skills_html(self, skill_categories: Dict[str, List[str]]) -> str:
        """Generate HTML for skills categories"""
        html = ""
        for category, skills in skill_categories.items():
            if skills:
                html += f"""
                <div class="skill-category">
                    <h4>{category.replace('_', ' ').title()}</h4>
                    <p>{', '.join(skills[:10])}</p>
                </div>
                """
        return html
    
    def _generate_list_html(self, items: List[str]) -> str:
        """Generate HTML list items"""
        return ''.join(f"<li>{item}</li>" for item in items)
    
    def _generate_experience_html(self, experience: List) -> str:
        """Generate HTML for experience section"""
        if not experience:
            return "<p>No experience data available.</p>"
        
        html = ""
        for exp in experience[:5]:  # Show top 5 experiences
            html += f"""
            <div style="margin: 15px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
                <h4>{getattr(exp, 'title', 'N/A')}</h4>
                <p><strong>{getattr(exp, 'company', 'N/A')}</strong></p>
                <p>{getattr(exp, 'duration', 'N/A')}</p>
                <p>{getattr(exp, 'description', '')[:200]}...</p>
            </div>
            """
        
        return html
    
    def get_export_statistics(self) -> Dict[str, Any]:
        """Get export statistics"""
        try:
            export_files = list(self.export_dir.glob("*"))
            
            stats = {
                "total_exports": len(export_files),
                "export_formats": {},
                "recent_exports": [],
                "total_size_mb": 0
            }
            
            for file in export_files:
                # Count by extension
                ext = file.suffix.lower()
                stats["export_formats"][ext] = stats["export_formats"].get(ext, 0) + 1
                
                # Add to recent exports (last 10)
                if len(stats["recent_exports"]) < 10:
                    stats["recent_exports"].append({
                        "filename": file.name,
                        "size_kb": file.stat().st_size / 1024,
                        "created_at": datetime.fromtimestamp(file.stat().st_ctime).isoformat()
                    })
                
                # Add to total size
                stats["total_size_mb"] += file.stat().st_size / (1024 * 1024)
            
            stats["total_size_mb"] = round(stats["total_size_mb"], 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting export statistics: {e}")
            return {"error": str(e)}
