"""
Batch test script for AI bill scanning.

Processes all images in test_images/ folder and saves results to text files.
Each result file contains:
1. Raw OCR text
2. LLM extracted JSON
3. Validation results
"""
import sys
import os
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

from app.ai.ocr import extract_text_from_image
from app.ai.llm import extract_bill_data
from app.ai.parser import validate_bill_data


def process_image(image_path: Path, output_dir: Path) -> dict:
    """
    Process a single bill image through the complete AI pipeline.
    
    Args:
        image_path: Path to bill image
        output_dir: Directory to save results
        
    Returns:
        Dictionary with processing results
    """
    result = {
        'image': image_path.name,
        'success': False,
        'ocr_text': None,
        'llm_output': None,
        'validated_data': None,
        'error': None
    }
    
    print(f"\n{'='*60}")
    print(f"Processing: {image_path.name}")
    print(f"{'='*60}")
    
    # Step 1: OCR
    print("1️⃣ Running OCR...")
    try:
        ocr_text = extract_text_from_image(str(image_path))
        result['ocr_text'] = ocr_text
        print(f"✅ OCR Success: {len(ocr_text)} characters")
    except Exception as e:
        result['error'] = f"OCR failed: {str(e)}"
        print(f"❌ OCR Failed: {e}")
        return result
    
    # Step 2: LLM
    print("2️⃣ Running LLM...")
    try:
        llm_output = extract_bill_data(ocr_text)
        result['llm_output'] = llm_output
        print(f"✅ LLM Success: {len(llm_output.get('items', []))} items extracted")
    except Exception as e:
        result['error'] = f"LLM failed: {str(e)}"
        print(f"❌ LLM Failed: {e}")
        return result
    
    # Step 3: Validation
    print("3️⃣ Running Validation...")
    try:
        validated_data = validate_bill_data(llm_output)
        result['validated_data'] = validated_data
        result['success'] = True
        print(f"✅ Validation Success: {len(validated_data['items'])} valid items")
    except Exception as e:
        result['error'] = f"Validation failed: {str(e)}"
        print(f"❌ Validation Failed: {e}")
        return result
    
    # Save results to file
    output_file = output_dir / f"{image_path.stem}_results.txt"
    save_results(result, output_file)
    print(f"💾 Results saved to: {output_file.name}")
    
    return result


def save_results(result: dict, output_path: Path):
    """
    Save processing results to a text file.
    
    Args:
        result: Processing result dictionary
        output_path: Path to save results
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write(f"AI BILL SCANNING TEST RESULTS\n")
        f.write(f"Image: {result['image']}\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Status: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}\n")
        f.write("="*60 + "\n\n")
        
        # OCR Text
        f.write("📄 RAW OCR TEXT\n")
        f.write("-"*60 + "\n")
        if result['ocr_text']:
            f.write(result['ocr_text'])
            f.write(f"\n\nLength: {len(result['ocr_text'])} characters\n")
        else:
            f.write("(No OCR text extracted)\n")
        f.write("\n\n")
        
        # LLM Output
        f.write("🤖 LLM EXTRACTED DATA\n")
        f.write("-"*60 + "\n")
        if result['llm_output']:
            # Convert any Decimal values to strings for JSON serialization
            llm_json = {
                'items': [
                    {
                        'name': item.get('name', ''),
                        'quantity': int(item.get('quantity', 1)),
                        'price': float(item.get('price', 0))
                    }
                    for item in result['llm_output'].get('items', [])
                ],
                'subtotal': float(result['llm_output'].get('subtotal', 0)),
                'tax': float(result['llm_output'].get('tax', 0)),
                'total': float(result['llm_output'].get('total', 0))
            }
            f.write(json.dumps(llm_json, indent=2))
            f.write(f"\n\nItems: {len(result['llm_output'].get('items', []))}\n")
        else:
            f.write("(No LLM output)\n")
        f.write("\n\n")
        
        # Validated Data
        f.write("✅ VALIDATED & CLEANED DATA\n")
        f.write("-"*60 + "\n")
        if result['validated_data']:
            # Convert Decimals to strings for JSON serialization
            validated_json = {
                'items': [
                    {
                        'name': item['name'],
                        'quantity': item['quantity'],
                        'price': str(item['price'])
                    }
                    for item in result['validated_data']['items']
                ],
                'subtotal': str(result['validated_data']['subtotal']),
                'tax': str(result['validated_data']['tax']),
                'total': str(result['validated_data']['total'])
            }
            f.write(json.dumps(validated_json, indent=2))
            f.write(f"\n\nValid Items: {len(result['validated_data']['items'])}\n")
            f.write(f"Total Amount: {result['validated_data']['total']}\n")
        else:
            f.write("(No validated data)\n")
        f.write("\n\n")
        
        # Error (if any)
        if result['error']:
            f.write("❌ ERROR\n")
            f.write("-"*60 + "\n")
            f.write(result['error'])
            f.write("\n\n")
        
        f.write("="*60 + "\n")


def main():
    """
    Main function to process all images in test_images folder.
    """
    # Setup paths
    test_dir = Path('test_images')
    
    if not test_dir.exists():
        print(f"❌ Error: {test_dir} folder not found!")
        print(f"Please create the folder and add bill images to test.")
        return
    
    # Find all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
    image_files = [
        f for f in test_dir.iterdir()
        if f.is_file() and f.suffix in image_extensions
    ]
    
    if not image_files:
        print(f"❌ No images found in {test_dir}/")
        print(f"Supported formats: JPG, JPEG, PNG")
        return
    
    print("="*60)
    print("🧪 BATCH AI BILL SCANNING TEST")
    print("="*60)
    print(f"Found {len(image_files)} images to process")
    print(f"Results will be saved to: {test_dir}/")
    print()
    
    # Process each image
    results = []
    for image_path in sorted(image_files):
        result = process_image(image_path, test_dir)
        results.append(result)
    
    # Summary
    print("\n" + "="*60)
    print("📊 BATCH TEST SUMMARY")
    print("="*60)
    
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    print(f"Total Images: {len(results)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print()
    
    # Detailed results
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['image']}")
        if result['success'] and result['validated_data']:
            print(f"   Items: {len(result['validated_data']['items'])}, "
                  f"Total: {result['validated_data']['total']}")
        elif result['error']:
            print(f"   Error: {result['error']}")
    
    print("\n" + "="*60)
    print(f"✅ All results saved to {test_dir}/*_results.txt")
    print("="*60)


if __name__ == "__main__":
    main()
