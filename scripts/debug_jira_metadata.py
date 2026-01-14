import asyncio
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.jira_service import jira_service

def debug_metadata():
    print("Debugging Jira Metadata...")
    
    if not jira_service.available:
        print("Jira Service Unavailable.")
        return

    try:
        # List all accessible projects
        print("Listing all accessible projects...")
        projects = jira_service.client.projects()
        
        if not projects:
            print("No projects found. Check permissions or user account.")
        
        for p in projects:
            print(f"FOUND PROJECT: {p.key} - {p.name} (ID: {p.id})")
            
            # If we find DEV, try to peek at meta
            if p.key == os.getenv("JIRA_PROJECT_KEY", "DEV"):
                print(f"   -> Verifying Metadata for {p.key}...")
                try:
                    meta = jira_service.client.createmeta(projectKeys=p.key, expand='projects.issuetypes.fields')
                    if meta['projects']:
                        imp = meta['projects'][0]
                        print(f"      Valid Issue Types: {[it['name'] for it in imp['issuetypes']]}")
                except Exception as meta_e:
                    print(f"      Could not fetch metadata: {meta_e}")

    except Exception as e:
        print(f"Error checking projects: {str(e)}")

if __name__ == "__main__":
    debug_metadata()
