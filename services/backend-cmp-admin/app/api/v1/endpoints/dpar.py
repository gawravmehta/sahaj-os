from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from typing import List, Literal, Optional

from fastapi.responses import JSONResponse
from app.api.v1.deps import get_current_user, get_dpar_service
from app.services.dpar_service import DPARequestService
from app.schemas.dpar_schema import DPARCreateRequest, ClarificationModel, DPARReportCreate
from app.utils.common import serialize_datetime

router = APIRouter()


@router.get("/get_all")
async def get_all_dpa_requests(
    request: Request,
    page: int = Query(1, description="Page number", ge=1),
    page_size: int = Query(10, description="Number of records per page", ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by request status"),
    dp_type: Optional[str] = Query(None, description="Filter by DP type"),
    created_from: Optional[str] = Query(None, description="Created from date (YYYY-MM-DD)"),
    created_to: Optional[str] = Query(None, description="Created to date (YYYY-MM-DD)"),
    current_user: dict = Depends(get_current_user),
    dpar_service: DPARequestService = Depends(get_dpar_service),
):
    """
    Get all DPA requests with pagination and optional filters.
    """

    return await dpar_service.get_all_requests(
        request=request,
        current_user=current_user,
        page=page,
        page_size=page_size,
        status=status,
        dp_type=dp_type,
        created_from=created_from,
        created_to=created_to,
    )


@router.post("/make-request")
async def make_dpa_request(
    request: DPARCreateRequest,
    request_details: Request,
    current_user: dict = Depends(get_current_user),
    service: DPARequestService = Depends(get_dpar_service),
):
    return await service.create_request(request, request_details, current_user)


@router.get("/get-one/{request_id}")
async def get_one_dpa_request(
    request_id: str,
    current_user: dict = Depends(get_current_user),
    service: DPARequestService = Depends(get_dpar_service),
):
    dpa_request = await service.get_one_request(request_id, current_user)
    return JSONResponse(status_code=200, content={"data": serialize_datetime(dpa_request)})


@router.patch("/set/{status}/{request_id}")
async def set_request_status(
    status: Literal["new", "kyc", "review", "related_req", "approved", "rejected"],
    request_id: str,
    current_user: dict = Depends(get_current_user),
    service: DPARequestService = Depends(get_dpar_service),
    status_details: Optional[str] = None,
):
    result = await service.set_status(request_id, status, status_details, current_user)
    return JSONResponse(status_code=200, content={"data": result})


@router.put("/request/kyc-verifications/{request_id}")
async def request_kyc_verifications(
    request_id: str,
    current_user: dict = Depends(get_current_user),
    service: DPARequestService = Depends(get_dpar_service),
):
    result = await service.request_kyc(request_id, current_user)
    return JSONResponse(status_code=200, content={"message": result})


@router.put("/request/clarification/{request_id}")
async def request_clarification(
    request_id: str,
    clarification_details: ClarificationModel,
    current_user: dict = Depends(get_current_user),
    service: DPARequestService = Depends(get_dpar_service),
):
    result = await service.clarification_request(request_id, clarification_details, current_user)
    return JSONResponse(
        status_code=200,
        content={"message": result},
    )


@router.put("/notes/add/{request_id}")
async def add_notes(
    request_id: str,
    note_title: str,
    note_str: str = None,
    current_user: dict = Depends(get_current_user),
    service: DPARequestService = Depends(get_dpar_service),
):
    result = await service.add_notes(request_id, note_title, note_str, current_user)
    return JSONResponse(
        status_code=200,
        content={"message": result},
    )


@router.put("/notes/delete/{request_id}/{note_id}")
async def delete_notes(
    request_id: str,
    note_id: str,
    current_user: dict = Depends(get_current_user),
    service: DPARequestService = Depends(get_dpar_service),
):
    result = await service.delete_notes(request_id, note_id, current_user)
    return JSONResponse(
        status_code=200,
        content={"message": result},
    )


@router.put("/dpa-request")
async def update_request(
    request_id: str,
    update_data: DPARCreateRequest,
    current_user: dict = Depends(get_current_user),
    service: DPARequestService = Depends(get_dpar_service),
):
    result = await service.update_request(request_id, update_data, current_user)
    return JSONResponse(status_code=200, content={"message": result})


@router.put("/allocate/{request_id}/{assignee_id}")
async def allocate_request(
    request_id: str, assignee_id: str, current_user: dict = Depends(get_current_user), service: DPARequestService = Depends(get_dpar_service)
):

    result = await service.allocate_request(request_id, assignee_id, current_user)
    return JSONResponse(
        status_code=200,
        content={"message": result},
    )


@router.post("/upload-kyc-document")
async def upload_kyc_documents(
    request_id: str,
    kyc_front: Optional[UploadFile] = File(default=None),
    kyc_back: Optional[UploadFile] = File(default=None),
    upload_attachments: List[UploadFile] = File(default=[]),
    current_user: dict = Depends(get_current_user),
    service: DPARequestService = Depends(get_dpar_service),
):

    return await service.upload_kyc_documents(
        request_id,
        current_user,
        kyc_front,
        kyc_back,
        upload_attachments,
    )


@router.get("/presigned-url")
async def get_presigned_url(file_url, current_user: dict = Depends(get_current_user), service: DPARequestService = Depends(get_dpar_service)):
    return await service.get_presigned_url(file_url, current_user)


@router.post("/send-report")
async def send_dpa_report(
    request_id: str, payload: DPARReportCreate, current_user: dict = Depends(get_current_user), service: DPARequestService = Depends(get_dpar_service)
):
    result = await service.send_dpar_report(request_id, payload, current_user)
    return JSONResponse(status_code=201, content=result)


@router.post("/dpar/bulk-upload")
async def dpar_bulk_upload(
    request: Request,
    file: UploadFile,
    current_user: dict = Depends(get_current_user),
    service: DPARequestService = Depends(get_dpar_service),
):
    result = await service.bulk_upload(request, file, current_user)
    return JSONResponse(status_code=201, content=result)


EXPORT_FIELDS = [
    "first_name",
    "last_name",
    "core_identifier",
    "secondary_identifier",
    "dp_type",
    "country",
    "request_type",
    "request_message",
]


def serialize_row(doc):
    return {field: str(doc.get(field, "")) for field in EXPORT_FIELDS}


@router.get("/export-dpar-request")
async def export_request(current_user: dict = Depends(get_current_user), service: DPARequestService = Depends(get_dpar_service)):
    return await service.export_requests(current_user)
