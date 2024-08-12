import sys
import os

# Add your project dir to the sys.path
sys.path.insert(0,'/home/ouiptcmy/public_html/api.smartmaheshwari.com')

activate_this = '/home/ouiptcmy/public_html/api.smartmaheshwari.com/venv/bin/activate'

with open(activate_this) as file:
    exec(file.read(), dict(__file__=activate_this))
    
from app import app as application