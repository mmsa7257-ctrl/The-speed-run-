[app]
title = The Speed Run
package.name = thespeedrun
package.domain = org.mnr
source.dir = .
source.include_exts = py,png,jpg,ttf
version = 1.0
requirements = python3,kivy,pygame,numpy
orientation = landscape
fullscreen = 1
android.archs = arm64-v8a
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1
