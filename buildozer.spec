[app]
# Основные настройки приложения
title = YouTube Downloader
package.name = ytdownloader
package.domain = org.example
version = 1.0.0

# Настройки исходного кода
source.dir = .
source.include_exts = py,png,jpg,kv,ttf,json

# Зависимости
requirements = 
    python3==3.10.12,
    kivy==2.3.0,
    pytube==15.0.0,
    requests==2.32.3,
    certifi==2024.2.2,
    android

# Android специфичные настройки
android.permissions = 
    INTERNET,
    READ_EXTERNAL_STORAGE,
    WRITE_EXTERNAL_STORAGE

android.api = 34
android.minapi = 26
android.ndk = 25.1.8937393  # Явное указание точной версии NDK
android.sdk = 34
android.gradle_dependencies = 
    com.android.tools.build:gradle:8.3.0,
    androidx.core:core-ktx:1.12.0

android.enable_androidx = True
android.allow_backup = False
android.accept_sdk_license = True  # Автопринятие лицензий

# Настройки сборки
p4a.branch = 2024.05.06  # Стабильная версия python-for-android
log_level = 2  # Детальный лог

[buildozer]
# Оптимизация для CI/CD
build_dir = ./.buildozer
bin_dir = ./bin
