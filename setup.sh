chmod +x builder/download_models.sh
./builder/download_models.sh
python -m venv venv
source venv/bin/activate
pip install -r  builder/requirements.txt
