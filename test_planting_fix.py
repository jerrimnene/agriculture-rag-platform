#!/usr/bin/env python3
"""
Test script to verify the maize planting window fix.
Tests that Chimanimani queries no longer suggest year-round planting.
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_chimanimani_maize_planting():
    """Test maize planting query for Chimanimani District."""
    print("=" * 60)
    print("Testing Maize Planting Query for Chimanimani District")
    print("=" * 60)
    
    query = {
        "query": "When should I plant maize in Chimanimani District?",
        "district": "Chimanimani"
    }
    
    print(f"\nQuery: {query['query']}")
    print(f"District: {query['district']}")
    print("\nSending request to API...")
    
    response = requests.post(f"{API_URL}/query", json=query)
    
    if response.status_code == 200:
        result = response.json()
        
        print("\n" + "=" * 60)
        print("RESPONSE FROM AgriEvidence:")
        print("=" * 60)
        print(result.get('response', 'No response'))
        
        print("\n" + "=" * 60)
        print("VERIFICATION:")
        print("=" * 60)
        
        response_text = result.get('response', '').lower()
        
        # Check for problematic phrases
        issues = []
        if 'year-round' in response_text or 'year round' in response_text:
            # Check if it's in context of clarification (e.g., "perennial crops year-round")
            if 'perennial' in response_text:
                print("✅ PASS: 'Year-round' mentioned only in context of perennial crops")
            else:
                issues.append("❌ FAIL: Response suggests year-round planting for annual crops")
        else:
            print("✅ PASS: No mention of 'year-round' planting")
        
        # Check for correct information
        if 'november' in response_text or 'december' in response_text:
            print("✅ PASS: Mentions November-December planting window")
        else:
            issues.append("❌ FAIL: Does not mention Nov-Dec planting window")
        
        if 'rainy season' in response_text or 'rainfall' in response_text:
            print("✅ PASS: References rainy season/rainfall patterns")
        else:
            print("⚠️  WARNING: No explicit mention of rainy season")
        
        # Check geo context
        geo_context = result.get('geo_context', {})
        if geo_context:
            print(f"\n✅ Geo Context Applied:")
            print(f"   District: {geo_context.get('district')}")
            print(f"   Region: {geo_context.get('region')}")
            print(f"   Rainfall: {geo_context.get('rainfall')}")
            if 'maize_planting_window' in geo_context:
                print(f"   Maize Planting Window: {geo_context['maize_planting_window']}")
            else:
                issues.append("❌ FAIL: maize_planting_window not in geo_context")
        else:
            issues.append("❌ FAIL: No geo_context in response")
        
        print("\n" + "=" * 60)
        if issues:
            print("TEST RESULT: FAILED ❌")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("TEST RESULT: PASSED ✅")
            print("System is now providing accurate maize planting guidance!")
        print("=" * 60)
        
    else:
        print(f"\n❌ ERROR: API request failed with status code {response.status_code}")
        print(response.text)

def test_geo_context_directly():
    """Test the geo context module directly."""
    print("\n\n" + "=" * 60)
    print("Testing Geo Context Module Directly")
    print("=" * 60)
    
    from src.geo.geo_context import GeoContext
    
    geo = GeoContext()
    district_info = geo.get_district_by_name('Chimanimani')
    
    if district_info:
        context = geo.format_context(district_info)
        
        print(f"\nDistrict: {context['district']}")
        print(f"Region: {context['region']}")
        print(f"Rainfall: {context['rainfall']}")
        print(f"Growing Season: {context.get('growing_season', 'N/A')}")
        
        if 'maize_planting_window' in context:
            print(f"Maize Planting Window: {context['maize_planting_window']}")
            print("\n✅ PASS: maize_planting_window is present in context")
        else:
            print("\n❌ FAIL: maize_planting_window is missing from context")
        
        # Check that growing season clarifies perennial crops
        growing_season = context.get('growing_season', '')
        if 'perennial' in growing_season.lower():
            print("✅ PASS: Growing season clarifies perennial crops")
        else:
            print("⚠️  WARNING: Growing season doesn't mention perennial crops")
    else:
        print("❌ ERROR: Could not find Chimanimani district")

if __name__ == "__main__":
    try:
        # Test direct geo context
        test_geo_context_directly()
        
        # Test full API
        test_chimanimani_maize_planting()
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API at", API_URL)
        print("Please ensure the API is running with: python3 -m src.api.main")
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
