import time
import os
from app.celery_app import celery
from app.db.database import SessionLocal
from app.db import models

ARTIFACTS_DIR = os.getenv('ARTIFACTS_DIR', '/code/app/static/artifacts')

@celery.task(name='app.tasks.process_build')
def process_build(build_id: int):
    db = SessionLocal()
    try:
        build = db.query(models.Build).filter(models.Build.id == build_id).first()
        if not build:
            return {'error': 'build not found'}
        build.status = 'running'
        db.commit()

        # Simulate build work
        time.sleep(5)  # in real world this runs the actual build pipeline

        # Ensure artifacts dir exists
        os.makedirs(ARTIFACTS_DIR, exist_ok=True)
        artifact_path = os.path.join(ARTIFACTS_DIR, f'build_{build_id}.apk')
        with open(artifact_path, 'wb') as f:
            f.write(b'\n'.join([b'M1 OS Nexus APK placeholder', f'build_id={build_id}'.encode()]))

        # Update build record
        build.status = 'success'
        # In production this would be an S3 URL or CDN path
        build.output_url = f"/artifacts/build_{build_id}.apk"
        db.commit()
        return {'status': 'success', 'output_url': build.output_url}
    except Exception as e:
        db.rollback()
        if 'build' in locals() and build:
            build.status = 'failed'
            db.commit()
        return {'status': 'failed', 'error': str(e)}
    finally:
        db.close()
