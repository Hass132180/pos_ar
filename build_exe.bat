@echo off
title Samir POS Builder (Python 3.8)

echo ========================================
echo   بناء ملف EXE لنظام نقاط البيع
echo   Samir Auto Parts POS System
echo ========================================
echo.

REM --- 1) التحقق من وجود Python 3.8 ---
echo [1/6] التحقق من Python 3.8...
py -3.8 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [خطأ] Python 3.8 غير مثبت!
    echo يرجى تثبيت Python 3.8 أولاً.
    pause
    exit /b 1
)
for /f "delims=" %%v in ('py -3.8 --version') do set PYVER=%%v
echo [✓] Python متوفر: %PYVER%
echo.

REM --- 2) تثبيت PyInstaller ---
echo [2/6] تثبيت PyInstaller...
py -3.8 -m pip install pyinstaller --quiet
if %errorlevel% neq 0 (
    echo [خطأ] فشل تثبيت PyInstaller
    pause
    exit /b 1
)
echo [✓] PyInstaller مثبت
py -3.8 -m PyInstaller --version
echo.

REM --- 3) تثبيت المتطلبات ---
echo [3/6] التحقق من المتطلبات...
if not exist requirements.txt (
    echo [تحذير] ملف requirements.txt غير موجود! سيتم المتابعة بدون تثبيت إضافي.
) else (
    py -3.8 -m pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo [خطأ] فشل تثبيت المتطلبات
        pause
        exit /b 1
    )
    echo [✓] جميع المتطلبات مثبتة
)
echo.

REM --- 4) التأكد من وجود ملف SPEC ---
echo [4/6] التحقق من ملف build_exe.spec...
if not exist build_exe.spec (
    echo [خطأ] ملف build_exe.spec غير موجود!
    echo يجب إنشاء SPEC أولاً عبر:
    echo py -3.8 -m PyInstaller main.py
    pause
    exit /b 1
)
echo [✓] الملف موجود
echo.

REM --- 5) تنظيف البناء القديم ---
echo [5/6] تنظيف الملفات القديمة...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
echo [✓] تم التنظيف
echo.

REM --- 6) البدء في إنشاء ملف EXE ---
echo [6/6] بناء ملف EXE...
echo بدأ البناء في: %date% - %time%
echo قد يستغرق ذلك عدة دقائق...
echo.

py -3.8 -m PyInstaller build_exe.spec --clean --noconfirm

if %errorlevel% neq 0 (
    echo.
    echo [خطأ] فشل بناء ملف EXE
    pause
    exit /b 1
)

echo.
echo ========================================
echo [✓✓✓] تم بناء ملف EXE بنجاح!
echo ========================================
echo.
echo الملف الناتج: dist\SamirPOS.exe
echo وقت الانتهاء: %date% - %time%
echo.
echo ملاحظات:
echo - الملف جاهز للنقل دون مشاكل
echo - يتم إنشاء قاعدة البيانات تلقائياً
echo - المستخدم الافتراضي: admin / admin123456
echo - لا تحذف ملف pos_system.db بعد إنشائه!
echo.

explorer dist
pause
