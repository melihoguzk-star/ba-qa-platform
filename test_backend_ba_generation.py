"""
Test BA generation directly via backend API
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_ba_generation():
    print("\n" + "="*80)
    print("TESTING BA GENERATION VIA BACKEND API")
    print("="*80)

    # Step 1: Get projects
    print("\n[1/6] Getting projects...")
    projects = requests.get(f"{BASE_URL}/projects").json()
    if not projects:
        print("✗ No projects found, creating one...")
        project = requests.post(f"{BASE_URL}/projects", json={
            "name": "Backend Test Project",
            "description": "Test project"
        }).json()
        project_id = project["id"]
        project_name = project["name"]
    else:
        project_id = projects[0]["id"]
        project_name = projects[0]["name"]

    print(f"✓ Using project: {project_name} (ID={project_id})")

    # Step 2: Start pipeline
    print("\n[2/6] Starting pipeline...")
    start_response = requests.post(f"{BASE_URL}/pipeline/start", json={
        "project_id": project_id,
        "project_name": project_name,
        "brd_content": "# Test BRD\n\nLogin ve Dashboard ekranları",
        "stages": ["ba", "ta", "tc"]
    })

    try:
        start_response.raise_for_status()
        run_id = start_response.json()["pipeline_run_id"]
        print(f"✓ Pipeline started: run_id={run_id}")
    except Exception as e:
        print(f"✗ Pipeline start failed: {e}")
        print(f"  Response: {start_response.text}")
        return

    # Step 3: Check initial status
    print("\n[3/6] Checking initial status...")
    status = requests.get(f"{BASE_URL}/pipeline/{run_id}/status").json()
    print(f"  Current stage: {status['current_stage']}")
    print(f"  Status: {status['status']}")

    # Step 4: Execute BA generation
    print("\n[4/6] Executing BA generation...")
    try:
        execute_response = requests.post(
            f"{BASE_URL}/pipeline/{run_id}/execute-stage",
            params={"stage": "ba_gen"}
        )
        execute_response.raise_for_status()
        print(f"✓ BA generation started: {execute_response.json()}")
    except Exception as e:
        print(f"✗ BA generation failed: {e}")
        print(f"  Response: {execute_response.text if execute_response else 'No response'}")
        return

    # Step 5: Poll status until complete
    print("\n[5/6] Polling status (max 60 seconds)...")
    max_attempts = 30
    for i in range(max_attempts):
        time.sleep(2)
        status = requests.get(f"{BASE_URL}/pipeline/{run_id}/status").json()

        print(f"  [{i+1}/{max_attempts}] Stage: {status['current_stage']}, Status: {status['status']}")

        if status['status'] == 'waiting_approval' and status['current_stage'] == 'ba_review':
            print("✓ BA generation completed!")
            break
        elif status['status'] == 'failed':
            print(f"✗ Pipeline failed: {status.get('error', 'Unknown error')}")
            return
    else:
        print("✗ Timeout waiting for BA generation")
        return

    # Step 6: Get checkpoint data
    print("\n[6/6] Getting BA checkpoint data...")
    checkpoint = requests.get(f"{BASE_URL}/pipeline/{run_id}/checkpoint/ba_gen").json()

    if checkpoint:
        print(f"✓ Checkpoint retrieved")
        print(f"  Keys: {list(checkpoint.keys())}")
        if 'ekranlar' in checkpoint:
            print(f"  Screens: {len(checkpoint['ekranlar'])}")
            for i, screen in enumerate(checkpoint['ekranlar'][:2], 1):
                print(f"    {i}. {screen.get('ekran_adi', 'N/A')}")
        else:
            print(f"  ⚠ No 'ekranlar' key in checkpoint")
            print(f"  Checkpoint content: {json.dumps(checkpoint, indent=2)[:500]}")
    else:
        print("✗ No checkpoint data found")

    print("\n" + "="*80)
    print("✅ BA GENERATION TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_ba_generation()
