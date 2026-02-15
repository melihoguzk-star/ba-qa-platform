"""Unit tests for OpenAPI Generator

Tests the OpenAPI 3.0.4 specification generation from TA JSON output.
"""

import json
import pytest
from pipeline.brd.openapi_generator import (
    generate_openapi_spec,
    export_to_json,
    validate_openapi_spec,
    _map_type_to_openapi,
    _normalize_path
)


def test_generate_openapi_spec_basic():
    """Test basic OpenAPI spec generation"""
    
    ta_content = {
        "teknik_analiz": {
            "genel_tanim": {
                "modul_adi": "Test Module",
                "teknoloji_stack": ["Python", "FastAPI"],
                "mimari_yaklasim": "Microservices"
            },
            "api_endpoint_ozeti": [
                {
                    "endpoint": "/api/v1/bo-test/users",
                    "method": "GET",
                    "aciklama": "Get all users",
                    "tag": "Users",
                    "query_parametreleri": [
                        {"ad": "pageNumber", "tip": "int", "zorunlu": False},
                        {"ad": "pageSize", "tip": "int", "zorunlu": False}
                    ],
                    "response_model": "UserListResponse",
                    "paginated": True
                }
            ],
            "request_response_modelleri": [
                {
                    "model_adi": "UserListResponse",
                    "alanlar": [
                        {"alan_adi": "users", "tip": "User[]", "zorunlu": True, "aciklama": "User list"},
                        {"alan_adi": "total", "tip": "int", "zorunlu": True, "aciklama": "Total count"}
                    ]
                }
            ]
        }
    }
    
    spec = generate_openapi_spec(ta_content, "TestProject", "1.0.0")
    
    # Basic structure checks
    assert spec["openapi"] == "3.0.4"
    assert spec["info"]["title"] == "TestProject API"
    assert spec["info"]["version"] == "1.0.0"
    assert "paths" in spec
    assert "components" in spec
    assert "schemas" in spec["components"]
    
    # Check EnliqResponse wrapper exists
    assert "EnliqResponse" in spec["components"]["schemas"]
    assert "PaginatedResponse" in spec["components"]["schemas"]
    
    # Check endpoint
    assert "/users" in spec["paths"]
    assert "get" in spec["paths"]["/users"]
    
    # Check response model
    assert "UserListResponse" in spec["components"]["schemas"]


def test_type_mapping():
    """Test TA type to OpenAPI type mapping"""
    
    assert _map_type_to_openapi("string") == {"type": "string"}
    assert _map_type_to_openapi("int") == {"type": "integer", "format": "int32"}
    assert _map_type_to_openapi("long") == {"type": "integer", "format": "int64"}
    assert _map_type_to_openapi("decimal") == {"type": "number", "format": "double"}
    assert _map_type_to_openapi("boolean") == {"type": "boolean"}
    assert _map_type_to_openapi("datetime") == {"type": "string", "format": "date-time"}
    assert _map_type_to_openapi("uuid") == {"type": "string", "format": "uuid"}
    
    # Array types
    array_result = _map_type_to_openapi("string[]")
    assert array_result["type"] == "array"
    assert array_result["items"]["type"] == "string"


def test_path_normalization():
    """Test path normalization"""
    
    assert _normalize_path("/api/v1/bo-service/users") == "/users"
    assert _normalize_path("/api/v1/bo-notifica/attribute/{id}") == "/attribute/{id}"
    assert _normalize_path("/users") == "/users"
    assert _normalize_path("/api/v1/users/{id}") == "/users/{id}"


def test_validate_openapi_spec():
    """Test OpenAPI spec validation"""
    
    # Valid spec
    valid_spec = {
        "openapi": "3.0.4",
        "info": {"title": "Test", "version": "1.0.0"},
        "paths": {}
    }
    is_valid, message = validate_openapi_spec(valid_spec)
    assert is_valid is True
    assert "Valid" in message
    
    # Missing required field
    invalid_spec = {
        "openapi": "3.0.4",
        "info": {"title": "Test", "version": "1.0.0"}
    }
    is_valid, message = validate_openapi_spec(invalid_spec)
    assert is_valid is False
    assert "paths" in message
    
    # Wrong version
    wrong_version = {
        "openapi": "2.0.0",
        "info": {"title": "Test", "version": "1.0.0"},
        "paths": {}
    }
    is_valid, message = validate_openapi_spec(wrong_version)
    assert is_valid is False
    assert "version" in message


def test_export_to_json():
    """Test JSON export"""
    
    spec = {
        "openapi": "3.0.4",
        "info": {"title": "Test", "version": "1.0.0"},
        "paths": {}
    }
    
    json_output = export_to_json(spec)
    
    # Should be valid JSON
    parsed = json.loads(json_output)
    assert parsed["openapi"] == "3.0.4"
    assert parsed["info"]["title"] == "Test"
    
    # Should be formatted with indentation
    assert "\n" in json_output
    assert "  " in json_output


def test_enliq_response_wrapper():
    """Test EnliqResponse wrapper in responses"""
    
    ta_content = {
        "teknik_analiz": {
            "api_endpoint_ozeti": [
                {
                    "endpoint": "/api/v1/bo-test/users/{id}",
                    "method": "GET",
                    "aciklama": "Get user by ID",
                    "tag": "Users",
                    "path_parametreleri": [
                        {"ad": "id", "tip": "uuid", "aciklama": "User ID"}
                    ],
                    "response_model": "UserResponse"
                }
            ],
            "request_response_modelleri": [
                {
                    "model_adi": "UserResponse",
                    "alanlar": [
                        {"alan_adi": "id", "tip": "uuid", "zorunlu": True},
                        {"alan_adi": "name", "tip": "string", "zorunlu": True}
                    ]
                }
            ]
        }
    }
    
    spec = generate_openapi_spec(ta_content, "TestProject")
    
    # Check that response uses EnliqResponse wrapper
    user_endpoint = spec["paths"]["/users/{id}"]["get"]
    response_200 = user_endpoint["responses"]["200"]
    
    assert "content" in response_200
    assert "application/json" in response_200["content"]
    
    schema = response_200["content"]["application/json"]["schema"]
    assert "allOf" in schema
    assert {"$ref": "#/components/schemas/EnliqResponse"} in schema["allOf"]
    
    # Check error responses
    assert "400" in user_endpoint["responses"]
    assert "500" in user_endpoint["responses"]
    assert "404" in user_endpoint["responses"]  # GET with path param should have 404


def test_pagination_parameters():
    """Test pagination parameters are added correctly"""
    
    ta_content = {
        "teknik_analiz": {
            "api_endpoint_ozeti": [
                {
                    "endpoint": "/api/v1/bo-test/users",
                    "method": "GET",
                    "aciklama": "List users",
                    "tag": "Users",
                    "paginated": True,
                    "response_model": "UserListResponse"
                }
            ],
            "request_response_modelleri": []
        }
    }
    
    spec = generate_openapi_spec(ta_content, "TestProject")
    
    endpoint = spec["paths"]["/users"]["get"]
    param_names = [p["name"] for p in endpoint["parameters"]]
    
    # Check pagination params
    assert "pageNumber" in param_names
    assert "pageSize" in param_names
    assert "sortType" in param_names
    assert "sortingColumn" in param_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
