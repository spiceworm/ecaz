from flask import Blueprint


api_v1_bp = Blueprint(
    "api_v1_bp",
    __name__,
    url_prefix="/v1",
)


@api_v1_bp.route("status")
def status():
    return {"message": "ok"}
