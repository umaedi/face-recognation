# Face Recognition System (FastAPI + pgvector + Celery)

Sistem pengenalan wajah performa tinggi dengan fitur **Adaptive Routing** (Realtime/Queued) berdasarkan beban CPU server.

## Fitur Utama
- **Face Identification (1:1)**: Verifikasi wajah terhadap user_id tertentu.
- **Rolling Enrollment**: Maksimal 3 wajah per user (FIFO).
- **Adaptive Routing**: Otomatis pindah ke mode antrean jika CPU > 60%.
- **Vector Search**: Menggunakan PostgreSQL `pgvector` untuk pencarian embedding 512-dimensi.
- **Async Architecture**: Dibangun dengan FastAPI, SQLAlchemy Async, dan Celery.

## Prasyarat
- Python 3.13+
- PostgreSQL dengan ekstensi `pgvector`
- Redis (Rekomendasi: Upstash untuk cloud)

## Cara Instalasi
1. Clone repositori ini.
2. Buat Virtual Environment: `python -m venv venv`
3. Aktifkan venv: `source venv/bin/activate`
4. Install dependensi: `pip install -r requirements.txt`
5. Konfigurasi `.env` (sesuaikan dengan database dan redis Anda).
6. Jalankan migrasi: `alembic upgrade head`

## Cara Menjalankan
Gunakan 3 terminal terpisah:

**Terminal 1 (API Server):**
```bash
uvicorn app.main:app --reload
```

**Terminal 2 (Celery Worker):**
```bash
celery -A app.tasks.celery_app worker -Q recognition --loglevel=info
```

**Terminal 3 (Monitoring Dashboard - Optional):**
```bash
./run_monitoring.sh
```

## Endpoint Utama
- `POST /faces/enroll`: Mendaftarkan wajah baru (Form-data: `user_id`, `image`).
- `GET /faces/{user_id}`: List wajah terdaftar untuk user tersebut.
- `POST /recognize`: Melakukan verifikasi wajah (Form-data: `user_id`, `image`).
- `GET /jobs/{job_id}`: Mengecek hasil proses jika masuk antrean.

## Catatan Server Shared
Sistem ini dikonfigurasi dengan `worker_concurrency=4` untuk menjaga agar tidak memonopoli CPU pada lingkungan server bersama.
