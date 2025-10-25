from setuptools import setup, find_packages

setup(
    name="arc",
    version="0.1.0",
    packages=find_packages(include=["arc", "arc.*"]),
    install_requires=[
        "numpy",
        "pygame",
        "mutagen",
        "pywebview",
        "pyqtwebengine",
        "pyqt5",
        "qtpy",
        "requests",
        "pyaudio",
        "qrcode",
        "pillow",
    ],
    python_requires=">=3.7",
)

