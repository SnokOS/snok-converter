# 1. Create the project folder
mkdir snok-converter && cd snok-converter

# 2. Save the six files above into this folder:
#    README.md, LICENSE, install.sh, config.json, snok-settings.py, snok-convert.py

# 3. Make install.sh executable
chmod +x install.sh

# 4. Initialize git and push
git init
git add .
git commit -m "Initial commit: Snok-Converter v2.0 (English)"
git branch -M main
git remote add origin https://github.com/SnokOS/snok-converter.git
git push -u origin main