"""HTTP adapter: request parsing, dependency injection, and service delegation."""
from fastapi import APIRouter, Query, Depends
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.dependencies import get_current_user, get_optional_user
from backend.modules.identity.access import Principal, optional_child
from backend.modules.curriculum import audio as service
from backend.schemas import SpeechEvaluationRequest, SpeechEvaluationResponse

router = APIRouter(prefix='/api/audio', tags=['Audio & Pronunciation'])

@router.get('/tts-info')
def get_tts_info():
    """Returns supported TTS modes, Arabic voice configs, and playback parameters."""
    return service.get_tts_info()

@router.get('/synthesize')
def synthesize_audio(text: str=Query(..., max_length=1000, description='Arabic text to vocalize'), speed: float=Query(1.0, description='Browser playback rate'), lang: str=Query('ar-SA'), content_version: str=Query('1'), actor=Depends(get_optional_user)):
    """
    Server-side TTS metadata endpoint.
    Labels audio explicitly as synthetic to satisfy Section 11.
    """
    return service.synthesize_audio(text=text, speed=speed, lang=lang, content_version=content_version)

@router.post('/synthesize-async')
def synthesize_audio_async(
    payload: dict,
    actor: Principal = Depends(get_optional_user)
):
    """
    Offload heavy TTS generation to the background task queue.
    Prevents HTTP worker starvation under high concurrent learner load.
    """
    from backend.tasks.queue import enqueue_task
    text = payload.get("text", "").strip()
    if not text:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    if len(text) > 1000:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Text exceeds maximum limit of 1000 characters")
    task = enqueue_task(
        task_type="synthesize_audio",
        params={
            "text": text,
            "speed": payload.get("speed", 1.0),
            "lang": payload.get("lang", "ar-SA"),
            "content_version": str(payload.get("content_version", "1")),
        },
        actor_id=actor.id if actor else None
    )
    return {
        "task_id": task.id,
        "status": task.status,
        "poll_url": f"/api/tasks/{task.id}"
    }

@router.post('/evaluate-speech', response_model=SpeechEvaluationResponse)
def evaluate_speech(
    req: SpeechEvaluationRequest,
    db: Session = Depends(get_db),
    actor: Principal = Depends(get_optional_user)
):
    """
    Evaluates student pronunciation against curriculum target phrase with MoE phoneme analysis.
    """
    if actor and req.child_id:
        optional_child(db, actor, req.child_id)
    return service.evaluate_pronunciation(req, db=db)

@router.get('/cache/{filename}')
def get_cached_audio(filename: str, actor=Depends(get_optional_user)):
    """Serve pre-generated curriculum audio files with S3/CDN redirection."""
    root = Path(__import__('os').getenv('FAHIM_AUDIO_CACHE_DIR', 'tmp/audio-cache')).resolve()
    target = (root / Path(filename).name).resolve()
    if target.parent == root and target.is_file():
        return FileResponse(target, media_type='audio/mpeg')

    from backend.storage import get_storage_adapter
    storage = get_storage_adapter()
    if storage.file_exists(filename):
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=storage.get_url(filename), status_code=307)

    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail='Audio asset not found')
