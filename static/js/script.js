document.addEventListener("DOMContentLoaded", function () {
  const input = document.getElementById("mediaInput");
  const videoPlayer = document.getElementById("videoPlayer");
  const uploadedImage = document.getElementById("uploadedImage");
  const framesContainer = document.getElementById("framesContainer");
  const annotatedContainer = document.getElementById("annotatedContainer");
  const fileNameDisplay = document.getElementById("fileNameDisplay");
  const detectionSummary = document.getElementById("detectionSummary");

  const extractedSection = document.getElementById("extractedSection");
  const annotatedSection = document.getElementById("annotatedSection");
  const sectionTitle = document.getElementById("sectionTitle");
  const annotatedSectionTitle = document.getElementById("annotatedSectionTitle");

  const statusSection = document.getElementById("statusSection");
  const progressBar = document.getElementById("progressBar");
  const statusMessage = document.getElementById("statusMessage");

  const zoomModal = document.createElement("div");
  zoomModal.id = "zoomModal";
  zoomModal.innerHTML = `
    <div class="zoom-modal-content">
      <span class="zoom-close">&times;</span>
      <img id="zoomModalImg" src="" />
    </div>
  `;
  document.body.appendChild(zoomModal);

  const zoomModalImg = document.getElementById("zoomModalImg");
  const closeBtn = zoomModal.querySelector(".zoom-close");

  closeBtn.onclick = () => {
    zoomModal.style.display = "none";
    zoomModalImg.src = "";
  };

  function addClickZoom(imgElement) {
    imgElement.addEventListener("click", () => {
      zoomModalImg.src = imgElement.src;
      zoomModal.style.display = "flex";
    });
  }

  input.addEventListener("change", function () {
    const file = input.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("media", file);

    videoPlayer.hidden = true;
    uploadedImage.hidden = true;
    videoPlayer.src = "";
    uploadedImage.src = "";
    framesContainer.innerHTML = "";
    annotatedContainer.innerHTML = "";
    fileNameDisplay.textContent = "";
    detectionSummary.textContent = "";

    sectionTitle.textContent = "";
    annotatedSectionTitle.textContent = "";
    extractedSection.style.display = "none";
    annotatedSection.style.display = "none";

    statusSection.style.display = "block";
    progressBar.value = 10;
    statusMessage.textContent = "Uploading and processing...";

    fetch("/upload", {
      method: "POST",
      body: formData,
    })
      .then(async (res) => {
        let data;
        try {
          data = await res.json();
        } catch (jsonErr) {
          throw new Error("Server returned an unexpected response (not JSON). Possible crash or misroute.");
        }

        if (!res.ok) throw new Error(data.error || "Upload failed.");
        return data;
      })
      .then((data) => {
        progressBar.value = 70;
        const { filename, frameUrls, mediaUrl, annotatedFrameUrls, summary } = data;
        const ext = filename.split(".").pop().toLowerCase();
        const urlWithTimestamp = `${mediaUrl}?t=${Date.now()}`;

        const previewBox = document.querySelector(".video-preview-box");
        previewBox.style.display = "flex";

        if (["mp4", "avi", "mov", "mkv", "webm"].includes(ext)) {
          videoPlayer.src = urlWithTimestamp;
          videoPlayer.hidden = false;
        } else if (["jpg", "jpeg", "png", "webp"].includes(ext)) {
          uploadedImage.src = urlWithTimestamp;
          uploadedImage.hidden = false;
        }

        fileNameDisplay.textContent = `Uploaded: ${filename}`;

        if (summary) {
          detectionSummary.textContent = summary;
          detectionSummary.style.display = "block";
        } else {
          detectionSummary.style.display = "none";
        }

        const detectedSet = new Set(
          annotatedFrameUrls.map(url => url.split("/").pop().split("?")[0])
        );

        if (frameUrls.length > 0) {
          extractedSection.style.display = "block";
          sectionTitle.textContent = "EXTRACTED FRAMES";
          framesContainer.innerHTML = "";

          frameUrls.forEach((src, index) => {
            const wrapper = document.createElement("div");
            wrapper.classList.add("frame-wrapper");

            const img = document.createElement("img");
            img.src = `${src}?t=${Date.now()}`;
            img.classList.add("frame-preview");

            const filenameOnly = src.split("/").pop().split("?")[0];
            if (detectedSet.has(filenameOnly)) {
              img.classList.add("highlighted");
            }

            addClickZoom(img);

            const label = document.createElement("div");
            label.className = "frame-label";
            label.textContent = `Frame ${index + 1}`;

            wrapper.appendChild(img);
            wrapper.appendChild(label);
            framesContainer.appendChild(wrapper);
          });
        } else {
          framesContainer.textContent = "No frames extracted.";
        }

        if (annotatedFrameUrls && annotatedFrameUrls.length > 0) {
          annotatedSection.style.display = "block";
          annotatedSectionTitle.textContent = "DETECTED DRONES";
          annotatedContainer.innerHTML = "";

          annotatedFrameUrls.forEach((src, index) => {
            const wrapper = document.createElement("div");
            wrapper.classList.add("frame-wrapper");

            const img = document.createElement("img");
            img.src = `${src}?t=${Date.now()}`;
            img.classList.add("frame-preview");
            addClickZoom(img);

            const label = document.createElement("div");
            label.className = "frame-label";
            label.textContent = `Frame ${index + 1}`;

            wrapper.appendChild(img);
            wrapper.appendChild(label);
            annotatedContainer.appendChild(wrapper);
          });
        } else {
          annotatedContainer.textContent = "No detections.";
        }

        progressBar.value = 100;
        statusMessage.textContent = "✅ Completed";
        setTimeout(() => {
          statusSection.style.display = "none";
        }, 1500);
      })
      .catch((err) => {
        console.error("Error:", err.message);
        fileNameDisplay.textContent = `❌ ${err.message}`;
        detectionSummary.style.display = "none";
        statusMessage.textContent = "❌ Error during processing";
        progressBar.value = 0;
      });
  });
});
