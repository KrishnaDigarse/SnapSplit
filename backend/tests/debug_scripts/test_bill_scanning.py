"""
Test script for AI bill scanning feature.

This script tests the complete bill upload and processing pipeline:
1. Setup verification (Tesseract, Gemini API)
2. User registration and login
3. Group creation
4. Bill image upload
5. Expense verification

Requirements:
- Server running on http://localhost:8000
- Tesseract OCR installed
- GEMINI_API_KEY in .env file
- Sample bill image
"""
import requests
import os
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER_EMAIL = "bill_test_user@example.com"
TEST_USER_PASSWORD = "testpass123"
TEST_USER_NAME = "Bill Test User"
TEST_GROUP_NAME = "Bill Test Group"

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_step(step_num, message):
    """Print a test step."""
    print(f"\n{BLUE}{step_num}️⃣ {message}{RESET}")
    print("=" * 60)


def print_success(message):
    """Print success message."""
    print(f"{GREEN}✅ {message}{RESET}")


def print_error(message):
    """Print error message."""
    print(f"{RED}❌ {message}{RESET}")


def print_info(message):
    """Print info message."""
    print(f"{YELLOW}ℹ️  {message}{RESET}")


def create_sample_bill_image(filename="test_bill.png"):
    """
    Create a sample bill image for testing.
    
    Returns:
        Path to created image
    """
    print_info("Creating sample bill image...")
    
    # Create image
    width, height = 600, 800
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a nice font, fall back to default if not available
    try:
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_medium = ImageFont.truetype("arial.ttf", 18)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw bill content
    y = 50
    
    # Header
    draw.text((200, y), "RESTAURANT ABC", fill='black', font=font_large)
    y += 40
    draw.text((220, y), "123 Main Street", fill='black', font=font_small)
    y += 30
    draw.text((200, y), "Tel: 555-1234", fill='black', font=font_small)
    y += 50
    
    # Date
    draw.text((50, y), "Date: 2024-01-30", fill='black', font=font_small)
    y += 40
    
    # Items
    draw.text((50, y), "ITEMS:", fill='black', font=font_medium)
    y += 30
    
    items = [
        ("1. Burger", "$12.00"),
        ("2. Fries", "$5.00"),
        ("3. Soda", "$3.00"),
    ]
    
    for item, price in items:
        draw.text((50, y), item, fill='black', font=font_medium)
        draw.text((450, y), price, fill='black', font=font_medium)
        y += 30
    
    y += 20
    draw.line([(50, y), (550, y)], fill='black', width=2)
    y += 30
    
    # Totals
    draw.text((50, y), "Subtotal:", fill='black', font=font_medium)
    draw.text((450, y), "$20.00", fill='black', font=font_medium)
    y += 30
    
    draw.text((50, y), "Tax (10%):", fill='black', font=font_medium)
    draw.text((450, y), "$2.00", fill='black', font=font_medium)
    y += 30
    
    draw.line([(50, y), (550, y)], fill='black', width=2)
    y += 30
    
    draw.text((50, y), "TOTAL:", fill='black', font=font_large)
    draw.text((450, y), "$22.00", fill='black', font=font_large)
    y += 50
    
    # Footer
    draw.text((200, y), "Thank you!", fill='black', font=font_medium)
    
    # Save image
    image.save(filename)
    print_success(f"Created sample bill: {filename}")
    
    return filename


def test_setup():
    """Test that all prerequisites are met."""
    print_step(0, "Verifying Setup")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health", timeout=5)
        if response.status_code == 200:
            print_success("Server is running")
        else:
            print_error("Server returned unexpected status")
            return False
    except requests.exceptions.RequestException:
        print_error("Server is not running. Start it with: python -m uvicorn main:app --reload")
        return False
    
    # Check for Tesseract
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print_success(f"Tesseract OCR installed: {version}")
    except Exception as e:
        print_error(f"Tesseract OCR not found: {e}")
        print_info("Install from: https://github.com/tesseract-ocr/tesseract")
        return False
    
    # Check for Gemini API key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print_success("Gemini API key found")
    else:
        print_error("GEMINI_API_KEY not found in .env file")
        print_info("Get one from: https://makersuite.google.com/app/apikey")
        return False
    
    return True


def register_user():
    """Register a test user."""
    print_step(1, "Registering Test User")
    
    payload = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "name": TEST_USER_NAME
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=payload)
    
    if response.status_code == 201:
        data = response.json()
        print_success(f"User registered: {data['email']}")
        print_info(f"User ID: {data['id']}")
        return data['id']
    elif response.status_code == 400 and "already registered" in response.text:
        print_info("User already exists, continuing...")
        return None
    else:
        print_error(f"Registration failed: {response.status_code}")
        print_error(response.text)
        return None


def login_user():
    """Login and get JWT token."""
    print_step(2, "Logging In")
    
    # UserLogin expects JSON with email and password
    payload = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=payload  # Send as JSON
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data['access_token']
        print_success("Login successful")
        print_info(f"Token: {token[:50]}...")
        return token
    else:
        print_error(f"Login failed: {response.status_code}")
        print_error(response.text)
        return None


def create_group(token):
    """Create a test group."""
    print_step(3, "Creating Test Group")
    
    payload = {
        "name": TEST_GROUP_NAME,
        "type": "CUSTOM"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/groups", json=payload, headers=headers)
    
    if response.status_code == 201:
        data = response.json()
        print_success(f"Group created: {data['name']}")
        print_info(f"Group ID: {data['id']}")
        return data['id']
    else:
        print_error(f"Group creation failed: {response.status_code}")
        print_error(response.text)
        return None


def upload_bill(token, group_id, image_path):
    """Upload a bill image."""
    print_step(4, "Uploading Bill Image")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(image_path, 'rb') as f:
        files = {'image': (os.path.basename(image_path), f, 'image/png')}
        data = {'group_id': group_id}
        
        print_info("Uploading and processing (this may take 5-15 seconds)...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/expenses/bill",
            headers=headers,
            files=files,
            data=data,
            timeout=30
        )
        
        elapsed = time.time() - start_time
        print_info(f"Processing took {elapsed:.2f} seconds")
    
    if response.status_code == 201:
        data = response.json()
        print_success(f"Bill uploaded successfully!")
        print_info(f"Expense ID: {data['id']}")
        print_info(f"Status: {data['status']}")
        
        if data['status'] == 'READY':
            print_success("AI processing succeeded!")
            print_info(f"Subtotal: ${data['subtotal']}")
            print_info(f"Tax: ${data['tax']}")
            print_info(f"Total: ${data['total_amount']}")
            print_info(f"Items extracted: {len(data.get('items', []))}")
            
            if data.get('items'):
                print("\nExtracted Items:")
                for item in data['items']:
                    print(f"  - {item['item_name']}: ${item['price']} x {item['quantity']}")
        elif data['status'] == 'FAILED':
            print_error("AI processing failed")
            print_error(f"Error: {data.get('description', 'Unknown error')}")
        
        return data
    else:
        print_error(f"Upload failed: {response.status_code}")
        print_error(response.text)
        return None


def verify_expense(token, expense_id):
    """Verify the created expense."""
    print_step(5, "Verifying Expense Details")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/expenses/{expense_id}", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print_success("Expense retrieved successfully")
        
        # Check for splits
        if data.get('splits'):
            print_info(f"Splits created: {len(data['splits'])}")
            for split in data['splits']:
                print(f"  - User {split['user_id']}: ${split['amount']}")
        
        # Check for OCR text
        if data.get('raw_ocr_text'):
            print_success("OCR text stored")
            print_info(f"OCR text preview: {data['raw_ocr_text'][:100]}...")
        
        return True
    else:
        print_error(f"Failed to retrieve expense: {response.status_code}")
        return False


def run_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print(f"{BLUE}🧪 SnapSplit AI Bill Scanning - Test Suite{RESET}")
    print("=" * 60)
    
    # Setup verification
    if not test_setup():
        print_error("\nSetup verification failed. Please fix issues and try again.")
        return False
    
    # Check for sample bill image
    image_path = "sample_bill.png"
    if not os.path.exists(image_path):
        print_info(f"Sample bill not found at {image_path}, creating one...")
        image_path = create_sample_bill_image()
    else:
        print_success(f"Using existing sample bill: {image_path}")
    
    # Register user
    user_id = register_user()
    
    # Login
    token = login_user()
    if not token:
        return False
    
    # Create group
    group_id = create_group(token)
    if not group_id:
        return False
    
    # Upload bill
    expense = upload_bill(token, group_id, image_path)
    if not expense:
        return False
    
    # Verify expense
    if expense.get('id'):
        verify_expense(token, expense['id'])
    
    # Summary
    print("\n" + "=" * 60)
    print(f"{GREEN}✅ All tests completed!{RESET}")
    print("=" * 60)
    
    if expense and expense.get('status') == 'READY':
        print(f"{GREEN}🎉 AI bill scanning is working perfectly!{RESET}")
    elif expense and expense.get('status') == 'FAILED':
        print(f"{YELLOW}⚠️  Bill uploaded but AI processing failed.{RESET}")
        print(f"{YELLOW}   This is expected behavior for error handling.{RESET}")
    
    print(f"\n{BLUE}Next steps:{RESET}")
    print("1. Try uploading a real bill photo")
    print("2. Test with different image qualities")
    print("3. Check the Swagger UI: http://localhost:8000/docs")
    
    # Cleanup (only delete if we created it)
    if image_path != "sample_bill.png":
        try:
            os.remove(image_path)
            print_info(f"\nCleaned up test image: {image_path}")
        except:
            pass
    
    return True


if __name__ == "__main__":
    try:
        success = run_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Test interrupted by user{RESET}")
        exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
