[app]
title = YouTube Downloader
package.name = ytdownloader
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,ttf
version = 1.0.0
requirements = python3,kivy==2.3.0,pytube==15.0.0,requests,certifi
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
android.api = 34
android.minapi = 26
android.ndk = 25b
android.sdk = 34
android.gradle_dependencies = com.android.tools.build:gradle:8.3.0, androidx.core:core-ktx:1.12.0
android.enable_androidx = True
p4a.branch = develop
osx.python_version = 3
osx.kivy_version = 2.3.0
