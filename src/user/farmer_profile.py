"""
Farmer Profile System with Gender/Youth Segmentation
Enables personalized agricultural recommendations based on farmer demographics
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgeGroup(str, Enum):
    """Age group categories."""
    YOUTH = "youth"  # < 35 years
    ADULT = "adult"  # 35-60 years
    SENIOR = "senior"  # > 60 years


class Gender(str, Enum):
    """Gender categories."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class FarmSize(str, Enum):
    """Farm size categories."""
    SMALL = "small"  # < 5 hectares
    MEDIUM = "medium"  # 5-50 hectares
    LARGE = "large"  # > 50 hectares
    COMMUNAL = "communal"  # Communal land


class EducationLevel(str, Enum):
    """Education level categories."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    AGRICULTURAL_TRAINING = "agricultural_training"
    NONE = "none"


class FarmerProfile:
    """Individual farmer profile with demographics and preferences."""
    
    def __init__(
        self,
        user_id: str,
        name: Optional[str] = None,
        age: Optional[int] = None,
        gender: Optional[Gender] = None,
        location: Optional[Dict] = None
    ):
        self.user_id = user_id
        self.name = name
        self.age = age
        self.gender = gender
        self.location = location or {}
        
        # Derived field
        self.age_group = self._calculate_age_group()
        
        # Farm details
        self.farm_size: Optional[FarmSize] = None
        self.farm_size_hectares: Optional[float] = None
        self.primary_crops: List[str] = []
        self.livestock: List[str] = []
        
        # Socioeconomic
        self.education_level: Optional[EducationLevel] = None
        self.household_size: Optional[int] = None
        self.has_children: bool = False
        
        # Resources
        self.has_irrigation: bool = False
        self.has_machinery: bool = False
        self.has_smartphone: bool = False
        self.has_internet: bool = False
        self.has_electricity: bool = False
        
        # Financial
        self.has_bank_account: bool = False
        self.has_credit_access: bool = False
        self.annual_income_usd: Optional[float] = None
        
        # Support & training
        self.farmer_group_member: bool = False
        self.received_extension_services: bool = False
        self.completed_training: List[str] = []
        
        # Preferences
        self.language_preference: str = "english"  # english, shona, ndebele
        self.notification_preferences: Dict = {}
        
        # Metadata
        self.created_at: str = datetime.now().isoformat()
        self.updated_at: str = datetime.now().isoformat()
        self.profile_completeness: float = 0.0
    
    def _calculate_age_group(self) -> Optional[AgeGroup]:
        """Calculate age group from age."""
        if self.age is None:
            return None
        
        if self.age < 35:
            return AgeGroup.YOUTH
        elif self.age <= 60:
            return AgeGroup.ADULT
        else:
            return AgeGroup.SENIOR
    
    def update_profile(self, **kwargs):
        """Update profile fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Recalculate derived fields
        if 'age' in kwargs:
            self.age_group = self._calculate_age_group()
        
        self.updated_at = datetime.now().isoformat()
        self.profile_completeness = self._calculate_completeness()
    
    def _calculate_completeness(self) -> float:
        """Calculate profile completeness percentage."""
        total_fields = 20  # Key fields to track
        completed = 0
        
        if self.name: completed += 1
        if self.age: completed += 1
        if self.gender: completed += 1
        if self.location.get('district'): completed += 1
        if self.farm_size: completed += 1
        if self.farm_size_hectares: completed += 1
        if self.primary_crops: completed += 1
        if self.education_level: completed += 1
        if self.household_size: completed += 1
        if self.has_irrigation is not None: completed += 1
        if self.has_machinery is not None: completed += 1
        if self.has_smartphone is not None: completed += 1
        if self.has_bank_account is not None: completed += 1
        if self.has_credit_access is not None: completed += 1
        if self.annual_income_usd: completed += 1
        if self.farmer_group_member is not None: completed += 1
        if self.received_extension_services is not None: completed += 1
        if self.language_preference: completed += 1
        if self.livestock: completed += 1
        if self.has_children is not None: completed += 1
        
        return (completed / total_fields) * 100
    
    def to_dict(self) -> Dict:
        """Convert profile to dictionary."""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'age': self.age,
            'age_group': self.age_group.value if self.age_group else None,
            'gender': self.gender.value if self.gender else None,
            'location': self.location,
            'farm_size': self.farm_size.value if self.farm_size else None,
            'farm_size_hectares': self.farm_size_hectares,
            'primary_crops': self.primary_crops,
            'livestock': self.livestock,
            'education_level': self.education_level.value if self.education_level else None,
            'household_size': self.household_size,
            'has_children': self.has_children,
            'has_irrigation': self.has_irrigation,
            'has_machinery': self.has_machinery,
            'has_smartphone': self.has_smartphone,
            'has_internet': self.has_internet,
            'has_electricity': self.has_electricity,
            'has_bank_account': self.has_bank_account,
            'has_credit_access': self.has_credit_access,
            'annual_income_usd': self.annual_income_usd,
            'farmer_group_member': self.farmer_group_member,
            'received_extension_services': self.received_extension_services,
            'completed_training': self.completed_training,
            'language_preference': self.language_preference,
            'notification_preferences': self.notification_preferences,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'profile_completeness': self.profile_completeness
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FarmerProfile':
        """Create profile from dictionary."""
        profile = cls(
            user_id=data['user_id'],
            name=data.get('name'),
            age=data.get('age'),
            gender=Gender(data['gender']) if data.get('gender') else None,
            location=data.get('location', {})
        )
        
        # Update with all fields
        if data.get('farm_size'):
            profile.farm_size = FarmSize(data['farm_size'])
        if data.get('education_level'):
            profile.education_level = EducationLevel(data['education_level'])
        
        profile.farm_size_hectares = data.get('farm_size_hectares')
        profile.primary_crops = data.get('primary_crops', [])
        profile.livestock = data.get('livestock', [])
        profile.household_size = data.get('household_size')
        profile.has_children = data.get('has_children', False)
        profile.has_irrigation = data.get('has_irrigation', False)
        profile.has_machinery = data.get('has_machinery', False)
        profile.has_smartphone = data.get('has_smartphone', False)
        profile.has_internet = data.get('has_internet', False)
        profile.has_electricity = data.get('has_electricity', False)
        profile.has_bank_account = data.get('has_bank_account', False)
        profile.has_credit_access = data.get('has_credit_access', False)
        profile.annual_income_usd = data.get('annual_income_usd')
        profile.farmer_group_member = data.get('farmer_group_member', False)
        profile.received_extension_services = data.get('received_extension_services', False)
        profile.completed_training = data.get('completed_training', [])
        profile.language_preference = data.get('language_preference', 'english')
        profile.notification_preferences = data.get('notification_preferences', {})
        profile.created_at = data.get('created_at', profile.created_at)
        profile.updated_at = data.get('updated_at', profile.updated_at)
        
        return profile


class PersonalizationEngine:
    """Generates personalized recommendations based on farmer profile."""
    
    # Program mappings
    YOUTH_PROGRAMS = {
        'training': [
            'Young Farmers Business School',
            'Digital Agriculture Training',
            'Agripreneurship Program',
            'Climate-Smart Youth Initiative'
        ],
        'financing': [
            'Youth in Agriculture Fund',
            'Start-up Capital Grants',
            'Equipment Leasing Programs'
        ],
        'support': [
            'Youth Farmer Mentorship',
            'Market Linkage Support',
            'Technology Access Programs'
        ]
    }
    
    WOMEN_PROGRAMS = {
        'training': [
            'Women in Agriculture Leadership',
            'Nutrition-Sensitive Agriculture',
            'Value Addition Training',
            'Financial Literacy for Women Farmers'
        ],
        'financing': [
            'Women Economic Empowerment Fund',
            'Group Lending Schemes',
            'Women-Owned Enterprise Support'
        ],
        'support': [
            'Women Farmer Networks',
            'Childcare Support at Farmer Field Schools',
            'Gender-Responsive Extension Services'
        ]
    }
    
    SMALL_FARMER_PROGRAMS = {
        'training': [
            'Conservation Agriculture',
            'Intensive Farming Techniques',
            'Home Garden Management',
            'Agroforestry Systems'
        ],
        'financing': [
            'Microfinance Options',
            'Input Credit Schemes',
            'Contract Farming Opportunities'
        ],
        'support': [
            'Farmer Field Schools',
            'Community Seed Banks',
            'Group Marketing Support'
        ]
    }
    
    def __init__(self):
        self.recommendations_cache = {}
    
    def generate_personalized_context(self, profile: FarmerProfile) -> str:
        """Generate personalized context string for RAG queries."""
        context_parts = []
        
        # Age/gender specific context
        if profile.age_group == AgeGroup.YOUTH:
            context_parts.append(
                "Note: This farmer is a youth (<35 years). Consider highlighting:\n"
                "- Youth-friendly financing options\n"
                "- Technology adoption opportunities\n"
                "- Entrepreneurship and value addition\n"
                "- Digital agriculture tools\n"
            )
        
        if profile.gender == Gender.FEMALE:
            context_parts.append(
                "Note: This farmer is female. Consider highlighting:\n"
                "- Women-specific support programs\n"
                "- Gender-responsive extension services\n"
                "- Women farmer networks and groups\n"
                "- Time-saving technologies\n"
                "- Nutrition-sensitive agriculture\n"
            )
        
        # Farm size context
        if profile.farm_size == FarmSize.SMALL:
            context_parts.append(
                "Note: Small-scale farmer (<5ha). Consider:\n"
                "- Intensive farming methods\n"
                "- High-value crops\n"
                "- Space-efficient practices\n"
                "- Microfinance options\n"
            )
        elif profile.farm_size == FarmSize.LARGE:
            context_parts.append(
                "Note: Large-scale farmer (>50ha). Consider:\n"
                "- Mechanization options\n"
                "- Bulk input procurement\n"
                "- Commercial farming practices\n"
                "- Export market opportunities\n"
            )
        
        # Resource constraints
        if not profile.has_irrigation:
            context_parts.append(
                "Note: No irrigation access. Emphasize:\n"
                "- Drought-resistant varieties\n"
                "- Rainwater harvesting\n"
                "- Water conservation techniques\n"
            )
        
        if not profile.has_machinery:
            context_parts.append(
                "Note: Limited machinery access. Consider:\n"
                "- Labor-efficient methods\n"
                "- Animal traction options\n"
                "- Equipment hire services\n"
            )
        
        # Financial context
        if not profile.has_credit_access:
            context_parts.append(
                "Note: Limited credit access. Emphasize:\n"
                "- Low-capital interventions\n"
                "- Microfinance options\n"
                "- Group lending schemes\n"
            )
        
        return "\n".join(context_parts) if context_parts else ""
    
    def get_relevant_programs(self, profile: FarmerProfile) -> Dict[str, List[str]]:
        """Get relevant programs for the farmer."""
        programs = {
            'training': [],
            'financing': [],
            'support': [],
            'priority_info': []
        }
        
        # Youth programs
        if profile.age_group == AgeGroup.YOUTH:
            programs['training'].extend(self.YOUTH_PROGRAMS['training'])
            programs['financing'].extend(self.YOUTH_PROGRAMS['financing'])
            programs['support'].extend(self.YOUTH_PROGRAMS['support'])
            programs['priority_info'].append(
                "🎯 You qualify for youth-specific programs (under 35 years)"
            )
        
        # Women programs
        if profile.gender == Gender.FEMALE:
            programs['training'].extend(self.WOMEN_PROGRAMS['training'])
            programs['financing'].extend(self.WOMEN_PROGRAMS['financing'])
            programs['support'].extend(self.WOMEN_PROGRAMS['support'])
            programs['priority_info'].append(
                "👩‍🌾 Women-specific support programs available"
            )
        
        # Small farmer programs
        if profile.farm_size == FarmSize.SMALL:
            programs['training'].extend(self.SMALL_FARMER_PROGRAMS['training'])
            programs['financing'].extend(self.SMALL_FARMER_PROGRAMS['financing'])
            programs['support'].extend(self.SMALL_FARMER_PROGRAMS['support'])
        
        # Remove duplicates
        for key in ['training', 'financing', 'support']:
            programs[key] = list(set(programs[key]))
        
        return programs
    
    def get_personalized_recommendations(
        self,
        profile: FarmerProfile,
        query_topic: Optional[str] = None
    ) -> Dict:
        """Get personalized recommendations for a farmer."""
        recommendations = {
            'profile_summary': self._generate_profile_summary(profile),
            'programs': self.get_relevant_programs(profile),
            'considerations': [],
            'next_steps': []
        }
        
        # Add considerations based on profile
        if profile.age_group == AgeGroup.YOUTH:
            recommendations['considerations'].append(
                "As a youth farmer, you may have advantages in technology adoption "
                "and access to youth-specific financing."
            )
        
        if profile.gender == Gender.FEMALE and profile.has_children:
            recommendations['considerations'].append(
                "Consider time-saving technologies and practices that accommodate "
                "household responsibilities."
            )
        
        if not profile.has_irrigation and profile.location.get('natural_region') in ['IV', 'V']:
            recommendations['considerations'].append(
                "In your region without irrigation, prioritize drought-resistant "
                "crops and water conservation."
            )
        
        if profile.profile_completeness < 50:
            recommendations['next_steps'].append(
                "Complete your profile to receive more personalized recommendations"
            )
        
        if not profile.farmer_group_member:
            recommendations['next_steps'].append(
                "Consider joining a farmer group for collective marketing and "
                "better input prices"
            )
        
        if not profile.received_extension_services:
            recommendations['next_steps'].append(
                "Contact your local AGRITEX office for free extension services"
            )
        
        return recommendations
    
    def _generate_profile_summary(self, profile: FarmerProfile) -> str:
        """Generate a human-readable profile summary."""
        parts = []
        
        # Demographics
        if profile.age_group:
            parts.append(f"{profile.age_group.value.title()} farmer")
        if profile.gender:
            parts.append(f"({profile.gender.value})")
        
        # Farm
        if profile.farm_size:
            parts.append(f"with {profile.farm_size.value} farm")
        if profile.farm_size_hectares:
            parts.append(f"({profile.farm_size_hectares}ha)")
        
        # Location
        if profile.location.get('district'):
            parts.append(f"in {profile.location['district']}")
        
        # Crops
        if profile.primary_crops:
            crops_str = ", ".join(profile.primary_crops[:3])
            parts.append(f"growing {crops_str}")
        
        return " ".join(parts)


class FarmerProfileManager:
    """Manages farmer profiles with persistence."""
    
    def __init__(self, storage_dir: str = None):
        if storage_dir is None:
            storage_dir = Path(__file__).parent.parent.parent / "data" / "farmer_profiles"
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.personalization = PersonalizationEngine()
    
    def create_profile(self, user_id: str, **kwargs) -> FarmerProfile:
        """Create a new farmer profile."""
        profile = FarmerProfile(user_id=user_id, **kwargs)
        self.save_profile(profile)
        logger.info(f"Created profile for user {user_id}")
        return profile
    
    def get_profile(self, user_id: str) -> Optional[FarmerProfile]:
        """Retrieve a farmer profile."""
        profile_file = self.storage_dir / f"{user_id}.json"
        
        if not profile_file.exists():
            return None
        
        with open(profile_file, 'r') as f:
            data = json.load(f)
        
        return FarmerProfile.from_dict(data)
    
    def save_profile(self, profile: FarmerProfile):
        """Save a farmer profile."""
        profile_file = self.storage_dir / f"{profile.user_id}.json"
        
        with open(profile_file, 'w') as f:
            json.dump(profile.to_dict(), f, indent=2)
    
    def update_profile(self, user_id: str, **kwargs) -> Optional[FarmerProfile]:
        """Update an existing profile."""
        profile = self.get_profile(user_id)
        
        if not profile:
            return None
        
        profile.update_profile(**kwargs)
        self.save_profile(profile)
        logger.info(f"Updated profile for user {user_id}")
        
        return profile
    
    def delete_profile(self, user_id: str) -> bool:
        """Delete a farmer profile."""
        profile_file = self.storage_dir / f"{user_id}.json"
        
        if profile_file.exists():
            profile_file.unlink()
            logger.info(f"Deleted profile for user {user_id}")
            return True
        
        return False
    
    def list_profiles(self, filters: Optional[Dict] = None) -> List[FarmerProfile]:
        """List all profiles, optionally filtered."""
        profiles = []
        
        for profile_file in self.storage_dir.glob("*.json"):
            with open(profile_file, 'r') as f:
                data = json.load(f)
            
            profile = FarmerProfile.from_dict(data)
            
            # Apply filters if provided
            if filters:
                match = True
                for key, value in filters.items():
                    if key == 'age_group' and profile.age_group != AgeGroup(value):
                        match = False
                    elif key == 'gender' and profile.gender != Gender(value):
                        match = False
                    elif key == 'farm_size' and profile.farm_size != FarmSize(value):
                        match = False
                    elif key == 'district' and profile.location.get('district') != value:
                        match = False
                
                if match:
                    profiles.append(profile)
            else:
                profiles.append(profile)
        
        return profiles
    
    def get_statistics(self) -> Dict:
        """Get aggregate statistics about farmers."""
        profiles = self.list_profiles()
        
        stats = {
            'total_farmers': len(profiles),
            'by_age_group': {},
            'by_gender': {},
            'by_farm_size': {},
            'by_district': {},
            'avg_profile_completeness': 0.0,
            'with_irrigation': 0,
            'with_machinery': 0,
            'with_credit_access': 0,
            'farmer_group_members': 0
        }
        
        for profile in profiles:
            # Age group
            if profile.age_group:
                age_key = profile.age_group.value
                stats['by_age_group'][age_key] = stats['by_age_group'].get(age_key, 0) + 1
            
            # Gender
            if profile.gender:
                gender_key = profile.gender.value
                stats['by_gender'][gender_key] = stats['by_gender'].get(gender_key, 0) + 1
            
            # Farm size
            if profile.farm_size:
                size_key = profile.farm_size.value
                stats['by_farm_size'][size_key] = stats['by_farm_size'].get(size_key, 0) + 1
            
            # District
            if profile.location.get('district'):
                district = profile.location['district']
                stats['by_district'][district] = stats['by_district'].get(district, 0) + 1
            
            # Aggregate metrics
            stats['avg_profile_completeness'] += profile.profile_completeness
            if profile.has_irrigation: stats['with_irrigation'] += 1
            if profile.has_machinery: stats['with_machinery'] += 1
            if profile.has_credit_access: stats['with_credit_access'] += 1
            if profile.farmer_group_member: stats['farmer_group_members'] += 1
        
        if profiles:
            stats['avg_profile_completeness'] /= len(profiles)
        
        return stats


if __name__ == "__main__":
    # Test the farmer profile system
    manager = FarmerProfileManager()
    
    # Create sample profiles
    youth_female = manager.create_profile(
        user_id="farmer_001",
        name="Tendai Moyo",
        age=28,
        gender=Gender.FEMALE,
        location={'district': 'Mashonaland East', 'natural_region': 'II'}
    )
    
    youth_female.update_profile(
        farm_size=FarmSize.SMALL,
        farm_size_hectares=3.5,
        primary_crops=['maize', 'beans', 'vegetables'],
        has_children=True,
        has_irrigation=False,
        has_smartphone=True,
        education_level=EducationLevel.SECONDARY
    )
    
    manager.save_profile(youth_female)
    
    # Get recommendations
    personalizer = PersonalizationEngine()
    context = personalizer.generate_personalized_context(youth_female)
    programs = personalizer.get_relevant_programs(youth_female)
    
    print("Profile Summary:")
    print(personalizer._generate_profile_summary(youth_female))
    print(f"\nProfile Completeness: {youth_female.profile_completeness:.1f}%")
    print(f"\nPersonalized Context:\n{context}")
    print(f"\nAvailable Programs:")
    print(f"Training: {len(programs['training'])} programs")
    print(f"Financing: {len(programs['financing'])} programs")
    print(f"Support: {len(programs['support'])} programs")
