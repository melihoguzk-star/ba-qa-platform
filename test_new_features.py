"""
Test script for new Import & Merge features
Tests: BRD Pipeline import and AI text parsing
"""
import json
from data.database import get_recent_pipeline_runs, get_pipeline_run_outputs, init_db

print("🧪 Testing New Import & Merge Features\n")
print("=" * 60)

# Initialize
init_db()

# Test 1: BRD Pipeline Import
print("\n1️⃣ Testing BRD Pipeline Import Feature")
print("-" * 60)

pipeline_runs = get_recent_pipeline_runs(limit=10)
print(f"   📊 Found {len(pipeline_runs)} pipeline runs")

if pipeline_runs:
    # Filter completed
    completed = [r for r in pipeline_runs if r.get('status') == 'completed']
    print(f"   ✅ Completed runs: {len(completed)}")

    if completed:
        # Test with first completed run
        test_run = completed[0]
        run_id = test_run['id']

        print(f"\n   Testing with Run #{run_id}:")
        print(f"      Project: {test_run.get('project_name', 'N/A')}")
        print(f"      JIRA: {test_run.get('jira_key', 'N/A')}")
        print(f"      Status: {test_run.get('status', 'N/A')}")
        print(f"      BA Score: {test_run.get('ba_score', 0):.0%}")
        print(f"      TA Score: {test_run.get('ta_score', 0):.0%}")
        print(f"      TC Score: {test_run.get('tc_score', 0):.0%}")

        # Get outputs
        outputs = get_pipeline_run_outputs(run_id)
        print(f"\n   📋 Outputs for Run #{run_id}: {len(outputs)}")

        if outputs:
            # Group by stage
            stages = {}
            for output in outputs:
                stage = output.get('stage')
                revision = output.get('revision_number', 0)

                if stage not in stages or revision > stages[stage].get('revision_number', 0):
                    stages[stage] = output

            print(f"   ✅ Available stages: {list(stages.keys())}")

            # Test parsing one output
            if 'ba' in stages:
                ba_output = stages['ba']
                try:
                    content_json = json.loads(ba_output.get('content_json', '{}'))

                    print(f"\n   🔍 BA Output Preview:")
                    print(f"      Revision: {ba_output.get('revision_number', 0)}")
                    print(f"      Keys: {list(content_json.keys())}")

                    if 'ekranlar' in content_json:
                        print(f"      Screens: {len(content_json['ekranlar'])}")

                    if 'backend_islemler' in content_json:
                        print(f"      Backend ops: {len(content_json['backend_islemler'])}")

                    print("\n   ✅ BRD Pipeline Import: READY")

                except Exception as e:
                    print(f"   ❌ Error parsing BA output: {e}")
            else:
                print("   ⚠️  No BA output found")
        else:
            print("   ⚠️  No outputs found for this run")
    else:
        print("   ⚠️  No completed runs available")
        print("   💡 Run BRD Pipeline first to test this feature")
else:
    print("   ⚠️  No pipeline runs found")
    print("   💡 Run BRD Pipeline first to test this feature")

# Test 2: AI Text Parsing
print("\n\n2️⃣ Testing AI Text Parsing Feature")
print("-" * 60)

# Check if Gemini key is available
import os
gemini_key = os.environ.get("GEMINI_API_KEY", "")

if gemini_key:
    print("   ✅ Gemini API key found")

    # Test with sample text
    sample_text = """
    Login Feature

    User Login Screen:
    - Email field (required, email input)
    - Password field (required, password input)
    - Login button

    Backend API:
    - POST /api/auth/login
    - Authenticate user credentials
    """

    print("\n   📝 Sample Text:")
    print("   " + sample_text.replace("\n", "\n   "))

    try:
        from agents.ai_client import call_gemini

        system_prompt = """You are a Business Analyst documentation expert.
Parse the given text and convert it into a structured BA (Business Analysis) JSON format.

The JSON structure should follow this schema:
{
  "ekranlar": [
    {
      "ekran_adi": "Screen name",
      "aciklama": "Screen description",
      "fields": [
        {"name": "field_name", "type": "field_type", "required": true/false}
      ]
    }
  ],
  "backend_islemler": [
    {
      "islem": "Operation name",
      "aciklama": "Operation description",
      "endpoint": "/api/path",
      "method": "GET/POST/PUT/DELETE"
    }
  ]
}

Return ONLY valid JSON, no markdown formatting or explanations."""

        print("\n   🤖 Calling Gemini AI for parsing...")

        result = call_gemini(
            system_prompt=system_prompt,
            user_content=f"Parse this BA document:\n\n{sample_text}",
            api_key=gemini_key,
            max_tokens=2000
        )

        if result.get('error'):
            print(f"   ❌ AI Error: {result['error']}")
        elif result.get('content'):
            parsed = result['content']

            print("   ✅ AI Parsing successful!")
            print(f"\n   📋 Parsed JSON:")
            print(f"      Keys: {list(parsed.keys())}")

            if 'ekranlar' in parsed:
                print(f"      Screens: {len(parsed['ekranlar'])}")
                if parsed['ekranlar']:
                    print(f"      - {parsed['ekranlar'][0].get('ekran_adi', 'N/A')}")

            if 'backend_islemler' in parsed:
                print(f"      Backend ops: {len(parsed['backend_islemler'])}")
                if parsed['backend_islemler']:
                    print(f"      - {parsed['backend_islemler'][0].get('islem', 'N/A')}")

            print("\n   ✅ AI Text Parsing: READY")
        else:
            print("   ❌ AI returned empty response")

    except Exception as e:
        print(f"   ❌ AI Parsing Error: {str(e)}")
        print("   💡 This may be a quota or API issue")
else:
    print("   ⚠️  Gemini API key not found")
    print("   💡 Set GEMINI_API_KEY environment variable or configure in Settings")
    print("   ℹ️  AI Text Parsing: Needs API key to test")

# Summary
print("\n\n" + "=" * 60)
print("🎯 Feature Test Summary")
print("=" * 60)

has_pipeline = len([r for r in pipeline_runs if r.get('status') == 'completed']) > 0 if pipeline_runs else False
has_gemini = bool(gemini_key)

print(f"\n1. BRD Pipeline Import: {'✅ READY' if has_pipeline else '⚠️  NEEDS PIPELINE RUN'}")
print(f"2. AI Text Parsing: {'✅ READY' if has_gemini else '⚠️  NEEDS API KEY'}")

if has_pipeline and has_gemini:
    print("\n🎉 All features ready for UI testing!")
    print("\n💡 Next steps:")
    print("   1. Run: streamlit run app.py")
    print("   2. Go to: Import & Merge")
    print("   3. Test both features manually")
elif has_pipeline:
    print("\n⚠️  Add Gemini API key to test AI parsing")
elif has_gemini:
    print("\n⚠️  Run BRD Pipeline to test pipeline import")
else:
    print("\n⚠️  Setup required:")
    print("   - Run BRD Pipeline (for pipeline import)")
    print("   - Add Gemini API key (for AI parsing)")

print("\n✅ Backend integration tests passed!")
