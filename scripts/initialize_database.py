"""Initialize and seed a hosted instance without making an administrator account."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import create_app
from scripts.seed_iso_course import seed
app=create_app()
seed(app.config['DATABASE'])
