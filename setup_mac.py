"""
Setup configuration for building Friendly Parakeet as a Mac app.

Run: python setup_mac.py py2app
"""

from setuptools import setup
import os
from pathlib import Path

# Application metadata
APP_NAME = 'Friendly Parakeet'
APP = ['src/parakeet/menubar_app.py']
DATA_FILES = [
    ('assets', ['assets/parakeet_icon.png', 'assets/parakeet_icon.icns']),
    ('assets/sounds', [
        'assets/sounds/budgie_hello.wav',
        'assets/sounds/budgie_alert.wav',
        'assets/sounds/budgie_eureka.wav',
        'assets/sounds/budgie_chirp.wav',
        'assets/sounds/budgie_happy.wav'
    ])
]

OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'assets/parakeet_icon.icns',
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleGetInfoString': "Your friendly coding companion",
        'CFBundleIdentifier': "com.friendlyparakeet.app",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'NSHumanReadableCopyright': "Copyright © 2024, MIT License",
        'LSUIElement': True,  # This makes it a menu bar app without dock icon
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,  # Support dark mode
    },
    'packages': [
        'rumps',
        'git',
        'flask',
        'click',
        'yaml',
        'dateutil',
        'parakeet'
    ],
    'includes': [
        'parakeet.scanner',
        'parakeet.tracker',
        'parakeet.breadcrumbs',
        'parakeet.git_maintenance',
        'parakeet.changelog',
        'parakeet.config',
        'parakeet.dashboard',
        'parakeet.brilliant_budgies',
        'parakeet.parakeet',
    ],
}

setup(
    name=APP_NAME,
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'rumps>=0.4.0',
        'gitpython>=3.1.0',
        'flask>=2.0.0',
        'jinja2>=3.0.0',
        'click>=8.0.0',
        'pyyaml>=6.0',
        'python-dateutil>=2.8.0',
        'pyobjc-core>=9.0',
        'pyobjc-framework-Cocoa>=9.0',
        'pyobjc-framework-AVFoundation>=9.0',
        'plyer>=2.1',
        'pillow>=10.0.0'
    ],
)