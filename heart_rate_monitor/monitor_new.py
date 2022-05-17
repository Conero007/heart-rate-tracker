import cv2
import numpy as np


class Monitor:
    def __init__(self, webcam=None) -> None:
        self.frame_count = 0

        if webcam:
            self.webcam = webcam
            self.setup()
        else:
            raise ValueError("cv2.VideoCapture object not provided")

    def setup(self) -> None:
        # Setup Required Parameters
        self.setup_webcam_parameters()
        self.output_display_parameters()
        self.color_magnification_parameters()
        self.heart_rate_calculation_parameters()

        # Initialize Gaussian filtered
        self.initialize_gaussian_filtered()

        # Bandpass Filter for Specified Frequencies
        self.initialize_bandpass_filter()

    def heart_rate_calculation_parameters(self):
        self.bpm_calculation_frequency = 15
        self.bpm_buffer_index = 0
        self.bpm_buffer_size = 10
        self.bpm_buffer = np.zeros((self.bpm_buffer_size))

    def output_display_parameters(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 1
        self.font_color = (0, 0, 0)
        self.line_type = 2
        self.box_color = (0, 255, 0)
        self.box_weight = 3

    def color_magnification_parameters(self):
        self.levels = 3
        self.alpha = 170
        self.min_frequency = 1.0
        self.max_frequency = 2.0
        self.buffer_size = 150
        self.buffer_index = 0

    def setup_webcam_parameters(self):
        self.real_width = 320
        self.real_height = 240
        self.video_width = 160
        self.video_height = 120
        self.video_channels = 3
        self.video_frame_rate = self.webcam.get(cv2.CAP_PROP_FPS)
        self.webcam.set(3, self.real_width)
        self.webcam.set(4, self.real_height)

    def buildGauss(self, frame):
        filtered = [frame]
        for _ in range(self.levels + 1):
            frame = cv2.pyrDown(frame)
            filtered.append(frame)
        return filtered

    def initialize_gaussian_filtered(self):
        firstFrame = np.zeros(
            (self.video_height, self.video_width, self.video_channels)
        )
        firstGauss = self.buildGauss(firstFrame)[self.levels]
        self.videoGauss = np.zeros(
            (
                self.buffer_size,
                firstGauss.shape[0],
                firstGauss.shape[1],
                self.video_channels,
            )
        )
        self.fourierTransformAvg = np.zeros((self.buffer_size))

    def initialize_bandpass_filter(self):
        self.frequencies = (
            (1.0 * self.video_frame_rate)
            * np.arange(self.buffer_size)
            / (1.0 * self.buffer_size)
        )
        self.mask = (self.frequencies >= self.min_frequency) & (
            self.frequencies <= self.max_frequency
        )

    def grab_pulse(self, fourierTransform):
        for buf in range(self.buffer_size):
            self.fourierTransformAvg[buf] = np.real(fourierTransform[buf]).mean()
        hz = self.frequencies[np.argmax(self.fourierTransformAvg)]
        bpm = 60.0 * hz
        self.bpm_buffer[self.bpm_buffer_index] = bpm
        self.bpm_buffer_index = (self.bpm_buffer_index + 1) % self.bpm_buffer_size

    def reconstruct_frame_helper(self, filtered):
        filteredFrame = filtered[self.buffer_index]
        for _ in range(self.levels):
            filteredFrame = cv2.pyrUp(filteredFrame)
        filteredFrame = filteredFrame[: self.video_height, : self.video_width]
        return filteredFrame

    def reconstruct_frame(self, filtered, detectionFrame, frame):
        filteredFrame = self.reconstruct_frame_helper(filtered)
        outputFrame = detectionFrame + filteredFrame
        outputFrame = cv2.convertScaleAbs(outputFrame)

        self.buffer_index = (self.buffer_index + 1) % self.buffer_size

        frame[
            self.video_height // 2 : self.real_height - self.video_height // 2,
            self.video_width // 2 : self.real_width - self.video_width // 2,
            :,
        ] = outputFrame

    def draw_on_frame(self, frame):
        cv2.rectangle(
            frame,
            (self.video_width // 2, self.video_height // 2),
            (
                self.real_width - self.video_width // 2,
                self.real_height - self.video_height // 2,
            ),
            self.box_color,
            self.box_weight,
        )

        if self.frame_count > self.bpm_buffer_size:
            text_location = (self.video_width // 2 + 5, 30)
            text = f"BPM: {int(self.bpm_buffer.mean())}"
        else:
            text_location = (20, 30)
            text = "Calculating BPM..."

        cv2.putText(
            frame,
            text,
            text_location,
            self.font,
            self.font_scale,
            self.font_color,
            self.line_type,
        )

    def run(self):
        while True:
            ret, frame = self.webcam.read()
            if ret == False:
                break

            frame = self.get_processed_frame(frame)
            cv2.imshow("self.Webcam Heart Rate Monitor", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    def get_processed_frame(self, frame):
        detectionFrame = frame[
            self.video_height // 2 : self.real_height - self.video_height // 2,
            self.video_width // 2 : self.real_width - self.video_width // 2,
            :,
        ]

        # Construct Gaussian filtered
        self.videoGauss[self.buffer_index] = self.buildGauss(detectionFrame)[
            self.levels
        ]
        fourierTransform = np.fft.fft(self.videoGauss, axis=0)

        # Bandpass Filter
        fourierTransform[self.mask == False] = 0

        # Grab a Pulse
        if self.buffer_index % self.bpm_calculation_frequency == 0:
            self.frame_count += 1
            self.grab_pulse(fourierTransform)

        # Amplify
        filtered = np.real(np.fft.ifft(fourierTransform, axis=0))
        filtered = filtered * self.alpha

        # Reconstruct Resulting Frame
        self.reconstruct_frame(filtered, detectionFrame, frame)

        # Draw on Frame
        self.draw_on_frame(frame)

        return frame


if __name__ == "__main__":
    webcam = cv2.VideoCapture(0)
    monitor = Monitor(webcam)
    monitor.run()
    webcam.release()
    cv2.destroyAllWindows()
