// Initialize webcam variables
let videoStream;
let videoElement;
let canvasElement;
let isWebcamActive = false;

// Create elements but don't start stream
function initElements() {
  console.log("Initializing elements");
  videoElement = document.createElement("video");
  videoElement.setAttribute("width", "320");
  videoElement.setAttribute("height", "240");
  videoElement.setAttribute("autoplay", "");
  videoElement.setAttribute("playsinline", "");

  canvasElement = document.createElement("canvas");
  canvasElement.width = 320;
  canvasElement.height = 240;
}

// Handle scan button click
async function toggleWebcam() {
  console.log("Toggle webcam called");
  const webcamContainer = document.getElementById("webcam-container");
  const scanButton = document.getElementById("scanButton");
  const webcamStatus = document.getElementById("webcam-status");

  if (!isWebcamActive) {
    console.log("Attempting to activate webcam");
    try {
      videoStream = await navigator.mediaDevices.getUserMedia({
        video: true,
      });
      console.log("Got video stream");

      webcamContainer.innerHTML = "";
      webcamContainer.appendChild(videoElement);
      webcamContainer.style.display = "block";

      videoElement.srcObject = videoStream;
      videoElement.style.display = "block";

      await videoElement.play();

      isWebcamActive = true;
      scanButton.textContent = "Stop Scan";
      webcamStatus.style.display = "block";
    } catch (error) {
      console.error("Error accessing webcam:", error);
    }
  } else {
    console.log("Deactivating webcam");
    if (videoStream) {
      videoStream.getTracks().forEach((track) => track.stop());
    }
    videoElement.srcObject = null;
    videoElement.style.display = "none";
    webcamContainer.style.display = "none";
    isWebcamActive = false;
    scanButton.textContent = "Start Scan";
    webcamStatus.style.display = "none";
  }
}

// Capture and process image
async function getIngredients() {
  if (!isWebcamActive) {
    alert("Please start the webcam first!");
    return;
  }

  try {
    // Capture frame
    canvasElement.width = videoElement.videoWidth;
    canvasElement.height = videoElement.videoHeight;
    const context = canvasElement.getContext("2d");
    context.drawImage(
      videoElement,
      0,
      0,
      canvasElement.width,
      canvasElement.height
    );

    // Convert to base64
    const dataURL = canvasElement.toDataURL("image/jpeg", 0.8);

    // Send to server
    const response = await fetch("/process_image", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ image_data: dataURL }),
    });

    const data = await response.json();

    if (data.ingredients) {
      // Display ingredients
      const ingredientsList = document.getElementById("ingredients-list");
      ingredientsList.innerHTML = data.ingredients.join(", ");
      document.getElementById("results-container").style.display = "block";
    }
  } catch (error) {
    console.error("Error processing image:", error);
    alert("Error processing image. Please try again.");
  }
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", function () {
  console.log("DOM Content Loaded");
  initElements();

  // Add scan button listener
  const scanButton = document.getElementById("scanButton");
  if (scanButton) {
    scanButton.addEventListener("click", toggleWebcam);
  }

  // Add get ingredients button listener
  const getIngredientsButton = document.getElementById("getIngredientsButton");
  if (getIngredientsButton) {
    getIngredientsButton.addEventListener("click", getIngredients);
  }
});
