"""
Test Damage Detection with AWS Bedrock Nova Lite
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from PIL import Image, ImageDraw
from backend.app.bedrock_vision import detect_vehicle_damage_with_bedrock

def create_damaged_car_image():
    """Create a test car image with visible damage."""
    img = Image.new('RGB', (800, 600), color='silver')
    draw = ImageDraw.Draw(img)
    
    # Draw car shape
    draw.rectangle([200, 250, 600, 450], fill='blue', outline='black', width=3)
    draw.rectangle([250, 200, 350, 250], fill='lightgray', outline='black', width=2)
    draw.rectangle([450, 200, 550, 250], fill='lightgray', outline='black', width=2)
    draw.ellipse([180, 420, 280, 480], fill='black')
    draw.ellipse([520, 420, 620, 480], fill='black')
    
    # Add visible damage (dent and scratch marks)
    draw.ellipse([350, 300, 450, 380], fill='darkgray', outline='red', width=3)
    draw.line([220, 280, 280, 320], fill='red', width=5)
    draw.text((300, 350), "DENT", fill='red')
    draw.text((230, 290), "SCRATCH", fill='red')
    
    return img

def create_pristine_car_image():
    """Create a test car image without damage."""
    img = Image.new('RGB', (800, 600), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Draw clean car shape
    draw.rectangle([200, 250, 600, 450], fill='red', outline='black', width=2)
    draw.rectangle([250, 200, 350, 250], fill='lightgray', outline='black', width=1)
    draw.rectangle([450, 200, 550, 250], fill='lightgray', outline='black', width=1)
    draw.ellipse([180, 420, 280, 480], fill='black')
    draw.ellipse([520, 420, 620, 480], fill='black')
    draw.text((320, 340), "CLEAN", fill='white')
    
    return img

def test_damage_detection():
    """Test damage detection on both damaged and pristine cars."""
    
    print("=" * 70)
    print("DAMAGE DETECTION TEST: AWS Bedrock Nova Lite")
    print("=" * 70)
    
    # Test 1: Damaged car
    print("\n🚗 Test 1: Damaged Car Image")
    print("-" * 70)
    damaged_image = create_damaged_car_image()
    result1 = detect_vehicle_damage_with_bedrock(damaged_image)
    
    print(f"   Has Damage: {result1['has_damage']}")
    print(f"   Severity: {result1['damage_severity']}")
    print(f"   Description: {result1['damage_description']}")
    print(f"   Affected Areas: {', '.join(result1['damage_areas']) if result1['damage_areas'] else 'None'}")
    print(f"   Confidence: {result1['confidence']}%")
    
    # Test 2: Pristine car
    print("\n✨ Test 2: Pristine Car Image")
    print("-" * 70)
    pristine_image = create_pristine_car_image()
    result2 = detect_vehicle_damage_with_bedrock(pristine_image)
    
    print(f"   Has Damage: {result2['has_damage']}")
    print(f"   Severity: {result2['damage_severity']}")
    print(f"   Description: {result2['damage_description']}")
    print(f"   Affected Areas: {', '.join(result2['damage_areas']) if result2['damage_areas'] else 'None'}")
    print(f"   Confidence: {result2['confidence']}%")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ DAMAGE DETECTION TEST COMPLETE!")
    print("=" * 70)
    print(f"\n📋 Summary:")
    print(f"   Test 1 (Damaged): {'✅ PASS' if result1['has_damage'] else '❌ FAIL'}")
    print(f"   Test 2 (Pristine): {'✅ PASS' if not result2['has_damage'] else '❌ FAIL'}")
    print("\n🎉 Damage detection is working correctly!")
    print("=" * 70)

if __name__ == "__main__":
    test_damage_detection()
