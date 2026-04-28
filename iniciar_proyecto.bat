@echo off
setlocal EnableExtensions

cd /d "%~dp0"

set "NO_BUILD=0"
set "RESET_DATA=0"
set "ASSUME_YES=0"
set "PAUSE_ON_EXIT=1"
set "SHOW_HELP=0"
set "EXIT_CODE=0"
if not defined DOCKER_WAIT_ATTEMPTS set "DOCKER_WAIT_ATTEMPTS=40"
if not defined DOCKER_WAIT_SECONDS set "DOCKER_WAIT_SECONDS=3"

:parse_args
if "%~1"=="" goto args_done
if /I "%~1"=="--help" (
    set "SHOW_HELP=1"
    shift
    goto parse_args
)
if /I "%~1"=="-h" (
    set "SHOW_HELP=1"
    shift
    goto parse_args
)
if /I "%~1"=="--no-build" (
    set "NO_BUILD=1"
    shift
    goto parse_args
)
if /I "%~1"=="--reset-data" (
    set "RESET_DATA=1"
    shift
    goto parse_args
)
if /I "%~1"=="--yes" (
    set "ASSUME_YES=1"
    shift
    goto parse_args
)
if /I "%~1"=="--no-pause" (
    set "PAUSE_ON_EXIT=0"
    shift
    goto parse_args
)

echo [ERROR] Opcion no reconocida: %~1
set "EXIT_CODE=1"
goto finish

:args_done
echo.
echo ========================================
echo   Hospital Project - inicio local
echo ========================================
echo.

if "%SHOW_HELP%"=="1" goto usage

where docker >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker no esta instalado o no esta en el PATH.
    echo Instala Docker Desktop y vuelve a ejecutar este script.
    set "EXIT_CODE=1"
    goto finish
)

docker compose version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose no esta disponible.
    echo Actualiza Docker Desktop y vuelve a ejecutar este script.
    set "EXIT_CODE=1"
    goto finish
)

if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [AVISO] Se ha creado .env a partir de .env.example.
        echo Edita .env con secretos reales y vuelve a ejecutar este script.
        set "EXIT_CODE=1"
        goto finish
    )
    echo [ERROR] Falta el archivo .env y no existe .env.example.
    set "EXIT_CODE=1"
    goto finish
)

call :require_env POSTGRES_USER || goto fail
call :require_env POSTGRES_PASSWORD || goto fail
call :require_env POSTGRES_DB || goto fail
call :require_env SECRET_KEY || goto fail
call :require_env ADMIN_USERNAME || goto fail
call :require_env ADMIN_PASSWORD_HASH || goto fail
call :require_env USER_USERNAME || goto fail
call :require_env USER_PASSWORD_HASH || goto fail
call :require_env MINIO_ROOT_USER || goto fail
call :require_env MINIO_ROOT_PASSWORD || goto fail
call :require_env MINIO_BUCKET_NAME || goto fail

findstr /I /C:"replace_with" /C:"change_me" ".env" >nul 2>&1
if not errorlevel 1 (
    echo [ERROR] .env contiene valores de plantilla como replace_with o change_me.
    echo Cambia esos secretos antes de arrancar el proyecto.
    set "EXIT_CODE=1"
    goto finish
)

echo [1/4] Comprobando Docker Desktop...
docker info >nul 2>&1
if errorlevel 1 (
    echo Docker no responde. Intentando abrir Docker Desktop...
    if exist "%ProgramFiles%\Docker\Docker\Docker Desktop.exe" (
        start "" "%ProgramFiles%\Docker\Docker\Docker Desktop.exe"
    )

    for /L %%I in (1,1,%DOCKER_WAIT_ATTEMPTS%) do (
        powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Sleep -Seconds %DOCKER_WAIT_SECONDS%" >nul 2>&1
        docker info >nul 2>&1
        if not errorlevel 1 goto docker_ready
        echo Esperando Docker Desktop... %%I/%DOCKER_WAIT_ATTEMPTS%
    )

    echo [ERROR] No se pudo conectar con Docker.
    echo Abre Docker Desktop manualmente y vuelve a ejecutar este script.
    echo Si Windows muestra "Access is denied", ejecutalo como administrador.
    set "EXIT_CODE=1"
    goto finish
)

:docker_ready
echo [2/4] Validando docker-compose.yml...
docker compose config >nul
if errorlevel 1 (
    echo [ERROR] La configuracion de Docker Compose no es valida.
    set "EXIT_CODE=1"
    goto finish
)

if "%RESET_DATA%"=="1" (
    echo.
    echo [AVISO] --reset-data borrara los volumenes locales de PostgreSQL y MinIO.
    echo Se perderan datos persistidos: tablas, historico, radiografias y objetos.
    if not "%ASSUME_YES%"=="1" (
        choice /C SN /N /M "Confirmas el borrado de volumenes? [S/N] "
        if errorlevel 2 (
            echo Operacion cancelada.
            set "EXIT_CODE=1"
            goto finish
        )
    )
    echo Reinicializando contenedores y volumenes...
    docker compose down -v
    if errorlevel 1 (
        echo [ERROR] No se pudieron borrar los volumenes.
        set "EXIT_CODE=1"
        goto finish
    )
)

if "%NO_BUILD%"=="1" (
    echo [3/4] Arrancando servicios sin reconstruir imagenes...
    docker compose up -d
) else (
    echo [3/4] Construyendo y arrancando servicios...
    docker compose up -d --build
)

if errorlevel 1 (
    echo [ERROR] No se pudo arrancar el proyecto.
    echo.
    echo Estado actual:
    docker compose ps
    echo.
    echo Ultimos logs del backend:
    docker compose logs --tail=60 backend
    echo.
    echo Si el backend indica "password authentication failed" y cambiaste POSTGRES_PASSWORD,
    echo ejecuta: iniciar_proyecto.bat --reset-data
    set "EXIT_CODE=1"
    goto finish
)

echo [4/4] Estado de contenedores:
docker compose ps

echo.
echo Proyecto iniciado.
echo Dashboard: http://localhost:8501
echo Backend:   http://localhost:8000
echo API docs:  http://localhost:8000/docs
echo MinIO:     http://localhost:9001
echo.
echo Comandos utiles:
echo   docker compose logs -f
echo   docker compose --profile pipeline up --build pipeline
echo   docker compose down
echo.
goto finish

:fail
set "EXIT_CODE=1"
goto finish

:require_env
findstr /R /C:"^%~1=." ".env" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Falta %~1 en .env.
    exit /b 1
)
exit /b 0

:usage
echo Uso:
echo   iniciar_proyecto.bat
echo   iniciar_proyecto.bat --no-build
echo   iniciar_proyecto.bat --reset-data
echo.
echo Opciones:
echo   --no-build   Arranca los contenedores sin reconstruir imagenes.
echo   --reset-data Borra volumenes de PostgreSQL/MinIO antes de arrancar.
echo   --yes        Confirma automaticamente --reset-data.
echo   --no-pause   No espera tecla al terminar. Util para terminales/scripts.
echo   --help       Muestra esta ayuda.
goto finish

:finish
if "%PAUSE_ON_EXIT%"=="1" (
    echo.
    pause
)
exit /b %EXIT_CODE%
