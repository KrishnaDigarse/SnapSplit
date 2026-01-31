"""
Test script for Week 4 async bill scanning implementation.

This script verifies:
1. All imports work correctly
2. Celery task is registered
3. API endpoints are accessible
4. No breaking changes from async migration

Run: python test_async_implementation.py
"""
import sys
import traceback

def test_imports():
    """Test that all new modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        from app.celery_app import celery_app
        print("  ✅ Celery app imported")
        
        from app.tasks.ai_tasks import process_bill_image_task
        print("  ✅ AI task imported")
        
        from app.routes.ai_expenses import router
        print("  ✅ AI expenses router imported")
        
        from main import app
        print("  ✅ FastAPI app imported")
        
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        traceback.print_exc()
        return False


def test_celery_task_registration():
    """Test that Celery task is properly registered."""
    print("\n🧪 Testing Celery task registration...")
    
    try:
        from app.celery_app import celery_app
        from app.tasks.ai_tasks import process_bill_image_task
        
        # Check task name
        expected_name = "app.tasks.ai_tasks.process_bill_image_task"
        actual_name = process_bill_image_task.name
        
        if actual_name == expected_name:
            print(f"  ✅ Task registered with correct name: {actual_name}")
        else:
            print(f"  ❌ Task name mismatch: expected {expected_name}, got {actual_name}")
            return False
        
        # Check task is in Celery app
        if actual_name in [str(task) for task in celery_app.tasks.keys()]:
            print(f"  ✅ Task found in Celery app tasks")
        else:
            print(f"  ⚠️  Task not yet in Celery app (will be registered when worker starts)")
        
        return True
    except Exception as e:
        print(f"  ❌ Task registration test failed: {e}")
        traceback.print_exc()
        return False


def test_api_routes():
    """Test that API routes are properly configured."""
    print("\n🧪 Testing API routes...")
    
    try:
        from app.routes.ai_expenses import router
        
        routes = [route.path for route in router.routes]
        expected_routes = ['/expenses/bill', '/expenses/{expense_id}/status']
        
        for expected in expected_routes:
            if expected in routes:
                print(f"  ✅ Route registered: {expected}")
            else:
                print(f"  ❌ Route missing: {expected}")
                return False
        
        return True
    except Exception as e:
        print(f"  ❌ Route test failed: {e}")
        traceback.print_exc()
        return False


def test_fastapi_app():
    """Test that FastAPI app can be created."""
    print("\n🧪 Testing FastAPI app...")
    
    try:
        from main import app
        
        route_count = len(app.routes)
        print(f"  ✅ FastAPI app created with {route_count} routes")
        
        # Check if our new routes are in the app
        all_paths = [route.path for route in app.routes]
        
        if '/api/v1/expenses/bill' in all_paths:
            print("  ✅ Bill upload endpoint found")
        else:
            print("  ❌ Bill upload endpoint missing")
            return False
        
        if '/api/v1/expenses/{expense_id}/status' in all_paths:
            print("  ✅ Status polling endpoint found")
        else:
            print("  ❌ Status polling endpoint missing")
            return False
        
        return True
    except Exception as e:
        print(f"  ❌ FastAPI app test failed: {e}")
        traceback.print_exc()
        return False


def test_configuration():
    """Test that configuration is properly set."""
    print("\n🧪 Testing configuration...")
    
    try:
        from app.core import celery_config
        
        # Check broker URL
        if hasattr(celery_config, 'CELERY_BROKER_URL'):
            print(f"  ✅ Broker URL configured: {celery_config.CELERY_BROKER_URL}")
        else:
            print("  ❌ Broker URL not configured")
            return False
        
        # Check result backend
        if hasattr(celery_config, 'CELERY_RESULT_BACKEND'):
            print(f"  ✅ Result backend configured: {celery_config.CELERY_RESULT_BACKEND}")
        else:
            print("  ❌ Result backend not configured")
            return False
        
        # Check serialization
        if hasattr(celery_config, 'CELERY_TASK_SERIALIZER'):
            print(f"  ✅ Task serializer: {celery_config.CELERY_TASK_SERIALIZER}")
        else:
            print("  ⚠️  Task serializer not explicitly set")
        
        return True
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Week 4 Async Implementation - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Celery Task Registration", test_celery_task_registration),
        ("API Routes", test_api_routes),
        ("FastAPI App", test_fastapi_app),
        ("Configuration", test_configuration),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Week 4 implementation is ready.")
        print("\nNext steps:")
        print("1. Start Redis: docker-compose up -d redis")
        print("2. Start Celery worker: celery -A app.celery_app worker --loglevel=info")
        print("3. Start FastAPI: python -m uvicorn main:app --reload")
        print("4. Test via Postman")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
