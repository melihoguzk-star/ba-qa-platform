"""
Projects Router — CRUD endpoints for projects
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from api.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from api.schemas.common import PaginatedResponse, SuccessResponse
from api.services import database_service

router = APIRouter()


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    status: Optional[str] = Query(None, description="Filter by status (active/deleted)"),
    search: Optional[str] = Query(None, description="Search in name and description"),
):
    """
    Get all projects with optional filters.

    - **status**: Filter by status (active/deleted)
    - **search**: Search term for name and description
    """
    projects = database_service.get_projects(status=status, search=search)
    return projects


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(project: ProjectCreate):
    """
    Create a new project.

    - **name**: Project name (unique, required)
    - **description**: Project description (optional)
    """
    try:
        project_id = database_service.create_project(
            name=project.name,
            description=project.description or "",
            jira_project_key="",
            tags=[]
        )

        created_project = database_service.get_project_by_id(project_id)
        if not created_project:
            raise HTTPException(status_code=500, detail="Failed to retrieve created project")

        return created_project

    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=409, detail=f"Project with name '{project.name}' already exists")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int):
    """
    Get a specific project by ID.

    - **project_id**: Project ID
    """
    project = database_service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")

    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project: ProjectUpdate):
    """
    Update a project.

    - **project_id**: Project ID
    - **name**: New project name (optional)
    - **description**: New project description (optional)
    """
    existing_project = database_service.get_project_by_id(project_id)
    if not existing_project:
        raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")

    update_data = {}
    if project.name is not None:
        update_data['name'] = project.name
    if project.description is not None:
        update_data['description'] = project.description

    if update_data:
        try:
            database_service.update_project(project_id, **update_data)
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                raise HTTPException(status_code=409, detail=f"Project with name '{project.name}' already exists")
            raise HTTPException(status_code=500, detail=str(e))

    updated_project = database_service.get_project_by_id(project_id)
    return updated_project


@router.delete("/{project_id}", response_model=SuccessResponse)
def delete_project(project_id: int):
    """
    Soft delete a project (sets status to 'deleted').

    - **project_id**: Project ID
    """
    existing_project = database_service.get_project_by_id(project_id)
    if not existing_project:
        raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")

    database_service.delete_project(project_id)

    return SuccessResponse(
        message=f"Project '{existing_project['name']}' deleted successfully",
        data={"project_id": project_id}
    )
