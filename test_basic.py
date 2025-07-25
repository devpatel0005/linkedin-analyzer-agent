"""
Basic tests for LinkedIn Analyzer Agent
"""

import pytest
import asyncio
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import settings
from src.models.profile import ProfileData, ExperienceItem, SkillItem
from src.services.analyzer import ProfileAnalyzer
from src.utils import validate_linkedin_url, clean_text, normalize_skill_name


class TestConfig:
    """Test configuration loading"""
    
    def test_settings_load(self):
        """Test that settings load correctly"""
        assert settings.APP_NAME == "LinkedIn Analyzer Agent"
        assert settings.APP_VERSION == "1.0.0"
        assert isinstance(settings.PORT, int)
    
    def test_directories_exist(self):
        """Test that required directories exist"""
        assert settings.DATA_DIR.exists()
        assert settings.LOGS_DIR.exists()
        assert settings.TEMP_DIR.exists()


class TestProfileModel:
    """Test profile data models"""
    
    def test_profile_creation(self):
        """Test ProfileData creation"""
        profile = ProfileData()
        profile.name = "John Doe"
        profile.headline = "Software Engineer"
        
        assert profile.name == "John Doe"
        assert profile.headline == "Software Engineer"
        assert isinstance(profile.experience, list)
        assert isinstance(profile.skills, list)
    
    def test_profile_to_dict(self):
        """Test profile to dictionary conversion"""
        profile = ProfileData()
        profile.name = "Jane Smith"
        profile.headline = "Data Scientist"
        
        profile_dict = profile.to_dict()
        assert isinstance(profile_dict, dict)
        assert profile_dict["name"] == "Jane Smith"
        assert profile_dict["headline"] == "Data Scientist"
    
    def test_experience_item(self):
        """Test ExperienceItem creation"""
        exp = ExperienceItem(
            title="Senior Developer",
            company="Tech Corp",
            duration="2 years"
        )
        
        assert exp.title == "Senior Developer"
        assert exp.company == "Tech Corp"
        assert exp.duration == "2 years"
    
    def test_skill_item(self):
        """Test SkillItem creation"""
        skill = SkillItem(name="Python", endorsements=25)
        
        assert skill.name == "Python"
        assert skill.endorsements == 25


class TestUtils:
    """Test utility functions"""
    
    def test_validate_linkedin_url(self):
        """Test LinkedIn URL validation"""
        valid_urls = [
            "https://www.linkedin.com/in/johndoe/",
            "https://www.linkedin.com/in/jane-smith",
            "https://www.linkedin.com/in/user123/"
        ]
        
        invalid_urls = [
            "https://linkedin.com/in/johndoe/",
            "https://www.linkedin.com/johndoe/",
            "https://facebook.com/johndoe",
            "not-a-url"
        ]
        
        for url in valid_urls:
            assert validate_linkedin_url(url), f"Should be valid: {url}"
        
        for url in invalid_urls:
            assert not validate_linkedin_url(url), f"Should be invalid: {url}"
    
    def test_clean_text(self):
        """Test text cleaning function"""
        test_cases = [
            ("  Hello   World  ", "Hello World"),
            ("Text with\nnewlines", "Text with newlines"),
            ("", ""),
            (None, "")
        ]
        
        for input_text, expected in test_cases:
            result = clean_text(input_text)
            assert result == expected, f"Expected '{expected}', got '{result}'"
    
    def test_normalize_skill_name(self):
        """Test skill name normalization"""
        test_cases = [
            ("python", "Python"),
            ("javascript", "JavaScript"),
            ("node.js", "Node.js"),
            ("AI", "AI"),
            ("machine learning", "Machine Learning")
        ]
        
        for input_skill, expected in test_cases:
            result = normalize_skill_name(input_skill)
            assert result == expected, f"Expected '{expected}', got '{result}'"


class TestAnalyzer:
    """Test profile analyzer"""
    
    def test_analyzer_creation(self):
        """Test ProfileAnalyzer creation"""
        analyzer = ProfileAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'skill_categories')
        assert hasattr(analyzer, 'trending_skills_2025')
    
    def test_career_level_detection(self):
        """Test career level detection"""
        analyzer = ProfileAnalyzer()
        
        # Create test profile
        profile = ProfileData()
        profile.name = "Test User"
        
        # Add senior level experience
        exp = ExperienceItem(
            title="Senior Software Engineer",
            company="Tech Corp",
            duration="3 years"
        )
        profile.experience.append(exp)
        
        career_level = analyzer._determine_career_level(profile)
        assert career_level in ["Entry-Level", "Mid-Level", "Senior", "Executive"]
    
    def test_skill_categorization(self):
        """Test skill categorization"""
        analyzer = ProfileAnalyzer()
        
        # Create test profile with skills
        profile = ProfileData()
        profile.skills = [
            SkillItem(name="Python"),
            SkillItem(name="Leadership"),
            SkillItem(name="Machine Learning")
        ]
        
        categories = analyzer._categorize_skills(profile)
        assert isinstance(categories, dict)
        assert 'technical' in categories
        assert 'soft_skills' in categories
    
    def test_completeness_score(self):
        """Test profile completeness scoring"""
        analyzer = ProfileAnalyzer()
        
        # Create complete profile
        profile = ProfileData()
        profile.name = "Complete User"
        profile.headline = "Software Engineer"
        profile.summary = "Experienced developer"
        profile.location = "New York"
        
        score = analyzer._calculate_completeness_score(profile)
        assert isinstance(score, int)
        assert 0 <= score <= 100


class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_profile_analysis_integration(self):
        """Test complete profile analysis flow"""
        # Create a comprehensive test profile
        profile = ProfileData()
        profile.name = "Integration Test User"
        profile.headline = "Senior Data Scientist"
        profile.location = "San Francisco, CA"
        profile.summary = "Experienced data scientist with machine learning expertise"
        
        # Add experience
        exp1 = ExperienceItem(
            title="Senior Data Scientist",
            company="Tech Giant",
            duration="3 years"
        )
        exp2 = ExperienceItem(
            title="Data Analyst",
            company="Startup Inc",
            duration="2 years"
        )
        profile.experience = [exp1, exp2]
        
        # Add skills
        profile.skills = [
            SkillItem(name="Python", endorsements=50),
            SkillItem(name="Machine Learning", endorsements=30),
            SkillItem(name="Leadership", endorsements=15)
        ]
        
        # Analyze profile
        analyzer = ProfileAnalyzer()
        analysis = await analyzer.analyze_profile(profile)
        
        # Verify analysis results
        assert analysis is not None
        assert analysis.career_level in ["Entry-Level", "Mid-Level", "Senior", "Executive"]
        assert isinstance(analysis.industry_focus, list)
        assert isinstance(analysis.skill_categories, dict)
        assert 0 <= analysis.profile_completeness_score <= 100
        assert 0 <= analysis.confidence_score <= 1.0


def run_tests():
    """Run all tests"""
    print("🧪 Running LinkedIn Analyzer Agent Tests...")
    print("=" * 50)
    
    # Run tests with pytest
    import subprocess
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", __file__, "-v"
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        return result.returncode == 0
    
    except FileNotFoundError:
        print("⚠️  pytest not found, running basic tests...")
        
        # Run basic tests without pytest
        try:
            # Test config
            test_config = TestConfig()
            test_config.test_settings_load()
            test_config.test_directories_exist()
            print("✅ Configuration tests passed")
            
            # Test profile model
            test_profile = TestProfileModel()
            test_profile.test_profile_creation()
            test_profile.test_profile_to_dict()
            print("✅ Profile model tests passed")
            
            # Test utils
            test_utils = TestUtils()
            test_utils.test_validate_linkedin_url()
            test_utils.test_clean_text()
            test_utils.test_normalize_skill_name()
            print("✅ Utility function tests passed")
            
            # Test analyzer
            test_analyzer = TestAnalyzer()
            test_analyzer.test_analyzer_creation()
            test_analyzer.test_career_level_detection()
            test_analyzer.test_skill_categorization()
            test_analyzer.test_completeness_score()
            print("✅ Analyzer tests passed")
            
            print("\n🎉 All basic tests passed!")
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
