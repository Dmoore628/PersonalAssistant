from setuptools import setup, find_packages

setup(
    name="PersonalAssistant",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "neo4j",
        "pika",
        "pvporcupine",
        "sounddevice",
        "pygetwindow",
        "pyautogui",
        "opencv-python",
        "numpy",
    ],
    entry_points={
        "console_scripts": [
            "start-assistant=services.voice_processing.main:start_hud_overlay",
        ]
    },
    author="Dmoore628",
    description="Archi AI Digital Twin System",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Dmoore628/PersonalAssistant",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)