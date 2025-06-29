@echo off
echo === Lancement de l'application Analyse d'eau ===
cd /d %~dp0
streamlit run app.py
pause