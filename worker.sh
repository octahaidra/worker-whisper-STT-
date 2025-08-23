export RUNPOD_API_KEY=rpa_YEAX9OIM0N4Q6BJKY8ZJ5QFQAKLF78BZJDMUZ2UUmnvn4p
source venv/bin/activate
python src/rp_handler.py --worker --rp_serve_api --rp_api_port 3050 --rp_api_concurrency 1 --rp_api_host 0.0.0.0 --rp_log_level DEBUG

