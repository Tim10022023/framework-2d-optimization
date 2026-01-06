from fastapi import APIRouter
from app.core.functions import list_function_specs

router = APIRouter(prefix="/functions", tags=["functions"])


@router.get("")
def list_functions():
    return {"functions": list_function_specs()}
