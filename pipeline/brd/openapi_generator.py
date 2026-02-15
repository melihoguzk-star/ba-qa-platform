"""OpenAPI 3.0.4 Specification Generator

TA (Teknik Analiz) JSON çıktısından Loodos şirket standartlarına uygun
OpenAPI 3.0.4 specification oluşturur.

Özellikler:
- EnliqResponse wrapper (tüm response'larda)
- Standart error responses (400, 500, 404)
- Pagination desteği (pageNumber, pageSize, sortType, sortingColumn)
- X-UserId header desteği
- Resource bazlı tags
"""

import json
from typing import Dict, List, Any, Optional, Union, cast


def generate_openapi_spec(
    ta_content: dict,
    ba_content: dict,
    project_name: str,
    version: str = "1.0.0",
    base_path: str = "/api/v1"
) -> dict:
    """
    TA ve BA JSON'ından OpenAPI 3.0.4 spec oluşturur.
    
    Args:
        ta_content: Teknik Analiz JSON içeriği
        ba_content: Business Analiz JSON içeriği
        project_name: Proje adı
        version: API versiyonu
        base_path: Base URL path (örn: /api/v1/bo-myservice)
    
    Returns:
        OpenAPI 3.0.4 specification dict
    """
    
    # TA içeriğinden teknik analiz objesini çıkar
    ta = ta_content.get("teknik_analiz", ta_content)
    
    # Base OpenAPI structure
    openapi_spec = {
        "openapi": "3.0.4",
        "info": {
            "title": f"{project_name} API",
            "description": f"{project_name} API Documentation",
            "termsOfService": "https://loodos.com/",
            "contact": {
                "name": "Loodos",
                "url": "https://loodos.com/",
                "email": ""
            },
            "version": version
        },
        "servers": [
            {
                "url": f"https://api.example.com{base_path}",
                "description": "Production"
            },
            {
                "url": f"https://staging-api.example.com{base_path}",
                "description": "Staging"
            }
        ],
        "paths": {},
        "components": {
            "schemas": _build_schemas(ta),
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        },
        "security": [
            {"BearerAuth": []}
        ]
    }
    
    # Endpoint'leri paths'e ekle
    endpoints = ta.get("api_endpoint_ozeti", [])
    openapi_spec["paths"] = _build_paths(endpoints, ta)
    
    return openapi_spec


def _build_schemas(ta: dict) -> dict:
    """Component schemas oluşturur (EnliqResponse wrapper dahil)."""
    
    schemas = {
        # ProcessStatus enum
        "ProcessStatus": {
            "type": "string",
            "enum": ["Success", "Warning", "Error"],
            "description": "İşlem durumu"
        },
        
        # FriendlyMessage object
        "FriendlyMessage": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Mesaj başlığı"
                },
                "message": {
                    "type": "string",
                    "description": "Mesaj içeriği"
                },
                "cancelable": {
                    "type": "boolean",
                    "description": "İptal edilebilir mi?"
                },
                "buttonPositive": {
                    "type": "string",
                    "description": "Pozitif buton metni"
                },
                "buttonNegative": {
                    "type": "string",
                    "description": "Negatif buton metni"
                },
                "buttonNeutral": {
                    "type": "string",
                    "description": "Nötr buton metni"
                }
            },
            "nullable": True
        },
        
        # Base EnliqResponse wrapper (new standard)
        "EnliqResponse": {
            "type": "object",
            "properties": {
                "processStatus": {
                    "$ref": "#/components/schemas/ProcessStatus",
                    "description": "İşlem durumu"
                },
                "friendlyMessage": {
                    "$ref": "#/components/schemas/FriendlyMessage",
                    "description": "Kullanıcı dostu mesaj"
                },
                "serverTime": {
                    "type": "integer",
                    "format": "int32",
                    "description": "Sunucu zamanı (Unix timestamp)"
                },
                "payload": {
                    "type": "object",
                    "description": "Response data",
                    "nullable": True
                }
            }
        },
        
        # Pagination wrapper
        "PaginatedResponse": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object"
                    },
                    "description": "Sayfa içeriği"
                },
                "pageNumber": {
                    "type": "integer",
                    "format": "int32",
                    "description": "Mevcut sayfa numarası"
                },
                "pageSize": {
                    "type": "integer",
                    "format": "int32",
                    "description": "Sayfa boyutu"
                },
                "totalPages": {
                    "type": "integer",
                    "format": "int32",
                    "description": "Toplam sayfa sayısı"
                },
                "totalCount": {
                    "type": "integer",
                    "format": "int32",
                    "description": "Toplam kayıt sayısı"
                },
                "hasPrevious": {
                    "type": "boolean",
                    "description": "Önceki sayfa var mı?"
                },
                "hasNext": {
                    "type": "boolean",
                    "description": "Sonraki sayfa var mı?"
                }
            }
        }
    }
    
    # TA'dan request/response modellerini ekle
    models = ta.get("request_response_modelleri", [])
    for model in models:
        model_name = model.get("model_adi", "UnknownModel")
        schema = _convert_model_to_schema(model)
        schemas[model_name] = schema
    
    return schemas


def _convert_model_to_schema(model: Dict[str, Any]) -> Dict[str, Any]:
    """TA model'ini OpenAPI schema'ya dönüştürür."""

    properties: Dict[str, Any] = {}
    required: List[str] = []
    
    fields = model.get("alanlar", [])
    for field in fields:
        field_name = field.get("alan_adi", "unknown")
        field_type = field.get("tip", "string")
        is_required = field.get("zorunlu", False)
        description = field.get("aciklama", "")
        
        # OpenAPI type mapping
        openapi_type = _map_type_to_openapi(field_type)
        
        properties[field_name] = {
            "type": openapi_type["type"],
            "description": description
        }
        
        if openapi_type.get("format"):
            properties[field_name]["format"] = openapi_type["format"]
        
        if openapi_type.get("items"):
            properties[field_name]["items"] = openapi_type["items"]
        
        if is_required:
            required.append(field_name)

    schema: Dict[str, Any] = {
        "type": "object",
        "properties": properties
    }

    if required:
        schema["required"] = required

    return schema


def _map_type_to_openapi(field_type: str) -> Dict[str, Any]:
    """TA field type'ını OpenAPI type'a map eder."""

    type_mapping: Dict[str, Dict[str, str]] = {
        "string": {"type": "string"},
        "int": {"type": "integer", "format": "int32"},
        "long": {"type": "integer", "format": "int64"},
        "decimal": {"type": "number", "format": "double"},
        "double": {"type": "number", "format": "double"},
        "float": {"type": "number", "format": "float"},
        "boolean": {"type": "boolean"},
        "bool": {"type": "boolean"},
        "datetime": {"type": "string", "format": "date-time"},
        "date": {"type": "string", "format": "date"},
        "uuid": {"type": "string", "format": "uuid"},
        "guid": {"type": "string", "format": "uuid"},
    }
    
    # Array kontrolü
    if "[]" in field_type or "list" in field_type.lower() or "array" in field_type.lower():
        base_type = field_type.replace("[]", "").replace("List<", "").replace(">", "").strip()
        item_type = type_mapping.get(base_type.lower(), {"type": "string"})
        return {
            "type": "array",
            "items": item_type
        }
    
    return type_mapping.get(field_type.lower(), {"type": "string"})


def _build_paths(endpoints: List[dict], ta: dict) -> dict:
    """API endpoint'lerinden OpenAPI paths oluşturur."""
    
    paths = {}
    
    for endpoint in endpoints:
        path = endpoint.get("endpoint", "/unknown")
        method = endpoint.get("method", "GET").lower()
        description = endpoint.get("aciklama", "")
        tag = endpoint.get("tag", "Default")
        
        # Path parametrelerini OpenAPI formatına çevir
        # Örn: /api/users/{id} -> /users/{id}
        openapi_path = _normalize_path(path)
        
        if openapi_path not in paths:
            paths[openapi_path] = {}
        
        # Operation object oluştur
        operation = {
            "tags": [tag],
            "summary": description or f"{method.upper()} {openapi_path}",
            "operationId": f"{method}_{openapi_path.replace('/', '_').replace('{', '').replace('}', '')}",
            "parameters": _build_parameters(endpoint),
            "responses": _build_responses(endpoint, ta)
        }
        
        # Request body varsa ekle
        request_body = _build_request_body(endpoint, ta)
        if request_body:
            operation["requestBody"] = request_body
        
        paths[openapi_path][method] = operation
    
    return paths


def _normalize_path(path: str) -> str:
    """Path'i normalize eder (base path'i kaldırır)."""
    
    # /api/v1/bo-service/users/{id} -> /users/{id}
    parts = path.split("/")
    
    # api, v1, bo-service gibi prefix'leri atla
    normalized_parts = []
    skip_next = False
    
    for part in parts:
        if not part:
            continue
        if part in ["api", "v1"] or part.startswith("bo-"):
            continue
        normalized_parts.append(part)
    
    return "/" + "/".join(normalized_parts) if normalized_parts else "/"


def _build_parameters(endpoint: dict) -> List[dict]:
    """Endpoint parametrelerini oluşturur."""
    
    parameters = []
    
    # Path parameters
    path_params = endpoint.get("path_parametreleri", [])
    for param in path_params:
        parameters.append({
            "name": param.get("ad", "id"),
            "in": "path",
            "required": True,
            "schema": {
                "type": _map_type_to_openapi(param.get("tip", "string"))["type"]
            },
            "description": param.get("aciklama", "")
        })
    
    # Query parameters
    query_params = endpoint.get("query_parametreleri", [])
    for param in query_params:
        param_schema = {
            "name": param.get("ad", "param"),
            "in": "query",
            "required": param.get("zorunlu", False),
            "schema": _map_type_to_openapi(param.get("tip", "string")),
            "description": param.get("aciklama", "")
        }
        parameters.append(param_schema)
    
    # Pagination parametreleri ekle (GET istekleri için)
    if endpoint.get("method", "GET").upper() == "GET" and endpoint.get("paginated", False):
        parameters.extend([
            {
                "name": "pageNumber",
                "in": "query",
                "schema": {"type": "integer", "format": "int32", "default": 1},
                "description": "Sayfa numarası"
            },
            {
                "name": "pageSize",
                "in": "query",
                "schema": {"type": "integer", "format": "int32", "default": 10},
                "description": "Sayfa boyutu"
            },
            {
                "name": "sortType",
                "in": "query",
                "schema": {"type": "string", "enum": ["Asc", "Desc"]},
                "description": "Sıralama yönü"
            },
            {
                "name": "sortingColumn",
                "in": "query",
                "schema": {"type": "string"},
                "description": "Sıralama kolonu"
            }
        ])
    
    # X-UserId header (POST, PUT, DELETE için)
    if endpoint.get("method", "GET").upper() in ["POST", "PUT", "DELETE"]:
        if endpoint.get("requires_user_id", False):
            parameters.append({
                "name": "X-UserId",
                "in": "header",
                "schema": {"type": "string"},
                "description": "Kullanıcı ID"
            })
    
    return parameters


def _build_request_body(endpoint: dict, ta: dict) -> Optional[dict]:
    """Request body oluşturur."""
    
    method = endpoint.get("method", "GET").upper()
    
    # GET ve DELETE genelde body almaz
    if method in ["GET", "DELETE"]:
        return None
    
    request_model = endpoint.get("request_model", "")
    
    if not request_model:
        return None
    
    # Model referansı
    return {
        "content": {
            "application/json": {
                "schema": {
                    "$ref": f"#/components/schemas/{request_model}"
                }
            },
            "text/json": {
                "schema": {
                    "$ref": f"#/components/schemas/{request_model}"
                }
            },
            "application/*+json": {
                "schema": {
                    "$ref": f"#/components/schemas/{request_model}"
                }
            }
        }
    }


def _build_responses(endpoint: Dict[str, Any], ta: Dict[str, Any]) -> Dict[str, Any]:
    """Response definitions oluşturur (EnliqResponse wrapper ile)."""

    responses: Dict[str, Any] = {}
    
    response_model = endpoint.get("response_model", "")
    
    # 200 OK
    responses["200"] = {
        "description": "OK",
        "content": {
            "application/json": {
                "schema": {
                    "allOf": [
                        {"$ref": "#/components/schemas/EnliqResponse"},
                        {
                            "type": "object",
                            "properties": {
                                "payload": {
                                    "$ref": f"#/components/schemas/{response_model}" if response_model else {"type": "object"}
                                }
                            }
                        }
                    ]
                }
            }
        }
    }
    
    # 400 Bad Request
    responses["400"] = {
        "description": "Bad Request",
        "content": {
            "application/json": {
                "schema": {
                    "$ref": "#/components/schemas/EnliqResponse"
                }
            }
        }
    }
    
    # 500 Internal Server Error
    responses["500"] = {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "schema": {
                    "$ref": "#/components/schemas/EnliqResponse"
                }
            }
        }
    }
    
    # 404 Not Found (GET, PUT, DELETE için)
    method = endpoint.get("method", "GET").upper()
    if method in ["GET", "PUT", "DELETE"] and "{" in endpoint.get("endpoint", ""):
        responses["404"] = {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/EnliqResponse"
                    }
                }
            }
        }
    
    return responses


def export_to_json(openapi_spec: dict, indent: int = 2) -> str:
    """OpenAPI spec'i JSON string'e dönüştürür."""
    return json.dumps(openapi_spec, ensure_ascii=False, indent=indent)


def validate_openapi_spec(openapi_spec: dict) -> tuple[bool, str]:
    """
    OpenAPI spec'in temel doğrulamasını yapar.
    
    Returns:
        (is_valid, error_message)
    """
    
    required_fields = ["openapi", "info", "paths"]
    
    for field in required_fields:
        if field not in openapi_spec:
            return False, f"Missing required field: {field}"
    
    if openapi_spec["openapi"] != "3.0.4":
        return False, f"Invalid OpenAPI version: {openapi_spec['openapi']}"
    
    if not isinstance(openapi_spec["paths"], dict):
        return False, "paths must be an object"
    
    return True, "Valid OpenAPI 3.0.4 specification"


# ═══════════════════════════════════════════════════════════
# AI-ASSISTED GENERATION
# ═══════════════════════════════════════════════════════════

def generate_openapi_with_ai(
    ta_content: dict,
    ba_content: dict,
    project_name: str,
    anthropic_key: str,
    gemini_key: str,
    version: str = "1.0.0",
    base_path: str = "/api/v1",
    model: str = None,
    log=None
) -> dict:
    """
    AI ile zenginleştirilmiş OpenAPI spec oluşturur (BA + TA kombinasyonu).
    
    Args:
        ta_content: Teknik Analiz JSON içeriği
        ba_content: Business Analiz JSON içeriği
        project_name: Proje adı
        anthropic_key: Anthropic API key
        gemini_key: Gemini API key
        version: API versiyonu
        base_path: Base URL path
        model: AI model (None ise default)
        log: Log fonksiyonu
    
    Returns:
        OpenAPI 3.0.4 specification dict
    """
    from agents.brd_prompts import OPENAPI_SYSTEM
    from agents.ai_client import call_ai
    
    if log:
        log("    🤖 AI ile OpenAPI spec oluşturuluyor...")
    
    # TA içeriğini özetle (token limiti için)
    ta = ta_content.get("teknik_analiz", ta_content)
    ta_summary = json.dumps({
        "genel_tanim": ta.get("genel_tanim", {}),
        "api_endpoint_ozeti": ta.get("api_endpoint_ozeti", []),
        "request_response_modelleri": ta.get("request_response_modeller", [])
    }, ensure_ascii=False, indent=2)

    # BA içeriğini özetle
    ba_summary = json.dumps(ba_content, ensure_ascii=False, indent=2)
    
    # User prompt oluştur
    user_prompt = f"""PROJE: {project_name}
VERSION: {version}
BASE_PATH: {base_path}

TEKNİK ANALİZ:
{ta_summary}

BUSINESS ANALİZ:
{ba_summary}

Yukarıdaki Teknik Analiz ve Business Analiz'den Loodos standartlarına %100 uyumlu OpenAPI 3.0.4 spec oluştur.

ZORUNLU:
- EnliqResponse wrapper kullan
- Pagination parametreleri ekle (GET list endpoint'leri için)
- X-UserId header ekle (POST/PUT/DELETE için)
- Error responses (400, 500, 404)
- Zengin açıklamalar ve example values

SADECE JSON DÖNDÜR, başka metin ekleme."""
    
    # AI çağrısı
    try:
        response = call_ai(
            OPENAPI_SYSTEM,
            user_prompt,
            anthropic_key,
            gemini_key,
            model,
            output_token_limit=16000
        )
        
        # Response'u parse et
        if isinstance(response, dict):
            # Eğer response zaten dict ise direkt kullan
            openapi_spec = response
        elif isinstance(response, str):
            # String ise JSON parse et
            openapi_spec = json.loads(response)
        else:
            raise ValueError(f"Unexpected AI response type: {type(response)}")
        
        if log:
            log("    ✅ AI generation tamamlandı")
        
        return openapi_spec
        
    except json.JSONDecodeError as e:
        if log:
            error_msg: str = str(e)
            log(f"    ❌ AI response JSON parse hatası: {error_msg[:100]}")
        raise ValueError(f"AI invalid JSON döndürdü: {str(e)}")
    except Exception as e:
        if log:
            error_msg: str = str(e)
            log(f"    ❌ AI generation hatası: {error_msg[:100]}")
        raise


def validate_loodos_standards(openapi_spec: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    OpenAPI spec'in Loodos standartlarına uygunluğunu kontrol eder.

    Returns:
        (is_valid, error_messages)
    """
    errors: List[str] = []
    
    # 1. EnliqResponse wrapper kontrolü
    schemas = openapi_spec.get("components", {}).get("schemas", {})
    if "EnliqResponse" not in schemas:
        errors.append("EnliqResponse schema eksik")
    else:
        enliq = schemas["EnliqResponse"]
        # Yeni standart: processStatus, friendlyMessage, serverTime, payload
        required_props = ["processStatus", "friendlyMessage", "serverTime", "payload"]
        for prop in required_props:
            if prop not in enliq.get("properties", {}):
                errors.append(f"EnliqResponse.{prop} property eksik")
    
    # 2. Response'larda EnliqResponse kullanımı kontrolü
    paths = openapi_spec.get("paths", {})
    for path, methods in paths.items():
        for method, operation in methods.items():
            method_str = str(method)  # Type assertion for Pylance
            if method_str not in ["get", "post", "put", "delete", "patch"]:
                continue
            
            responses = operation.get("responses", {})
            if "200" in responses:
                response_200 = responses["200"]
                content = response_200.get("content", {})
                if "application/json" in content:
                    schema = content["application/json"].get("schema", {})
                    # allOf ile EnliqResponse referansı kontrolü
                    if "allOf" in schema:
                        has_enliq = any(
                            "$ref" in item and "EnliqResponse" in item["$ref"]
                            for item in schema["allOf"]
                        )
                        if not has_enliq:
                            errors.append(f"{method_str.upper()} {path}: 200 response EnliqResponse kullanmıyor")
                    elif "$ref" not in schema or "EnliqResponse" not in schema.get("$ref", ""):
                        errors.append(f"{method_str.upper()} {path}: 200 response EnliqResponse kullanmıyor")

            # 3. Error responses kontrolü
            if "400" not in responses:
                errors.append(f"{method_str.upper()} {path}: 400 response eksik")
            if "500" not in responses:
                errors.append(f"{method_str.upper()} {path}: 500 response eksik")
    
    # 4. Pagination kontrolü (GET list endpoint'leri için)
    for path, methods in paths.items():
        if "get" in methods:
            operation = methods["get"]
            # Eğer response array dönüyorsa pagination olmalı
            params = operation.get("parameters", [])
            param_names = [p.get("name") for p in params]
            
            # En azından bir pagination parametresi varsa diğerleri de olmalı
            pagination_params = ["pageNumber", "pageSize", "sortType", "sortingColumn"]
            has_any_pagination = any(p in param_names for p in pagination_params)
            
            if has_any_pagination:
                for param in pagination_params:
                    if param not in param_names:
                        errors.append(f"GET {path}: {param} pagination parametresi eksik")
    
    return (len(errors) == 0, errors)


def generate_openapi_spec_hybrid(
    ta_content: dict,
    ba_content: dict,
    project_name: str,
    anthropic_key: str,
    gemini_key: str,
    version: str = "1.0.0",
    base_path: str = "/api/v1",
    model: str = None,
    log=None
) -> dict:
    """
    Hybrid OpenAPI generation: AI ile dene (BA+TA), başarısız olursa code-based'e düş.
    
    Args:
        ta_content: Teknik Analiz JSON içeriği
        ba_content: Business Analiz JSON içeriği
        project_name: Proje adı
        anthropic_key: Anthropic API key
        gemini_key: Gemini API key
        version: API versiyonu
        base_path: Base URL path
        model: AI model
        log: Log fonksiyonu
    
    Returns:
        OpenAPI 3.0.4 specification dict
    """
    
    try:
        # AI ile generate et
        spec = generate_openapi_with_ai(
            ta_content, ba_content, project_name, anthropic_key, gemini_key,
            version, base_path, model, log
        )
        
        # Loodos standartlarını validate et
        if log:
            log("    🔍 Loodos standartları kontrol ediliyor...")

        is_valid: bool
        errors: List[str]
        is_valid, errors = validate_loodos_standards(spec)
        
        if is_valid:
            if log:
                log("    ✅ Loodos standartları validation başarılı")
            return spec
        else:
            if log:
                log(f"    ⚠️ Loodos validation başarısız ({len(errors)} hata)")
                for error in errors[:3]:  # İlk 3 hatayı göster
                    log(f"       - {error}")
                if len(errors) > 3:
                    log(f"       ... ve {len(errors) - 3} hata daha")
                log("    🔄 Code-based generation'a geçiliyor...")
            
            # Fallback to code-based
            return generate_openapi_spec(ta_content, ba_content, project_name, version, base_path)
    
    except Exception as e:
        if log:
            error_msg: str = str(e)
            log(f"    ❌ AI generation hatası: {error_msg[:150]}")
            log("    🔄 Code-based generation'a geçiliyor...")

        # Fallback to code-based
        return generate_openapi_spec(ta_content, ba_content, project_name, version, base_path)
