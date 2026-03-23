"""Controles locais do sistema para ambiente de desenvolvimento."""
import os
import subprocess
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.models.user import User
from app.utils.deps import get_current_user

router = APIRouter(prefix="/system", tags=["system"])

_LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1", "testclient"}


def _ensure_local_only(request: Request) -> None:
    if os.environ.get("MARKETINGAI_ENV", "development").strip().lower() == "production":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Controle local desabilitado em producao")
    if os.environ.get("MARKETINGAI_LOCAL_CONTROL") != "1":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Controle local disponivel apenas quando iniciado pelo run.bat")
    client_host = (request.client.host if request.client else "").strip().lower()
    if client_host not in _LOCAL_HOSTS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Controle local disponivel apenas via localhost")


def _launch_stop_script(root: Path) -> None:
    stop_script = root / "stop.bat"
    if not stop_script.is_file():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="stop.bat nao encontrado")
    subprocess.Popen(
        ["cmd", "/c", "start", "", "cmd", "/c", f'timeout /t 2 /nobreak >nul & call "{stop_script}"'],
        cwd=str(root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


@router.post("/stop-local")
def stop_local_system(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    _ensure_local_only(request)
    root = Path(__file__).resolve().parent.parent.parent.parent
    _launch_stop_script(root)
    return {
        "status": "stopping",
        "message": "Encerramento local iniciado.",
        "requested_by": current_user.email,
    }
