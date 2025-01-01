// Initialize webcam variables
let videoStream;
let videoElement;
let canvasElement;
let isWebcamActive = false;

// Create elements but don't start stream
function initElements() {
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
  const webcamContainer = document.getElementById("webcam-container");
  const scanButton = document.getElementById("scanButton");
  const webcamStatus = document.getElementById("webcam-status");

  if (!isWebcamActive) {
    try {
      videoStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 320 },
          height: { ideal: 240 },
        },
      });

      // Show the container
      webcamContainer.classList.add("active");

      // Setup video element
      videoElement.srcObject = videoStream;
      videoElement.style.display = "block";
      await videoElement.play();

      // Update state and UI
      isWebcamActive = true;
      scanButton.textContent = "Stop Scan";
      webcamStatus.style.display = "block";

      // Make sure video element is in container
      if (!webcamContainer.contains(videoElement)) {
        webcamContainer.innerHTML = ""; // Clear any existing content
        webcamContainer.appendChild(videoElement);
      }

      console.log("Webcam activated");
    } catch (error) {
      console.error("Error accessing webcam:", error);
      addMessageToChat(
        "Error accessing webcam. Please make sure it's connected and permissions are granted.",
        "bot"
      );
    }
  } else {
    // Stop the webcam
    if (videoStream) {
      videoStream.getTracks().forEach((track) => track.stop());
    }
    videoElement.srcObject = null;
    videoElement.style.display = "none";
    webcamContainer.classList.remove("active");
    isWebcamActive = false;
    scanButton.textContent = "Scan";
    webcamStatus.style.display = "none";
    console.log("Webcam deactivated");
  }
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", function () {
  console.log("Initializing webcam elements");
  initElements();

  // Add click handler to scan button
  const scanButton = document.getElementById("scanButton");
  if (scanButton) {
    console.log("Adding scan button listener");
    scanButton.addEventListener("click", toggleWebcam);
  } else {
    console.error("Scan button not found");
  }
});

// Capture frame and send to server when 'Get Recipe' button is pressed
async function captureAndSendFrame() {
  if (!videoElement.videoWidth) {
    console.error("Video not ready");
    return [];
  }

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

  try {
    const dataURL = canvasElement.toDataURL("image/jpeg", 0.8);
    const response = await fetch("/process_image", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ image_data: dataURL }),
    });

    const data = await response.json();
    if (data.ingredients) {
      return data.ingredients;
    }
  } catch (error) {
    console.error("Error:", error);
  }
  return [];
}

// Update the ingredients list on the page
function updateIngredientsList(ingredients) {
  const ingredientsContainer = document.getElementById("ingredients-list");
  ingredientsContainer.innerHTML = ""; // Clear previous list
  ingredients.forEach((ingredient) => {
    const item = document.createElement("li");
    item.textContent = ingredient;
    ingredientsContainer.appendChild(item);
  });
}

// Send message function
async function sendMessage() {
  const userInput = document.getElementById("user-input").value;
  if (userInput.trim() === "") return;

  addMessageToChat(userInput, "user");

  // Only capture frame if webcam is active
  let ingredients = [];
  if (isWebcamActive) {
    ingredients = await captureAndSendFrame();
  } else {
    addMessageToChat("Please start the webcam scan first!", "bot");
    return;
  }

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: userInput,
        ingredients: ingredients,
      }),
    });

    const data = await response.json();
    if (data.response) {
      addMessageToChat(data.response, "bot");
    } else if (data.error) {
      addMessageToChat("Error: " + data.error, "bot");
    }
  } catch (error) {
    console.error("Error:", error);
    addMessageToChat("An error occurred while processing your request.", "bot");
  }

  document.getElementById("user-input").value = "";
}

// Add message to chat
function addMessageToChat(message, sender) {
  const chatContainer = document.getElementById("chat-container");
  const messageElement = document.createElement("div");
  messageElement.classList.add("message", sender + "-message");
  messageElement.textContent = message;
  chatContainer.appendChild(messageElement);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Event listener for Enter key
document
  .getElementById("user-input")
  .addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
      sendMessage();
    }
  });
