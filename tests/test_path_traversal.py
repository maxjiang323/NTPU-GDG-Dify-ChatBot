
import os
import sys
import django
from django.conf import settings
from django.test import RequestFactory
from django.views.static import serve
from django.http import Http404

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

def test_path_traversal():
    print("Testing Path Traversal vulnerability in django.views.static.serve...")
    
    # Mock request
    factory = RequestFactory()
    
    # Define the document root as used in config/urls.py
    document_root = os.path.join(settings.BASE_DIR, 'frontend/Dify-ChatBot-V2/dist')
    
    # Ensure document root exists for the test (create a dummy file if needed)
    if not os.path.exists(document_root):
        print(f"Directory {document_root} does not exist. Creating path for test.")
        os.makedirs(document_root, exist_ok=True)
    
    # Create a sensitive file outside document root to try to access
    secret_file = os.path.join(settings.BASE_DIR, 'secret.txt')
    with open(secret_file, 'w') as f:
        f.write("SECRET_CONTENT")
        
    try:
        # payload = "../../../secret.txt" 
        # But wait, urls.py regex enforces prefix:
        # re_path(r'^(?P<path>(lovable-uploads|favicon\.ico|robots\.txt|placeholder\.svg).*)$', serve, ...)
        
        # So we must start with one of those, e.g., "lovable-uploads/../../../secret.txt"
        
        # Create 'lovable-uploads' dir to pass the initial check if serve does file existence check early? 
        # Actually serve checks the final path.
        
        payload = "lovable-uploads/../../../secret.txt"
        
        print(f"Attempting to access: {payload}")
        print(f"Document root: {document_root}")
        
        request = factory.get(f"/{payload}")
        
        try:
            response = serve(request, path=payload, document_root=document_root)
            
            if response.status_code == 200:
                content = b"".join(response.streaming_content) if response.streaming_content else response.content
                if b"SECRET_CONTENT" in content:
                    print("VULNERABLE: Successfully read secret file!")
                else:
                    print(f"Response 200 but content not matched. Content len: {len(content)}")
            else:
                print(f"Safe: Response code {response.status_code}")
                
        except Http404:
            print("Safe: Http404 raised (Django blocked the traversal or file not found)")
        except Exception as e:
            print(f"Safe: Exception raised: {type(e).__name__}: {e}")

    finally:
        # Cleanup
        if os.path.exists(secret_file):
            os.remove(secret_file)
            print("Cleaned up secret file.")

if __name__ == "__main__":
    test_path_traversal()
