# Heart Rate Tracker using Camera

## Overview

This project is a Python-based application using Flask to implement a camera-based system for heart rate detection, inspired by the research paper [A Remote Photoplethysmography-Based Heart Rate Monitoring System Using a Low-Cost Camera: A Preliminary Study](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7126755/).

## Project Description

The goal of this project is to detect the user's heart rate through a camera, leveraging human skin color changes related to blood circulation, which are imperceptible to the naked eye. The implementation involves spatial and temporal processing of video feeds to amplify subtle facial variations, allowing for accurate heart rate monitoring.

## Features

- **Heart Rate Detection:** The system uses a camera to monitor subtle changes in skin color, allowing for non-intrusive heart rate monitoring.

- **Spatial and Temporal Processing:** Video feeds undergo spatial and temporal processing to enhance the visibility of facial variations associated with blood circulation.

## How it Works

1. **Camera-based Monitoring:** The user places their face in front of the camera, and the system captures video feeds.

2. **Color Changes Detection:** The application analyzes color changes in the skin, particularly those related to blood circulation.

3. **Spatial and Temporal Processing:** The captured video undergoes spatial and temporal processing to amplify subtle facial variations.

4. **Heart Rate Calculation:** The processed video data is used to calculate the user's heart rate.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/heart-rate-tracker.git
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the Flask application:

   ```bash
   python app.py
   ```

   Visit `http://localhost:5000` in your web browser to access the application.

## Usage

- Open the application in a web browser.
- Allow camera access.
- Position your face in front of the camera.
- The application will detect and display your heart rate in real-time.

## References

- Research Paper: [A Remote Photoplethysmography-Based Heart Rate Monitoring System Using a Low-Cost Camera: A Preliminary Study](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7126755/)

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute it as per the license terms.
