[app]
title = YouTube Downloader
package.name = ytdownloader
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,ttf
version = 1.0.0

requirements = 
    python3,
    kivy==2.3.0,
    pytube==15.0.0,
    openssl,
    requests==2.32.3,
    certifi==2024.6.2

android.permissions = 
    INTERNET,
    READ_EXTERNAL_STORAGE,
    WRITE_EXTERNAL_STORAGE

android.api = 34
android.minapi = 26
android.archs = arm64-v8a
android.enable_androidx = True
android.gradle_dependencies = 
    'com.android.tools.build:gradle:8.3.2',
    'androidx.core:core-ktx:1.12.0'

orientation = portrait
fullscreen = 0
icon = assets/icon.png

p4a.branch = develop
android.ignore_setup_py = True
android.allow_backup = False
android.accept_sdk_license = True
log_level = 2
