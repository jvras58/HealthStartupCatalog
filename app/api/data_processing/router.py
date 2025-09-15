import os
import tempfile
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session

from app.api.authentication.controller import get_current_user
from app.api.authorization.controller import validate_transaction_access
from app.api.data_processing.controller import DataProcessingController
from app.api.data_processing.schemas import CatalogRequest, CatalogResponse
from app.database.session import get_session
from app.models.user import User

router = APIRouter()
controller = DataProcessingController()

DbSession = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

@router.post("/catalog", response_model=CatalogResponse)
def process_catalog(
    request: CatalogRequest,
    pdf: UploadFile = None,
    db_session: Session = DbSession,
    current_user: CurrentUser = CurrentUser,
):
    validate_transaction_access(db_session, current_user, "OP_3000001")
    pdf_path = None
    if pdf:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = pdf.file.read()
            tmp.write(content)
            pdf_path = tmp.name

    result = controller.process_catalog(
        db_session, request.url, pdf_path, request.clues, current_user
    )
    if pdf_path:
        os.unlink(pdf_path)
    return CatalogResponse(**result)
