TALLER CLOUD ECOVISION IA - PRACTICA EN REPOSITORIO EXISTENTE
================================================================

Repositorio del grupo:
https://github.com/stexc7/INGENIERIA-EN-SOFTWARE

IMPORTANTE
----------
- Esta carpeta debe copiarse dentro del repositorio existente.
- NO ejecute git init dentro de esta carpeta.
- La practica es una simulacion local controlada; no representa telemetria real de una nube.

FLUJO RECOMENDADO
-----------------
1. Stephano crea la rama taller-cloud-stephano y agrega esta carpeta con la version estable.
2. Se sube la rama, se crea Pull Request y se integra a main.
3. El segundo integrante crea la rama taller-cloud-incidente desde main.
4. Sustituye app.py por app_fallida.py, registra el cambio, crea Pull Request y lo integra.
5. Ambos ejecutan la version fallida y capturan errores, metricas y logs.
6. Stephano crea la rama taller-cloud-rollback y ejecuta git revert sobre el commit defectuoso.
7. Se integra el rollback y se valida nuevamente el servicio.

PREPARACION LOCAL
-----------------
Desde CMD, dentro de esta carpeta:

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

VERSION ESTABLE
---------------
Terminal 1:
python app.py

Terminal 2:
venv\Scripts\activate
python load_test.py

Abrir:
http://127.0.0.1:5000/health
http://127.0.0.1:5000/dashboard

VERSION FALLIDA
---------------
Detener el servidor con Ctrl+C y ejecutar:
copy /Y app_fallida.py app.py
python app.py

En otra terminal:
venv\Scripts\activate
python load_test.py

Abrir:
http://127.0.0.1:5000/health
http://127.0.0.1:5000/metrics

Logs:
notepad ecovision.log

Metricas:
start metricas.csv

ROLLBACK
--------
El rollback debe realizarse desde una rama nueva, revirtiendo el commit que introdujo app.py defectuoso:

git log --oneline
git revert <HASH_DEL_COMMIT_DEFECTUOSO> --no-edit
git push -u origin taller-cloud-rollback

Despues del merge del Pull Request, ejecutar nuevamente app.py y load_test.py.
El resultado esperado es health=healthy, 30 solicitudes exitosas y 0% de errores.
