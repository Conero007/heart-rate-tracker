import cv2
import sys
import numpy as np


def buildGauss(frame, levels):
    pyramid = [frame]
    for _ in range(levels):
        frame = cv2.pyrDown(frame)
        pyramid.append(frame)
    return pyramid


def reconstruct_frame_helper(pyramid, index, levels, videoHeight, videoWidth):
    filteredFrame = pyramid[index]
    for _ in range(levels):
        filteredFrame = cv2.pyrUp(filteredFrame)
    filteredFrame = filteredFrame[:videoHeight, :videoWidth]
    return filteredFrame


def initialize_gaussian_pyramid(
    videoHeight, videoWidth, videoChannels, levels, bufferSize
):
    firstFrame = np.zeros((videoHeight, videoWidth, videoChannels))
    firstGauss = buildGauss(firstFrame, levels + 1)[levels]
    videoGauss = np.zeros(
        (bufferSize, firstGauss.shape[0], firstGauss.shape[1], videoChannels)
    )
    fourierTransformAvg = np.zeros((bufferSize))

    return videoGauss, fourierTransformAvg


def initialize_bandpass_filter(videoFrameRate, bufferSize, maxFrequency, minFrequency):
    frequencies = (1.0 * videoFrameRate) * np.arange(bufferSize) / (1.0 * bufferSize)
    mask = (frequencies >= minFrequency) & (frequencies <= maxFrequency)
    return frequencies, mask


def grab_pulse(
    bufferSize,
    fourierTransform,
    fourierTransformAvg,
    frequencies,
    bpmBuffer,
    bpmBufferSize,
    bpmBufferIndex,
):
    for buf in range(bufferSize):
        fourierTransformAvg[buf] = np.real(fourierTransform[buf]).mean()
    hz = frequencies[np.argmax(fourierTransformAvg)]
    bpm = 60.0 * hz
    bpmBuffer[bpmBufferIndex] = bpm
    bpmBufferIndex = (bpmBufferIndex + 1) % bpmBufferSize
    return bpmBufferIndex


def reconstruct_frame(
    filtered,
    levels,
    videoHeight,
    videoWidth,
    detectionFrame,
    bufferSize,
    frame,
    realHeight,
    realWidth,
    bufferIndex,
):
    filteredFrame = reconstruct_frame_helper(
        filtered, bufferIndex, levels, videoHeight, videoWidth
    )
    outputFrame = detectionFrame + filteredFrame
    outputFrame = cv2.convertScaleAbs(outputFrame)

    bufferIndex = (bufferIndex + 1) % bufferSize

    frame[
        videoHeight // 2 : realHeight - videoHeight // 2,
        videoWidth // 2 : realWidth - videoWidth // 2,
        :,
    ] = outputFrame

    return bufferIndex


def main(webcam):
    # Webcam Parameters
    realWidth = 320 * 2
    realHeight = 240 * 2
    videoWidth = 160 * 2
    videoHeight = 120 * 2
    videoChannels = 3
    videoFrameRate = webcam.get(cv2.CAP_PROP_FPS)
    webcam.set(3, realWidth)
    webcam.set(4, realHeight)

    # Color Magnification Parameters
    levels = 3
    alpha = 170
    minFrequency = 1.0
    maxFrequency = 2.0
    bufferSize = 150
    bufferIndex = 0

    # Output Display Parameters
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 1
    fontColor = (0, 0, 0)
    lineType = 2
    boxColor = (0, 255, 0)
    boxWeight = 3

    # Initialize Gaussian Pyramid
    videoGauss, fourierTransformAvg = initialize_gaussian_pyramid(
        videoHeight, videoWidth, videoChannels, levels, bufferSize
    )

    # Bandpass Filter for Specified Frequencies
    frequencies, mask = initialize_bandpass_filter(
        videoFrameRate, bufferSize, maxFrequency, minFrequency
    )

    # Heart Rate Calculation Variables
    bpmCalculationFrequency = 15
    bpmBufferIndex = 0
    bpmBufferSize = 10
    bpmBuffer = np.zeros((bpmBufferSize))

    frame_count = 0
    while True:
        ret, frame = webcam.read()
        if ret == False:
            break

        detectionFrame = frame[
            videoHeight // 2 : realHeight - videoHeight // 2,
            videoWidth // 2 : realWidth - videoWidth // 2,
            :,
        ]

        # Construct Gaussian Pyramid
        videoGauss[bufferIndex] = buildGauss(detectionFrame, levels + 1)[levels]
        fourierTransform = np.fft.fft(videoGauss, axis=0)

        # Bandpass Filter
        fourierTransform[mask == False] = 0

        # Grab a Pulse
        if bufferIndex % bpmCalculationFrequency == 0:
            frame_count += 1
            bpmBufferIndex = grab_pulse(
                bufferSize,
                fourierTransform,
                fourierTransformAvg,
                frequencies,
                bpmBuffer,
                bpmBufferSize,
                bpmBufferIndex,
            )

        # Amplify
        filtered = np.real(np.fft.ifft(fourierTransform, axis=0))
        filtered = filtered * alpha

        # Reconstruct Resulting Frame
        bufferIndex = reconstruct_frame(
            filtered,
            levels,
            videoHeight,
            videoWidth,
            detectionFrame,
            bufferSize,
            frame,
            realHeight,
            realWidth,
            bufferIndex,
        )

        cv2.rectangle(
            frame,
            (videoWidth // 2, videoHeight // 2),
            (realWidth - videoWidth // 2, realHeight - videoHeight // 2),
            boxColor,
            boxWeight,
        )

        if frame_count > bpmBufferSize:
            text_location = (videoWidth // 2 + 5, 30)
            text = f"BPM: {int(bpmBuffer.mean())}"
        else:
            text_location = (20, 30)
            text = "Calculating BPM..."

        cv2.putText(
            frame,
            text,
            text_location,
            font,
            fontScale,
            fontColor,
            lineType,
        )

        cv2.imshow("Webcam Heart Rate Monitor", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


if __name__ == "__main__":
    webcam = cv2.VideoCapture(0)
    main(webcam)
    webcam.release()
    cv2.destroyAllWindows()
