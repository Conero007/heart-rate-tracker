import sys
import cv2
import numpy as np

# Helper Methods
def buildGauss(frame, levels):
    pyramid = [frame]
    for _ in range(levels):
        frame = cv2.pyrDown(frame)
        pyramid.append(frame)
    return pyramid


def reconstructFrame(pyramid, index, levels):
    filteredFrame = pyramid[index]
    for _ in range(levels):
        filteredFrame = cv2.pyrUp(filteredFrame)
    filteredFrame = filteredFrame[:videoHeight, :videoWidth]
    return filteredFrame


# Webcam Parameters
webcam = None
if len(sys.argv) == 2:
    webcam = cv2.VideoCapture(sys.argv[1])
else:
    webcam = cv2.VideoCapture(0)
realWidth = 320 * 2
realHeight = 240 * 2
videoWidth = 160 * 2
videoHeight = 120 * 2
videoChannels = 3
videoFrameRate = 15
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
loadingTextLocation = (20, 30)
bpmTextLocation = (videoWidth // 2 + 5, 30)
fontScale = 1
fontColor = (255, 255, 255)
lineType = 2
boxColor = (0, 255, 0)
boxWeight = 3

def  initialize_Gaussian_Pyramid():
    firstFrame = np.zeros((videoHeight, videoWidth, videoChannels))
    firstGauss = buildGauss(firstFrame, levels + 1)[levels]
    videoGauss = np.zeros(
        (bufferSize, firstGauss.shape[0], firstGauss.shape[1], videoChannels)
    )
    fourierTransformAvg = np.zeros((bufferSize))

    return videoGauss, fourierTransformAvg

def bandpass_filter():
    frequencies = (1.0 * videoFrameRate) * np.arange(bufferSize) / (1.0 * bufferSize)
    mask = (frequencies >= minFrequency) & (frequencies <= maxFrequency)
    return mask, frequencies

# Heart Rate Calculation Variables
bpmCalculationFrequency = 15
bpmBufferIndex = 0
bpmBufferSize = 10
bpmBuffer = np.zeros((bpmBufferSize))

i = 0
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
    videoGauss, fourierTransformAvg = initialize_Gaussian_Pyramid()
    videoGauss[bufferIndex] = buildGauss(detectionFrame, levels + 1)[levels]
    fourierTransform = np.fft.fft(videoGauss, axis=0)

    # Bandpass Filter
    mask, frequencies = bandpass_filter()
    fourierTransform[mask == False] = 0

    # Grab a Pulse
    if bufferIndex % bpmCalculationFrequency == 0:
        i = i + 1
        for buf in range(bufferSize):
            fourierTransformAvg[buf] = np.real(fourierTransform[buf]).mean()
        hz = frequencies[np.argmax(fourierTransformAvg)]
        bpm = 60.0 * hz
        bpmBuffer[bpmBufferIndex] = bpm
        bpmBufferIndex = (bpmBufferIndex + 1) % bpmBufferSize

    # Amplify
    filtered = np.real(np.fft.ifft(fourierTransform, axis=0))
    filtered = filtered * alpha

    # Reconstruct Resulting Frame
    filteredFrame = reconstructFrame(filtered, bufferIndex, levels)
    outputFrame = detectionFrame + filteredFrame
    outputFrame = cv2.convertScaleAbs(outputFrame)

    bufferIndex = (bufferIndex + 1) % bufferSize

    frame[
        videoHeight // 2 : realHeight - videoHeight // 2,
        videoWidth // 2 : realWidth - videoWidth // 2,
        :,
    ] = outputFrame
    cv2.rectangle(
        frame,
        (videoWidth // 2, videoHeight // 2),
        (realWidth - videoWidth // 2, realHeight - videoHeight // 2),
        boxColor,
        boxWeight,
    )
    if i > bpmBufferSize:
        cv2.putText(
            frame,
            "BPM: %d" % bpmBuffer.mean(),
            bpmTextLocation,
            font,
            fontScale,
            fontColor,
            lineType,
        )
    else:
        cv2.putText(
            frame,
            "Calculating BPM...",
            loadingTextLocation,
            font,
            fontScale,
            fontColor,
            lineType,
        )

    # outputVideoWriter.write(frame)

    if len(sys.argv) != 2:
        cv2.imshow("Webcam Heart Rate Monitor", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

webcam.release()
cv2.destroyAllWindows()
