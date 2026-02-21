"""
Design Compliance Service — Vision AI-powered design compliance checking
"""
import base64
from datetime import datetime
from typing import List, Dict, Optional, AsyncGenerator
from pathlib import Path
import tempfile
import os


def analyze_design_compliance(
    ba_document: str,
    image_files: List[bytes],
    project_name: Optional[str] = None,
    checks: Optional[List[str]] = None,
    extra_context: Optional[str] = None,
    model: str = "gemini-2.0-flash-exp",
    api_key: Optional[str] = None
) -> Dict:
    """
    Perform design compliance analysis using 4-agent pipeline.

    Args:
        ba_document: BA document text content
        image_files: List of image file bytes (screens)
        project_name: Optional project name
        checks: List of compliance checks to perform
        extra_context: Additional context
        model: Vision model to use (gemini or claude)
        api_key: API key for the model

    Returns:
        Dict with all agent outputs and final report
    """
    from agents.agent_definitions import create_design_agents
    from agno.media import Image as AgnoImage

    # Default checks
    if checks is None:
        checks = [
            "Gereksinim ↔ Tasarım Eşleştirme (Traceability)",
            "Eksik/Fazla Özellik Tespiti"
        ]

    # Validate API key
    if not api_key:
        from ..config import get_settings
        settings = get_settings()
        if model.startswith("gemini-"):
            api_key = settings.gemini_api_key
        elif model.startswith("claude-"):
            api_key = settings.anthropic_api_key
        else:
            raise ValueError(f"Unknown model type: {model}")

    if not api_key:
        raise ValueError(f"API key required for model {model}")

    # Create agents
    agents = create_design_agents(api_key, model=model)
    if not all(agents):
        raise RuntimeError("Failed to create design agents")

    requirements_agent, screen_agent, compliance_agent, report_agent = agents

    # Process images (resize if needed to prevent API errors)
    design_images = []
    for img_bytes in image_files:
        try:
            from PIL import Image
            import io

            # Open image with PIL
            img = Image.open(io.BytesIO(img_bytes))

            # Check dimensions and resize if needed
            max_dimension = 8000
            width, height = img.size

            if width > max_dimension or height > max_dimension:
                # Calculate new size maintaining aspect ratio
                if width > height:
                    new_width = max_dimension
                    new_height = int(height * (max_dimension / width))
                else:
                    new_height = max_dimension
                    new_width = int(width * (max_dimension / height))

                # Resize image
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                print(f"Resized image from {width}x{height} to {new_width}x{new_height}")

            # Save to temp file
            tmp_path = os.path.join(tempfile.gettempdir(), f"tmp_design_{len(design_images)}.png")
            img.save(tmp_path, format='PNG')

            design_images.append(AgnoImage(filepath=Path(tmp_path)))
        except Exception as e:
            print(f"Warning: Failed to process image: {e}")
            continue

    if not design_images:
        raise ValueError("No valid images provided")

    # Build context strings
    checks_str = ", ".join(checks)
    context_str = f"Proje: {project_name}. {extra_context}" if project_name else extra_context or ""

    # Step 1: Requirements Extraction
    req_prompt = f"""Aşağıdaki iş analizi dokümanından tüm gereksinimleri çıkar.
Kontrol kapsamı: {checks_str}
{f'Ek bağlam: {context_str}' if context_str else ''}

--- İŞ ANALİZİ DOKÜMANI ---
{ba_document}"""

    req_response = requirements_agent.run(req_prompt)
    requirements_output = req_response.content

    # Step 2: Screen Analysis
    screen_prompt = f"""Bu tasarım ekranlarını detaylı analiz et.
{f'Proje: {project_name}' if project_name else ''}
Ekran sayısı: {len(design_images)}"""

    screen_response = screen_agent.run(screen_prompt, images=design_images)
    screen_output = screen_response.content

    # Step 3: Compliance Check
    compliance_prompt = f"""Karşılaştır:
Kontroller: {checks_str}

--- GEREKSİNİMLER ---
{requirements_output}

--- EKRAN ANALİZİ ---
{screen_output}"""

    compliance_response = compliance_agent.run(compliance_prompt, images=design_images)
    compliance_output = compliance_response.content

    # Step 4: Report Generation
    report_prompt = f"""Rapor oluştur.
Proje: {project_name or 'Belirtilmedi'}
Ekran sayısı: {len(design_images)}

--- UYUMLULUK ---
{compliance_output}

--- GEREKSİNİMLER ---
{requirements_output}"""

    report_response = report_agent.run(report_prompt)
    report_output = report_response.content

    # Build full report
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    full_report = f"""# Design Compliance Report

## Proje: {project_name or 'Belirtilmedi'}
## Tarih: {timestamp}
## Ekran Sayısı: {len(design_images)}
## Kontroller: {checks_str}

---

# 1. Gereksinimler
{requirements_output}

---

# 2. Ekran Analizi
{screen_output}

---

# 3. Uyumluluk Kontrolü
{compliance_output}

---

# 4. Final Rapor
{report_output}
"""

    # Cleanup temp files
    for img in design_images:
        try:
            if img.filepath and os.path.exists(img.filepath):
                os.remove(img.filepath)
        except:
            pass

    return {
        "project_name": project_name,
        "num_screens": len(design_images),
        "checks": checks,
        "requirements_output": requirements_output,
        "screen_output": screen_output,
        "compliance_output": compliance_output,
        "report_output": report_output,
        "timestamp": timestamp,
        "full_report": full_report
    }


async def analyze_design_compliance_stream(
    ba_document: str,
    image_files: List[bytes],
    project_name: Optional[str] = None,
    checks: Optional[List[str]] = None,
    extra_context: Optional[str] = None,
    model: str = "gemini-2.0-flash-exp",
    api_key: Optional[str] = None
) -> AsyncGenerator[Dict, None]:
    """
    Streaming version of design compliance analysis.
    Yields progress events as agents complete their work.

    Yields:
        Dict with event_type, step, progress, message, data
    """
    from agents.agent_definitions import create_design_agents
    from agno.media import Image as AgnoImage

    try:
        # Initialize
        yield {
            "event_type": "progress",
            "progress": 0,
            "message": "Initializing agents...",
            "step": None
        }

        # Default checks
        if checks is None:
            checks = [
                "Gereksinim ↔ Tasarım Eşleştirme (Traceability)",
                "Eksik/Fazla Özellik Tespiti"
            ]

        # Validate API key
        if not api_key:
            from ..config import get_settings
            settings = get_settings()
            if model.startswith("gemini-"):
                api_key = settings.gemini_api_key
            elif model.startswith("claude-"):
                api_key = settings.anthropic_api_key

        if not api_key:
            raise ValueError(f"API key required for model {model}")

        # Create agents
        agents = create_design_agents(api_key, model=model)
        if not all(agents):
            raise RuntimeError("Failed to create design agents")

        requirements_agent, screen_agent, compliance_agent, report_agent = agents

        # Process images (resize if needed to prevent API errors)
        yield {
            "event_type": "progress",
            "progress": 5,
            "message": "Processing images...",
            "step": None
        }

        design_images = []
        for img_bytes in image_files:
            try:
                from PIL import Image
                import io

                # Open image with PIL
                img = Image.open(io.BytesIO(img_bytes))

                # Check dimensions and resize if needed
                max_dimension = 8000
                width, height = img.size

                if width > max_dimension or height > max_dimension:
                    # Calculate new size maintaining aspect ratio
                    if width > height:
                        new_width = max_dimension
                        new_height = int(height * (max_dimension / width))
                    else:
                        new_height = max_dimension
                        new_width = int(width * (max_dimension / height))

                    # Resize image
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    print(f"Resized image from {width}x{height} to {new_width}x{new_height}")

                # Save to temp file
                tmp_path = os.path.join(tempfile.gettempdir(), f"tmp_design_{len(design_images)}.png")
                img.save(tmp_path, format='PNG')

                design_images.append(AgnoImage(filepath=Path(tmp_path)))
            except Exception as e:
                print(f"Warning: Failed to process image: {e}")
                continue

        if not design_images:
            raise ValueError("No valid images provided")

        # Build context strings
        checks_str = ", ".join(checks)
        context_str = f"Proje: {project_name}. {extra_context}" if project_name else extra_context or ""

        # Step 1: Requirements Extraction
        yield {
            "event_type": "progress",
            "progress": 10,
            "message": "Extracting requirements...",
            "step": "requirements"
        }

        req_prompt = f"""Aşağıdaki iş analizi dokümanından tüm gereksinimleri çıkar.
Kontrol kapsamı: {checks_str}
{f'Ek bağlam: {context_str}' if context_str else ''}

--- İŞ ANALİZİ DOKÜMANI ---
{ba_document}"""

        req_response = requirements_agent.run(req_prompt)
        requirements_output = req_response.content

        yield {
            "event_type": "agent_output",
            "step": "requirements",
            "progress": 30,
            "data": {"output": requirements_output}
        }

        # Step 2: Screen Analysis
        yield {
            "event_type": "progress",
            "progress": 35,
            "message": f"Analyzing {len(design_images)} screens...",
            "step": "screen_analysis"
        }

        screen_prompt = f"""Bu tasarım ekranlarını detaylı analiz et.
{f'Proje: {project_name}' if project_name else ''}
Ekran sayısı: {len(design_images)}"""

        screen_response = screen_agent.run(screen_prompt, images=design_images)
        screen_output = screen_response.content

        yield {
            "event_type": "agent_output",
            "step": "screen_analysis",
            "progress": 55,
            "data": {"output": screen_output}
        }

        # Step 3: Compliance Check
        yield {
            "event_type": "progress",
            "progress": 60,
            "message": "Checking compliance...",
            "step": "compliance"
        }

        compliance_prompt = f"""Karşılaştır:
Kontroller: {checks_str}

--- GEREKSİNİMLER ---
{requirements_output}

--- EKRAN ANALİZİ ---
{screen_output}"""

        compliance_response = compliance_agent.run(compliance_prompt, images=design_images)
        compliance_output = compliance_response.content

        yield {
            "event_type": "agent_output",
            "step": "compliance",
            "progress": 80,
            "data": {"output": compliance_output}
        }

        # Step 4: Report Generation
        yield {
            "event_type": "progress",
            "progress": 85,
            "message": "Generating report...",
            "step": "report"
        }

        report_prompt = f"""Rapor oluştur.
Proje: {project_name or 'Belirtilmedi'}
Ekran sayısı: {len(design_images)}

--- UYUMLULUK ---
{compliance_output}

--- GEREKSİNİMLER ---
{requirements_output}"""

        report_response = report_agent.run(report_prompt)
        report_output = report_response.content

        yield {
            "event_type": "agent_output",
            "step": "report",
            "progress": 95,
            "data": {"output": report_output}
        }

        # Build full report
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        full_report = f"""# Design Compliance Report

## Proje: {project_name or 'Belirtilmedi'}
## Tarih: {timestamp}
## Ekran Sayısı: {len(design_images)}
## Kontroller: {checks_str}

---

# 1. Gereksinimler
{requirements_output}

---

# 2. Ekran Analizi
{screen_output}

---

# 3. Uyumluluk Kontrolü
{compliance_output}

---

# 4. Final Rapor
{report_output}
"""

        # Complete
        yield {
            "event_type": "complete",
            "progress": 100,
            "message": "Analysis complete!",
            "data": {
                "project_name": project_name,
                "num_screens": len(design_images),
                "checks": checks,
                "requirements_output": requirements_output,
                "screen_output": screen_output,
                "compliance_output": compliance_output,
                "report_output": report_output,
                "timestamp": timestamp,
                "full_report": full_report
            }
        }

        # Cleanup temp files
        for img in design_images:
            try:
                if img.filepath and os.path.exists(img.filepath):
                    os.remove(img.filepath)
            except:
                pass

    except Exception as e:
        yield {
            "event_type": "error",
            "message": str(e),
            "progress": 0
        }
