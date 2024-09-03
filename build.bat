@ECHO OFF

set "release_type=%1"

if "%release_type%"=="--debug" (
    if exist build\ (
        del /S /Q build\\*
        rmdir /S /Q build
    )
    if exist dist\ (
        del /S /Q dist\\*
        rmdir /S /Q dist
    )

    echo debug> release_type.txt
    python -m PyInstaller --noconfirm --clean build.spec
    del release_type.txt
) else (
    if "%release_type%"=="--release" (
        if exist build\ (
            del /S /Q build\\*
            rmdir /S /Q build
        )
        if exist dist\ (
            del /S /Q dist\\*
            rmdir /S /Q dist
        )

        echo release> release_type.txt
        python -m PyInstaller --noconfirm --clean build.spec
        del release_type.txt
    ) else (
        echo Invalid release type
    )
)