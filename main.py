name: Build Android APK

on:
  workflow_dispatch:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install flet flet-cli requests
      - run: flet build apk
      - uses: actions/upload-artifact@v4
        with:
          name: HJ_echanj_APK
          path: build/apk/*.apk
