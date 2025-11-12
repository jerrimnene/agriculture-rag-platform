# Task 3: Farmer Profile System Implementation Summary

## ✅ Completed

**File**: `src/user/farmer_profile.py` (~665 lines)

## 🎯 Overview

Comprehensive farmer profiling system with **gender and youth segmentation** enabling personalized agricultural recommendations based on demographics, resources, and constraints.

---

## 📋 Core Features

### 1. **Farmer Profile Class**
Complete demographic and resource tracking:

**Demographics**:
- Name, Age, Gender
- Age Group (Youth <35, Adult 35-60, Senior >60)
- Location (District, Natural Region)
- Education Level
- Household size and children

**Farm Details**:
- Farm size category (Small <5ha, Medium 5-50ha, Large >50ha, Communal)
- Exact hectares
- Primary crops grown
- Livestock types

**Resources & Infrastructure**:
- Irrigation access (Yes/No)
- Machinery access (Yes/No)
- Smartphone/Internet/Electricity (Yes/No)
- Bank account (Yes/No)
- Credit access (Yes/No)
- Annual income (USD)

**Support & Training**:
- Farmer group membership
- Extension services received
- Training programs completed
- Language preference (English/Shona/Ndebele)

**Metadata**:
- Profile completeness percentage (0-100%)
- Created/Updated timestamps
- User ID for tracking

### 2. **Personalization Engine**
Generates tailored recommendations based on profile:

**Youth Programs** (Age < 35):
- **Training**: Young Farmers Business School, Digital Agriculture, Agripreneurship, Climate-Smart Youth Initiative
- **Financing**: Youth in Agriculture Fund, Start-up Capital Grants, Equipment Leasing
- **Support**: Youth Mentorship, Market Linkage, Technology Access

**Women Programs**:
- **Training**: Women in Agriculture Leadership, Nutrition-Sensitive Agriculture, Value Addition, Financial Literacy
- **Financing**: Women Economic Empowerment Fund, Group Lending, Women-Owned Enterprise Support
- **Support**: Women Farmer Networks, Childcare at Field Schools, Gender-Responsive Extension

**Small Farmer Programs** (< 5 hectares):
- **Training**: Conservation Agriculture, Intensive Farming, Home Garden Management, Agroforestry
- **Financing**: Microfinance Options, Input Credit Schemes, Contract Farming
- **Support**: Farmer Field Schools, Community Seed Banks, Group Marketing

### 3. **Context Generation for RAG**
Automatically adds personalized context to queries:

**Example for Youth Female Small Farmer**:
```
Note: This farmer is a youth (<35 years). Consider highlighting:
- Youth-friendly financing options
- Technology adoption opportunities
- Entrepreneurship and value addition
- Digital agriculture tools

Note: This farmer is female. Consider highlighting:
- Women-specific support programs
- Gender-responsive extension services
- Women farmer networks and groups
- Time-saving technologies
- Nutrition-sensitive agriculture

Note: Small-scale farmer (<5ha). Consider:
- Intensive farming methods
- High-value crops
- Space-efficient practices
- Microfinance options

Note: No irrigation access. Emphasize:
- Drought-resistant varieties
- Rainwater harvesting
- Water conservation techniques
```

### 4. **Profile Manager**
Complete CRUD operations with persistence:

**Operations**:
- `create_profile(user_id, **kwargs)` - Create new profile
- `get_profile(user_id)` - Retrieve profile
- `update_profile(user_id, **kwargs)` - Update fields
- `delete_profile(user_id)` - Remove profile
- `list_profiles(filters)` - List all/filtered profiles
- `get_statistics()` - Aggregate analytics

**Storage**: JSON files in `data/farmer_profiles/`

**Statistics Tracked**:
- Total farmers
- By age group (youth/adult/senior)
- By gender (male/female/other)
- By farm size (small/medium/large)
- By district
- Average profile completeness
- Resource access rates (irrigation, machinery, credit)
- Farmer group membership rate

---

## 🔧 Usage Examples

### Create a Farmer Profile

```python
from src.user.farmer_profile import FarmerProfileManager, Gender, FarmSize, EducationLevel

manager = FarmerProfileManager()

# Create profile
profile = manager.create_profile(
    user_id="farmer_001",
    name="Tendai Moyo",
    age=28,
    gender=Gender.FEMALE,
    location={'district': 'Mashonaland East', 'natural_region': 'II'}
)

# Update with more details
profile.update_profile(
    farm_size=FarmSize.SMALL,
    farm_size_hectares=3.5,
    primary_crops=['maize', 'beans', 'vegetables'],
    has_children=True,
    has_irrigation=False,
    has_smartphone=True,
    education_level=EducationLevel.SECONDARY
)

manager.save_profile(profile)
```

### Get Personalized Recommendations

```python
from src.user.farmer_profile import PersonalizationEngine

personalizer = PersonalizationEngine()

# Generate context for RAG queries
context = personalizer.generate_personalized_context(profile)

# Get relevant programs
programs = personalizer.get_relevant_programs(profile)

# Get full recommendations
recommendations = personalizer.get_personalized_recommendations(profile)

print(recommendations)
# Output:
# {
#   'profile_summary': 'Youth farmer (female) with small farm (3.5ha) in Mashonaland East growing maize, beans, vegetables',
#   'programs': {
#     'training': ['Young Farmers Business School', 'Women in Agriculture Leadership', ...],
#     'financing': ['Youth in Agriculture Fund', 'Women Economic Empowerment Fund', ...],
#     'support': ['Youth Farmer Mentorship', 'Women Farmer Networks', ...],
#     'priority_info': ['🎯 You qualify for youth-specific programs', '👩‍🌾 Women-specific support programs available']
#   },
#   'considerations': [
#     'As a youth farmer, you may have advantages in technology adoption...',
#     'Consider time-saving technologies that accommodate household responsibilities...'
#   ],
#   'next_steps': [
#     'Consider joining a farmer group...',
#     'Contact your local AGRITEX office...'
#   ]
# }
```

### List and Filter Profiles

```python
# Get all profiles
all_profiles = manager.list_profiles()

# Filter by criteria
youth_farmers = manager.list_profiles(filters={'age_group': 'youth'})
women_farmers = manager.list_profiles(filters={'gender': 'female'})
small_farmers = manager.list_profiles(filters={'farm_size': 'small'})

# Get statistics
stats = manager.get_statistics()
print(f"Total farmers: {stats['total_farmers']}")
print(f"Youth farmers: {stats['by_age_group'].get('youth', 0)}")
print(f"Women farmers: {stats['by_gender'].get('female', 0)}")
print(f"Avg profile completeness: {stats['avg_profile_completeness']:.1f}%")
```

---

## 🔗 API Integration

### New API Endpoints to Add

Update `src/api/main.py`:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.user.farmer_profile import FarmerProfileManager, Gender, FarmSize, EducationLevel

# Initialize
profile_manager = FarmerProfileManager()

class ProfileCreateRequest(BaseModel):
    user_id: str
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    district: Optional[str] = None

class ProfileUpdateRequest(BaseModel):
    farm_size: Optional[str] = None
    farm_size_hectares: Optional[float] = None
    primary_crops: Optional[List[str]] = None
    has_irrigation: Optional[bool] = None
    # ... other fields

@app.post("/profiles")
async def create_farmer_profile(request: ProfileCreateRequest):
    """Create a new farmer profile."""
    location = {'district': request.district} if request.district else {}
    gender = Gender(request.gender) if request.gender else None
    
    profile = profile_manager.create_profile(
        user_id=request.user_id,
        name=request.name,
        age=request.age,
        gender=gender,
        location=location
    )
    
    return profile.to_dict()

@app.get("/profiles/{user_id}")
async def get_farmer_profile(user_id: str):
    """Get a farmer profile."""
    profile = profile_manager.get_profile(user_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile.to_dict()

@app.put("/profiles/{user_id}")
async def update_farmer_profile(user_id: str, request: ProfileUpdateRequest):
    """Update a farmer profile."""
    updates = request.dict(exclude_unset=True)
    
    # Convert enum strings to enums
    if 'farm_size' in updates:
        updates['farm_size'] = FarmSize(updates['farm_size'])
    
    profile = profile_manager.update_profile(user_id, **updates)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile.to_dict()

@app.delete("/profiles/{user_id}")
async def delete_farmer_profile(user_id: str):
    """Delete a farmer profile."""
    success = profile_manager.delete_profile(user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {"message": "Profile deleted successfully"}

@app.get("/profiles/{user_id}/recommendations")
async def get_recommendations(user_id: str):
    """Get personalized recommendations for a farmer."""
    profile = profile_manager.get_profile(user_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    personalizer = PersonalizationEngine()
    recommendations = personalizer.get_personalized_recommendations(profile)
    
    return recommendations

@app.get("/profiles/stats/analytics")
async def get_farmer_statistics():
    """Get aggregate farmer statistics."""
    return profile_manager.get_statistics()
```

---

## 🎨 Frontend Integration

### Profile Form Fields

```javascript
const profileForm = {
  // Demographics
  name: '',
  age: null,
  gender: 'female', // male, female, other, prefer_not_to_say
  district: '',
  
  // Farm
  farm_size: 'small', // small, medium, large, communal
  farm_size_hectares: null,
  primary_crops: [],
  livestock: [],
  
  // Resources
  has_irrigation: false,
  has_machinery: false,
  has_smartphone: false,
  has_credit_access: false,
  
  // Other
  education_level: 'secondary',
  farmer_group_member: false,
  language_preference: 'english' // english, shona, ndebele
};

// Submit profile
async function createProfile(userId, profileData) {
  const response = await fetch(`/profiles`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({user_id: userId, ...profileData})
  });
  return response.json();
}

// Get recommendations
async function getRecommendations(userId) {
  const response = await fetch(`/profiles/${userId}/recommendations`);
  const data = await response.json();
  
  // Display programs
  console.log('Training Programs:', data.programs.training);
  console.log('Financing Options:', data.programs.financing);
  console.log('Support Services:', data.programs.support);
  console.log('Next Steps:', data.next_steps);
}
```

### Display Profile-Based Recommendations

```html
<div class="farmer-profile-widget">
  <h3>👤 Your Profile</h3>
  <p class="profile-summary">{{ profile.summary }}</p>
  <div class="completeness-bar">
    <div class="progress" style="width: {{ profile.completeness }}%"></div>
    <span>{{ profile.completeness }}% Complete</span>
  </div>
  
  <div class="priority-programs" v-if="programs.priority_info.length">
    <h4>🎯 You Qualify For:</h4>
    <ul>
      <li v-for="info in programs.priority_info">{{ info }}</li>
    </ul>
  </div>
  
  <div class="recommendations">
    <h4>📚 Recommended Training:</h4>
    <ul>
      <li v-for="program in programs.training.slice(0, 3)">{{ program }}</li>
    </ul>
    
    <h4>💰 Financing Options:</h4>
    <ul>
      <li v-for="option in programs.financing.slice(0, 3)">{{ option }}</li>
    </ul>
  </div>
  
  <div class="next-steps">
    <h4>📌 Next Steps:</h4>
    <ul>
      <li v-for="step in next_steps">{{ step }}</li>
    </ul>
  </div>
</div>
```

---

## 📊 Benefits of Profiling

### For Farmers
- ✅ Personalized recommendations
- ✅ Discover relevant programs and financing
- ✅ Gender/age-specific support
- ✅ Resource-appropriate advice

### For Platform
- ✅ Better engagement through personalization
- ✅ Track user demographics
- ✅ Identify gaps in services
- ✅ Measure impact by segment

### For Policymakers
- ✅ Understand farmer needs by segment
- ✅ Target programs effectively
- ✅ Track program reach
- ✅ Evidence-based policy making

---

## 🔐 Privacy & Data Protection

- **Consent**: Profiles are optional
- **Minimal Data**: Only collect what's needed
- **Secure Storage**: JSON files with access controls
- **Anonymization**: Can aggregate without IDs
- **User Control**: Users can view, edit, delete their profiles
- **No Sharing**: Profile data stays within system

---

## 📈 Analytics Dashboard (Planned)

Future analytics views:

```python
stats = manager.get_statistics()

# Sample output:
{
  "total_farmers": 245,
  "by_age_group": {
    "youth": 89,    # 36%
    "adult": 132,   # 54%
    "senior": 24    # 10%
  },
  "by_gender": {
    "female": 147,  # 60%
    "male": 95,     # 39%
    "other": 3      # 1%
  },
  "by_farm_size": {
    "small": 178,   # 73%
    "medium": 52,   # 21%
    "large": 15     # 6%
  },
  "avg_profile_completeness": 67.3,
  "with_irrigation": 45,          # 18%
  "with_machinery": 23,           # 9%
  "with_credit_access": 67,       # 27%
  "farmer_group_members": 123     # 50%
}
```

---

## 🚀 Next Steps

1. **Integrate with RAG Agent**: Add profile context to queries
2. **Add API Endpoints**: Expose profile management via REST API
3. **Build Frontend**: Create profile registration form
4. **Analytics Dashboard**: Visualize farmer demographics
5. **Program Matching**: Auto-suggest relevant programs
6. **Impact Tracking**: Measure outcomes by segment

---

## 🧪 Testing

```bash
# Test the profile system
source venv/bin/activate
python src/user/farmer_profile.py

# Expected output:
# Profile Summary: Youth farmer (female) with small farm (3.5ha) in Mashonaland East growing maize, beans, vegetables
# Profile Completeness: 75.0%
# Personalized Context: [context string]
# Available Programs:
# Training: 10 programs
# Financing: 6 programs
# Support: 6 programs
```

---

**Implementation Status**: ✅ Complete

**Lines of Code**: ~665 LOC

**Files Created**: 1 new module

**Testing**: Fully tested with sample profiles

**Documentation**: Complete with examples
