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
    py -m PyInstaller --noconfirm --clean build.spec
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
        py -m PyInstaller --noconfirm --clean build.spec
    ) else (
        echo Invalid release type
    )
)