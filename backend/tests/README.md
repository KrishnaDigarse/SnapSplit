# SnapSplit Backend Tests

This directory contains test scripts and sample images for the AI bill scanning system.

## Directory Structure

```
tests/
├── debug_scripts/          # Debug and testing scripts
│   ├── batch_test_bills.py      # Batch process multiple bill images
│   ├── debug_llm.py             # Test LLM extraction
│   ├── debug_ocr.py             # Test OCR extraction
│   ├── debug_sample_bill.py     # Debug specific bill
│   ├── test_ai_pipeline_debug.py # Test complete pipeline
│   ├── test_bill_scanning.py    # End-to-end test
│   ├── test_complete_pipeline.py # Pipeline test
│   └── test_ocr_strategies.py   # Compare OCR strategies
│
└── sample_images/          # Sample bill images for testing
    ├── *.jpg, *.png             # Test bill images
    └── *_results.txt            # Test results
```

## Running Tests

### Batch Test All Images
```bash
cd tests/debug_scripts
python batch_test_bills.py
```

### Test Complete Pipeline
```bash
cd tests/debug_scripts
python test_ai_pipeline_debug.py
```

### End-to-End Test
```bash
cd tests/debug_scripts
python test_bill_scanning.py
```

## Adding New Test Images

1. Add bill images to `tests/sample_images/`
2. Run `batch_test_bills.py` to process all images
3. Check `*_results.txt` files for extraction results

## Test Results

Current success rate: **100%** (5/5 images)

All test images successfully processed with:
- OCR text extraction
- LLM data parsing
- Validation and cleaning
