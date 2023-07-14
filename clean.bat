del /f /s /q build
rmdir /s /q build

del /f /s /q __pycache__
rmdir /s /q __pycache__

del /Q *.pyd
del /Q *.cpp