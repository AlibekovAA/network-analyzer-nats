from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator, cast
from io import BytesIO

from fastapi import FastAPI, HTTPException, UploadFile, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.backend.log import get_logger
from app.backend.nats_client import NATSClient
from app.backend.models import NetworkAnalysisResult
from app.backend.config import NATS_SERVER_URL
from app.backend.network_analyzer import NetworkAnalyzer


logger = get_logger(__name__)


class AppState:
    def __init__(self) -> None:
        self.nats_client: NATSClient = NATSClient(server_url=NATS_SERVER_URL)
        self.network_analyzer: NetworkAnalyzer = NetworkAnalyzer(self.nats_client)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    state = AppState()
    app.state.nats_client = state.nats_client
    app.state.network_analyzer = state.network_analyzer

    try:
        await app.state.nats_client.connect()
        logger.info("[Server] Python server started and connected to NATS")
        yield
    except Exception as e:
        logger.error(f"[Server] Failed to start server: {str(e)}")
        raise
    finally:
        await app.state.nats_client.close()
        logger.info("[Server] Python server shutting down")


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/frontend"), name="static")


def get_app_state() -> AppState:
    return cast(AppState, app.state)


async def get_analyzer() -> NetworkAnalyzer:
    return get_app_state().network_analyzer


@app.get("/", response_class=HTMLResponse)
async def get_html() -> HTMLResponse:
    with open("app/frontend/index.html") as f:
        return HTMLResponse(content=f.read())


@app.get("/health")
async def health_check() -> dict[str, bool | str]:
    return {
        "status": "healthy",
        "nats_connected": app.state.nats_client.is_connected()
    }


@app.post("/analyze-network", response_model=NetworkAnalysisResult)
async def analyze_network_packets(
    file: UploadFile,
    analyzer: Annotated[NetworkAnalyzer, Depends(get_analyzer)]
) -> NetworkAnalysisResult:
    if not file.filename or not file.filename.endswith('.pcap'):
        logger.warning(f"[API] Attempted to upload non-PCAP file: {file.filename}")
        raise HTTPException(status_code=400, detail="Only PCAP files are supported")

    MAX_FILE_SIZE: int = 200 * 1024 * 1024
    contents_file = bytearray()
    chunk_size = 1024 * 1024
    total_size = 0

    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > MAX_FILE_SIZE:
            logger.warning(f"[API] File size exceeds limit: {total_size} bytes > {MAX_FILE_SIZE} bytes")
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE/1024/1024}MB"
            )
        contents_file.extend(chunk)

    try:
        result = await analyzer.analyze_pcap(BytesIO(contents_file))
        logger.info(f"[API] Successfully analyzed network packets from {file.filename}")
        return result
    except Exception as e:
        logger.error(f"[API] Failed to analyze network packets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
