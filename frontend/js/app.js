/* =========================================================
   Palm Mitra - Frontend JavaScript
   Connects HTML frontend to FastAPI backend
   ========================================================= */

const API_URL = "https://palm-mitra-2-0.onrender.com";


/* =========================
   AUTHENTICATION CHECK
========================= */

const token = localStorage.getItem("palmMitraToken");

if (!token) {
    window.location.href = "login.html";
}

async function verifyLogin() {

    try {

        const response = await fetch(
            `${API_URL}/api/auth/me`,
            {
                method: "GET",

                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        if (!response.ok) {

            localStorage.removeItem("palmMitraToken");
            localStorage.removeItem("palmMitraUser");

            window.location.href = "login.html";

            return null;
        }

        const data = await response.json();

        return data.user;

    } catch (error) {

        console.error(
            "Authentication verification failed:",
            error
        );

        return null;
    }
}

/* =========================================================
   Get HTML Elements
   ========================================================= */

const uploadArea = document.getElementById("uploadArea");
const leafInput = document.getElementById("leafInput");
const chooseButton = document.getElementById("chooseButton");

const fileName = document.getElementById("fileName");

const previewContainer =
    document.getElementById("previewContainer");

const imagePreview =
    document.getElementById("imagePreview");

const analyzeButton =
    document.getElementById("analyzeButton");
// =====================================================
// CAMERA SCAN ELEMENTS
// =====================================================

const scanButton = document.getElementById("scanButton");
const cameraContainer = document.getElementById("cameraContainer");
const cameraPreview = document.getElementById("cameraPreview");
const captureButton = document.getElementById("captureButton");
const closeCameraButton = document.getElementById("closeCameraButton");
const cameraCanvas = document.getElementById("cameraCanvas");

let cameraStream = null;

const loading =
    document.getElementById("loading");

const result =
    document.getElementById("result");

const errorBox =
    document.getElementById("error");

const errorMessage =
    document.getElementById("errorMessage");

const screeningResult =
    document.getElementById("screeningResult");

const confidenceResult =
    document.getElementById("confidenceResult");

const nutrientResult =
    document.getElementById("nutrientResult");

const statusResult =
    document.getElementById("statusResult");

const analysisMessage =
    document.getElementById("analysisMessage");

const priorityResult =
    document.getElementById("priorityResult");

const recommendationSummary =
    document.getElementById("recommendationSummary");

const recommendationActions =
    document.getElementById("recommendationActions");

const nextStep =
    document.getElementById("nextStep");
/* =========================================================
   WEATHER ELEMENTS
   ========================================================= */

const weatherLocation =
    document.getElementById("weatherLocation");

const weatherTemperature =
    document.getElementById("weatherTemperature");

const weatherFeelsLike =
    document.getElementById("weatherFeelsLike");

const weatherCondition =
    document.getElementById("weatherCondition");

const weatherHumidity =
    document.getElementById("weatherHumidity");

const weatherWind =
    document.getElementById("weatherWind");

const weatherCloudiness =
    document.getElementById("weatherCloudiness");

const weatherIcon =
    document.getElementById("weatherIcon");

const weatherLoading =
    document.getElementById("weatherLoading");

const weatherError =
    document.getElementById("weatherError");

const refreshWeatherButton =
    document.getElementById("refreshWeatherButton");

const irrigationAdvice =
    document.getElementById("irrigationAdvice");

const irrigationReason =
    document.getElementById("irrigationReason");

const irrigationActions =
    document.getElementById("irrigationActions");

/* =========================================================
   Selected File
   ========================================================= */

let selectedFile = null;


/* =========================================================
   Choose Image Button
   ========================================================= */

chooseButton.addEventListener("click", function () {
    leafInput.click();
});


/* =========================================================
   File Selected
   ========================================================= */

leafInput.addEventListener("change", function () {

    const file = leafInput.files[0];

    if (!file) {
        return;
    }

    handleSelectedFile(file);
});


/* =========================================================
   Drag and Drop
   ========================================================= */

uploadArea.addEventListener("dragover", function (event) {

    event.preventDefault();

    uploadArea.classList.add("dragover");
});


uploadArea.addEventListener("dragleave", function () {

    uploadArea.classList.remove("dragover");
});


uploadArea.addEventListener("drop", function (event) {

    event.preventDefault();

    uploadArea.classList.remove("dragover");

    const file = event.dataTransfer.files[0];

    if (!file) {
        return;
    }

    handleSelectedFile(file);
});


/* =========================================================
   Handle Selected File
   ========================================================= */

function handleSelectedFile(file) {

    hideError();

    const allowedTypes = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ];

    if (!allowedTypes.includes(file.type)) {

        showError(
            "Invalid image format. Please select a JPG, PNG or WEBP image."
        );

        return;
    }

    selectedFile = file;

    fileName.textContent =
        `Selected: ${file.name}`;

    const reader = new FileReader();

    reader.onload = function (event) {

        imagePreview.src =
            event.target.result;

        previewContainer.classList.remove("hidden");
    };

    reader.readAsDataURL(file);

    analyzeButton.disabled = false;

    result.classList.add("hidden");
}

// =====================================================
// CAMERA SCAN
// =====================================================

// Open camera
scanButton.addEventListener("click", async function () {

    hideError();

    cameraContainer.classList.remove("hidden");

    try {

        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: {
                    ideal: "environment"
                }
            },
            audio: false
        });

        cameraPreview.srcObject = cameraStream;

    } catch (error) {

        console.error("Camera access error:", error);

        cameraContainer.classList.add("hidden");

        showError(
            "Unable to access the camera. Please allow camera permission and try again."
        );
    }
});


// =====================================================
// CAPTURE IMAGE
// =====================================================

captureButton.addEventListener("click", function () {

    if (!cameraStream) {

        showError("Camera is not active.");

        return;
    }


    if (
        !cameraPreview.videoWidth ||
        !cameraPreview.videoHeight
    ) {

        showError(
            "Camera is not ready yet. Please wait a moment."
        );

        return;
    }


    const width = cameraPreview.videoWidth;
    const height = cameraPreview.videoHeight;


    cameraCanvas.width = width;
    cameraCanvas.height = height;


    const context = cameraCanvas.getContext("2d");


    context.drawImage(
        cameraPreview,
        0,
        0,
        width,
        height
    );


    cameraCanvas.toBlob(
        function (blob) {

            if (!blob) {

                showError(
                    "Could not capture the image. Please try again."
                );

                return;
            }


            const capturedFile = new File(
                [blob],
                "palm_leaf_scan.jpg",
                {
                    type: "image/jpeg"
                }
            );


            // Send the captured image through
            // the EXISTING image-selection pipeline.
            handleSelectedFile(capturedFile);


            // Stop camera
            stopCamera();


            // Hide camera
            cameraContainer.classList.add("hidden");

        },
        "image/jpeg",
        0.92
    );

});


// =====================================================
// CLOSE CAMERA
// =====================================================

closeCameraButton.addEventListener("click", function () {

    stopCamera();

    cameraContainer.classList.add("hidden");

});


// =====================================================
// STOP CAMERA
// =====================================================

function stopCamera() {

    if (cameraStream) {

        cameraStream
            .getTracks()
            .forEach(function (track) {

                track.stop();

            });

        cameraStream = null;
    }


    cameraPreview.srcObject = null;
}


// Stop camera if page is closed/refreshed
window.addEventListener("beforeunload", function () {

    stopCamera();

});

/* =========================================================
   Analyze Button
   ========================================================= */

analyzeButton.addEventListener(
    "click",
    analyzeLeaf
);


/* =========================================================
   Analyze Leaf
   ========================================================= */

async function analyzeLeaf() {

    if (!selectedFile) {

        showError(
            "Please select an oil-palm leaf image first."
        );

        return;
    }

    hideError();

    result.classList.add("hidden");

    loading.classList.remove("hidden");

    analyzeButton.disabled = true;

    const formData = new FormData();

    formData.append(
        "file",
        selectedFile
    );

    try {

        const response = await fetch(
            `${API_URL}/api/analyze-leaf`,
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "The server could not analyze the image."
            );
        }

        displayResult(data);

    } catch (error) {

        console.error(
            "Palm Mitra API Error:",
            error
        );

        showError(
            getFriendlyErrorMessage(error)
        );

    } finally {

        loading.classList.add("hidden");

        analyzeButton.disabled = false;
    }
}


/* =========================================================
   Display Backend Result
   ========================================================= */

function displayResult(data) {

    const analysis =
        data.result.analysis;

    const recommendation =
        data.result.recommendation;


    /* -----------------------------------------
       Screening
       ----------------------------------------- */

    const screening =
        analysis.screening;

    screeningResult.textContent =
        formatScreening(screening);


    /* -----------------------------------------
       Confidence
       ----------------------------------------- */

    if (
        screening &&
        typeof screening.confidence === "number"
    ) {

        confidenceResult.textContent =
            `${(
                screening.confidence * 100
            ).toFixed(2)}%`;

    } else {

        confidenceResult.textContent =
            "—";
    }


    /* -----------------------------------------
       Nutrient Detection
       ----------------------------------------- */

    const nutrientDetection =
        analysis.nutrient_detection;

    nutrientResult.textContent =
        formatNutrientResult(
            nutrientDetection
        );


    /* -----------------------------------------
       Overall Status
       ----------------------------------------- */

    statusResult.textContent =
        formatStatus(
            analysis.status
        );


    /* -----------------------------------------
       Analysis Message
       ----------------------------------------- */

    analysisMessage.textContent =
        analysis.message ||
        "No additional analysis message was returned.";


    /* -----------------------------------------
       Recommendation
       ----------------------------------------- */

    if (recommendation) {

        priorityResult.textContent =
            recommendation.priority ||
            "—";

        recommendationSummary.textContent =
            recommendation.summary ||
            "No recommendation summary available.";

        recommendationActions.innerHTML = "";

        const actions =
            recommendation.actions || [];

        actions.forEach(function (action) {

            const li =
                document.createElement("li");

            li.textContent = action;

            recommendationActions.appendChild(li);
        });

        nextStep.textContent =
            recommendation.next_step ||
            "Continue monitoring the palm.";
    }


    /* -----------------------------------------
       Show Result
       ----------------------------------------- */

    result.classList.remove("hidden");

    result.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


/* =========================================================
   Format Screening Result
   ========================================================= */

function formatScreening(screening) {

    if (!screening) {
        return "—";
    }

    const prediction =
        screening.prediction;

    if (prediction === "healthy") {
        return "Healthy";
    }

    if (prediction === "diseased") {
        return "Abnormal";
    }

    return prediction || "—";
}


/* =========================================================
   Format Nutrient Result
   ========================================================= */

function formatNutrientResult(nutrientDetection) {

    if (!nutrientDetection) {
        return "Not available";
    }

    const detections =
        nutrientDetection.detections || [];

    if (detections.length === 0) {

        return "No clear pattern";
    }

    const firstDetection =
        detections[0];

    if (
        firstDetection.class_name
    ) {

        return firstDetection.class_name;
    }

    if (
        firstDetection.name
    ) {

        return firstDetection.name;
    }

    return "Pattern detected";
}


/* =========================================================
   Format Overall Status
   ========================================================= */

function formatStatus(status) {

    if (!status) {
        return "—";
    }

    switch (status) {

        case "healthy":
            return "Healthy";

        case "uncertain":
            return "Uncertain";

        case "problem_detected":
            return "Attention Needed";

        default:
            return status.replaceAll(
                "_",
                " "
            );
    }
}


/* =========================================================
   Error Handling
   ========================================================= */

function showError(message) {

    errorMessage.textContent =
        message;

    errorBox.classList.remove("hidden");

    errorBox.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });
}


function hideError() {

    errorBox.classList.add("hidden");
}


/* =========================================================
   Friendly API Error Messages
   ========================================================= */

function getFriendlyErrorMessage(error) {

    if (
        error.message.includes(
            "Failed to fetch"
        )
    ) {

        return (
            "Palm Mitra could not connect to the backend. " +
            "Please make sure the FastAPI server is running " +
            "at http://127.0.0.1:8000."
        );
    }

    return (
        error.message ||
        "Something went wrong while analyzing the leaf."
    );
}
/* =========================================================
   FARM PROFILE
   ========================================================= */

const farmForm =
    document.getElementById("farmForm");

const farmSaveMessage =
    document.getElementById("farmSaveMessage");


/* =========================================================
   Save Farm Profile
   ========================================================= */

farmForm.addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();

        const farm = {

            name:
                document.getElementById(
                    "farmName"
                ).value.trim(),

            location:
                document.getElementById(
                    "farmLocation"
                ).value.trim(),

            area:
                document.getElementById(
                    "farmArea"
                ).value,

            palms:
                document.getElementById(
                    "palmCount"
                ).value,

            plantationType:
                document.getElementById(
                    "plantationType"
                ).value,

            waterSource:
                document.getElementById(
                    "waterSource"
                ).value,

            irrigation:
                document.getElementById(
                    "irrigationType"
                ).value,

            soil:
                document.getElementById(
                    "soilType"
                ).value,

            plantationDate:
                document.getElementById(
                    "plantationDate"
                ).value
        };


        /* -----------------------------------------
           Basic Validation
           ----------------------------------------- */

        if (
            !farm.name ||
            !farm.location ||
            !farm.area ||
            !farm.palms ||
            !farm.plantationType ||
            !farm.waterSource
        ) {

            farmSaveMessage.textContent =
                "Please fill in the required farm details.";

            return;
        }


        /* -----------------------------------------
           Save Locally For Now
           ----------------------------------------- */

     /* -----------------------------------------
   Save Farm To Database
   ----------------------------------------- */

const token = localStorage.getItem("palmMitraToken");

try {
    const response = await fetch(
        `${API_URL}/api/farm`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(farm)
        }
    );

    const data = await response.json();

    if (!response.ok) {
        console.error(
            "Failed to save farm:",
            data.detail || "Unknown error"
        );
        return;
    }

    console.log(
        "Farm saved successfully:",
        data.farm
    );

} catch (error) {
    console.error(
        "Error saving farm:",
        error
    );
}




        /* -----------------------------------------
           Update Dashboard
           ----------------------------------------- */

        updateFarmDashboard(farm);


        farmSaveMessage.textContent =
            "✓ Farm profile saved successfully.";


        farmSaveMessage.style.color =
            "var(--primary)";
    }
);


/* =========================================================
   Load Existing Farm Profile
   ========================================================= */

async function loadFarmProfile() {

    const token =
        localStorage.getItem("palmMitraToken");

    if (!token) {
        return;
    }

    try {

        const response = await fetch(
            `${API_URL}/api/farm`,
            {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const data = await response.json();

        if (!response.ok) {

            console.error(
                "Could not load farm profile:",
                data.detail || "Unknown error"
            );

            return;
        }

        const farm = data.farm;

        if (!farm) {
            console.log(
                "No farm profile found for this user."
            );
            return;
        }

        document.getElementById(
            "farmName"
        ).value =
            farm.name || "";


        document.getElementById(
            "farmLocation"
        ).value =
            farm.location || "";


        document.getElementById(
            "farmArea"
        ).value =
            farm.area || "";


        document.getElementById(
            "palmCount"
        ).value =
            farm.palms || "";


        document.getElementById(
            "plantationType"
        ).value =
            farm.plantationType || "";


        document.getElementById(
            "waterSource"
        ).value =
            farm.waterSource || "";


        document.getElementById(
            "irrigationType"
        ).value =
            farm.irrigation || "";


        document.getElementById(
            "soilType"
        ).value =
            farm.soil || "";


        document.getElementById(
            "plantationDate"
        ).value =
            farm.plantationDate || "";


        updateFarmDashboard(farm);

    } catch (error) {

        console.error(
            "Could not load farm profile:",
            error
        );
    }
}


/* =========================================================
   Update Dashboard
   ========================================================= */

function updateFarmDashboard(farm) {

    document.getElementById(
        "dashboardArea"
    ).textContent =
        `${farm.area || 0} acres`;


    document.getElementById(
        "dashboardPalms"
    ).textContent =
        farm.palms || "0";


    document.getElementById(
        "dashboardWater"
    ).textContent =
        farm.waterSource || "Not set";


    document.getElementById(
        "dashboardType"
    ).textContent =
        farm.plantationType || "Not set";


    document.getElementById(
        "dashboardLocation"
    ).textContent =
        farm.location || "Not set";


    document.getElementById(
        "dashboardSoil"
    ).textContent =
        farm.soil || "Not set";


    document.getElementById(
        "dashboardIrrigation"
    ).textContent =
        farm.irrigation || "Not set";


    document.getElementById(
        "dashboardDate"
    ).textContent =
        farm.plantationDate || "Not set";


    const statusBadge =
        document.getElementById(
            "farmStatusBadge"
        );


    statusBadge.textContent =
        "Profile configured";


    statusBadge.style.background =
        "#e8f5e9";


    statusBadge.style.color =
        "var(--primary)";
}


/* =========================================================
   Initialize Farm Profile
   ========================================================= */

loadFarmProfile();
loadWeather();
/* =========================================================
   WEATHER
   ========================================================= */

/* =========================================================
   WEATHER
   ========================================================= */

async function loadWeather() {

    const token =
        localStorage.getItem("palmMitraToken");

    if (!token) {
        return;
    }


    /* -----------------------------------------
       Get Farm Profile From Database
       ----------------------------------------- */

    let farm;

    try {

        const farmResponse =
            await fetch(
                `${API_URL}/api/farm`,
                {
                    method: "GET",
                    headers: {
                        "Authorization": `Bearer ${token}`
                    }
                }
            );


        const farmData =
            await farmResponse.json();


        if (!farmResponse.ok) {

            throw new Error(
                farmData.detail ||
                "Could not load farm profile."
            );
        }


        farm =
            farmData.farm;


    } catch (error) {

        console.error(
            "Could not load farm profile for weather:",
            error
        );

        if (weatherError) {

            weatherError.textContent =
                "Could not load your farm profile. Please try again.";

            weatherError.classList.remove(
                "hidden"
            );
        }

        return;
    }


    /* -----------------------------------------
       Check Farm Location
       ----------------------------------------- */

    if (!farm) {

        if (weatherError) {

            weatherError.textContent =
                "Please save your farm profile first.";

            weatherError.classList.remove(
                "hidden"
            );
        }

        return;
    }


    const city =
        farm.location;


    if (!city) {

        if (weatherError) {

            weatherError.textContent =
                "Please add your farm location in My Farm.";

            weatherError.classList.remove(
                "hidden"
            );
        }

        return;
    }


    /* -----------------------------------------
       Loading State
       ----------------------------------------- */

    if (weatherLoading) {
        weatherLoading.classList.remove("hidden");
    }

    if (weatherError) {
        weatherError.classList.add("hidden");
    }


    /* -----------------------------------------
       Get Weather
       ----------------------------------------- */

    try {

        const response =
            await fetch(
                `${API_URL}/api/weather?city=${encodeURIComponent(city)}`
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Could not retrieve weather information."
            );
        }


        displayWeather(
            data.weather
        );


    } catch (error) {

        console.error(
            "Weather API Error:",
            error
        );

        if (weatherError) {

            weatherError.textContent =
                getFriendlyWeatherError(error);

            weatherError.classList.remove(
                "hidden"
            );
        }


    } finally {

        if (weatherLoading) {
            weatherLoading.classList.add("hidden");
        }
    }
}


/* =========================================================
   Display Weather
   ========================================================= */

function displayWeather(weather) {

    if (!weather) {
        return;
    }


    if (weatherLocation) {

        weatherLocation.textContent =
            `${weather.location}, ${weather.country}`;
    }


    if (weatherTemperature) {

        weatherTemperature.textContent =
            weather.temperature !== null &&
            weather.temperature !== undefined
                ? `${weather.temperature.toFixed(1)}°C`
                : "—";
    }


    if (weatherFeelsLike) {

        weatherFeelsLike.textContent =
            weather.feels_like !== null &&
            weather.feels_like !== undefined
                ? `${weather.feels_like.toFixed(1)}°C`
                : "—";
    }


    if (weatherCondition) {

        weatherCondition.textContent =
            weather.description ||
            weather.condition ||
            "Unknown";
    }


    if (weatherHumidity) {

        weatherHumidity.textContent =
            weather.humidity !== null &&
            weather.humidity !== undefined
                ? `${weather.humidity}%`
                : "—";
    }


    if (weatherWind) {

        weatherWind.textContent =
            weather.wind_speed !== null &&
            weather.wind_speed !== undefined
                ? `${weather.wind_speed} m/s`
                : "—";
    }


    if (weatherCloudiness) {

        weatherCloudiness.textContent =
            weather.cloudiness !== null &&
            weather.cloudiness !== undefined
                ? `${weather.cloudiness}%`
                : "—";
    }


    if (
        weatherIcon &&
        weather.icon
    ) {

        weatherIcon.src =
            `https://openweathermap.org/img/wn/${weather.icon}@2x.png`;

        weatherIcon.alt =
            weather.description ||
            "Weather icon";

        weatherIcon.classList.remove(
            "hidden"
        );
    }
    updateIrrigationGuidance(weather);
}

function updateIrrigationGuidance(weather) {

    if (!weather) return;

    const temperature =
        Number(weather.temperature);

    const humidity =
        Number(weather.humidity);

    const cloudiness =
        Number(weather.cloudiness);

    const condition =
        (weather.condition || "").toLowerCase();

    let advice = "";
    let reason = "";
    let actions = [];

    /*
     * Rain/cloud conditions
     */
    if (
        condition.includes("rain") ||
        condition.includes("drizzle") ||
        condition.includes("thunderstorm")
    ) {

        advice =
            "Review irrigation before watering.";

        reason =
            "Rain-related weather is currently present, " +
            "so additional irrigation may not be necessary.";

        actions = [
            "Check soil moisture in the root zone.",
            "Consider recent rainfall before irrigating.",
            "Check that drainage is working properly."
        ];

    /*
     * Very cloudy / humid conditions
     */
    } else if (
        cloudiness >= 80 &&
        humidity >= 70
    ) {

        advice =
            "Check soil moisture before irrigation.";

        reason =
            "The weather is cloudy and humid, so avoid " +
            "irrigating automatically without checking the soil.";

        actions = [
            "Check soil moisture before watering.",
            "Consider recent rainfall.",
            "Monitor drainage around the palms."
        ];

    /*
     * Hot conditions
     */
    } else if (
        temperature >= 32 &&
        humidity < 60
    ) {

        advice =
            "Monitor soil moisture more frequently.";

        reason =
            "Current conditions are relatively hot and less humid, " +
            "so the crop may require closer irrigation monitoring.";

        actions = [
            "Check soil moisture regularly.",
            "Follow your normal irrigation schedule when needed.",
            "Check the root zone for excessive dryness."
        ];

    /*
     * Normal conditions
     */
    } else {

        advice =
            "Follow the normal irrigation schedule.";

        reason =
            "Current weather does not indicate a strong reason " +
            "to change irrigation based on weather alone.";

        actions = [
            "Check soil moisture before irrigation.",
            "Follow your farm's normal irrigation schedule.",
            "Continue monitoring weather and drainage conditions."
        ];
    }

    if (irrigationAdvice) {
        irrigationAdvice.textContent = advice;
    }

    if (irrigationReason) {
        irrigationReason.textContent = reason;
    }

    if (irrigationActions) {

        irrigationActions.innerHTML = "";

        actions.forEach(function(action) {

            const li =
                document.createElement("li");

            li.textContent = action;

            irrigationActions.appendChild(li);
        });
    }
}

/* =========================================================
   Weather Error
   ========================================================= */

function getFriendlyWeatherError(error) {

    if (
        error.message.includes(
            "Failed to fetch"
        )
    ) {

        return (
            "Could not connect to the Palm Mitra weather service. " +
            "Please make sure the FastAPI backend is running."
        );
    }

    return (
        error.message ||
        "Unable to load weather information."
    );
}


/* =========================================================
   Refresh Weather
   ========================================================= */

if (refreshWeatherButton) {

    refreshWeatherButton.addEventListener(
        "click",
        loadWeather
    );
}
/* =========================================================
   FARM ACTIVITIES
   ========================================================= */

const activityForm =
    document.getElementById("activityForm");

const activityList =
    document.getElementById("activityList");

const activitySaveMessage =
    document.getElementById("activitySaveMessage");

const totalActivities =
    document.getElementById("totalActivities");

const pendingActivities =
    document.getElementById("pendingActivities");

const completedActivities =
    document.getElementById("completedActivities");

const upcomingActivities =
    document.getElementById("upcomingActivities");


function getActivities() {

    const savedActivities =
        localStorage.getItem(
            "palmMitraActivities"
        );

    if (!savedActivities) {
        return [];
    }

    try {

        return JSON.parse(
            savedActivities
        );

    } catch (error) {

        console.error(
            "Could not load activities:",
            error
        );

        return [];
    }
}


function saveActivities(activities) {

    localStorage.setItem(
        "palmMitraActivities",
        JSON.stringify(activities)
    );
}


activityForm.addEventListener(
    "submit",
    function (event) {

        event.preventDefault();

        const name =
            document.getElementById(
                "activityName"
            ).value;

        const date =
            document.getElementById(
                "activityDate"
            ).value;

        const notes =
            document.getElementById(
                "activityNotes"
            ).value.trim();


        if (!name || !date) {

            activitySaveMessage.textContent =
                "Please select an activity and date.";

            return;
        }


        const activities =
            getActivities();


        const newActivity = {

            id:
                Date.now(),

            name:
                name,

            date:
                date,

            notes:
                notes,

            completed:
                false
        };


        activities.push(
            newActivity
        );


        saveActivities(
            activities
        );


        activityForm.reset();


        activitySaveMessage.textContent =
            "✓ Activity added successfully.";


        activitySaveMessage.style.color =
            "var(--primary)";


        renderActivities();

    });
        /* =========================================================
   AUTOMATIC FARM ACTIVITY SUGGESTIONS
   ========================================================= */

const recommendedActivities =
    document.getElementById(
        "recommendedActivities"
    );


async function generateFarmSuggestions() {

    if (!recommendedActivities) {
        return;
    }

    const token =
        localStorage.getItem("palmMitraToken");

    if (!token) {
        return;
    }


    let farm;

    try {

        const response =
            await fetch(
                `${API_URL}/api/farm`,
                {
                    method: "GET",
                    headers: {
                        "Authorization": `Bearer ${token}`
                    }
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            console.error(
                "Could not load farm profile:",
                data.detail || "Unknown error"
            );

            return;
        }


        farm =
            data.farm;


        if (!farm) {

            recommendedActivities.innerHTML = `

                <div class="empty-activities">

                    <span>
                        🌱
                    </span>

                    <p>
                        Complete your farm profile first.
                    </p>

                    <small>
                        Palm Mitra will generate suggestions
                        from your farm information.
                    </small>

                </div>

            `;

            return;
        }

    } catch (error) {

        console.error(
            "Could not load farm profile:",
            error
        );

        return;
    }


    const suggestions = [];


    /* -----------------------------------------------------
       Soil Testing
       ----------------------------------------------------- */

    if (
        !farm.soil ||
        farm.soil.trim() === "" ||  
        farm.soil.trim().toLowerCase() === "unknown"
    ) {

        suggestions.push({

            name:
                "Soil Testing",

            reason:
                "Your soil information has not been configured yet.",

            priority:
                "Important"

        });

    }


    /* -----------------------------------------------------
       Water & Drainage
       ----------------------------------------------------- */

    if (
        farm.waterSource
    ) {

        suggestions.push({

            name:
                "Water & Drainage Check",

            reason:
                `Verify that the ${farm.waterSource.toLowerCase()} water source and farm drainage are working properly.`,

            priority:
                "Important"

        });

    }


    /* -----------------------------------------------------
       Irrigation Monitoring
       ----------------------------------------------------- */

    if (
        farm.irrigation
    ) {

        suggestions.push({

            name:
                "Irrigation Monitoring",

            reason:
                `Monitor the farm's ${farm.irrigation.toLowerCase()} irrigation system and check soil moisture.`,

            priority:
                "Routine"

        });

    }


    /* -----------------------------------------------------
       Leaf Monitoring
       ----------------------------------------------------- */

    suggestions.push({

        name:
            "Leaf Monitoring",

        reason:
            "Regularly inspect palm leaves for unusual colour, spots or other visible changes.",

        priority:
            "Routine"

    });


    /* -----------------------------------------------------
       Pest & Disease Monitoring
       ----------------------------------------------------- */

    suggestions.push({

        name:
            "Pest & Disease Monitoring",

        reason:
            "Inspect palms regularly for insects, fungal symptoms and abnormal leaf patterns.",

        priority:
            "Routine"

    });


    /* -----------------------------------------------------
       Nutrient Management
       ----------------------------------------------------- */

    if (
    farm.soil &&
    farm.soil.trim() !== "" &&
    farm.soil.trim().toLowerCase() !== "unknown"
) {

        suggestions.push({

            name:
                "Nutrient Management",

            reason:
                "Review soil condition and nutrient requirements as part of routine farm management.",

            priority:
                "Routine"

        });

    }


    displayFarmSuggestions(
        suggestions
    );
}


function displayFarmSuggestions(
    suggestions
) {

    if (
        !recommendedActivities
    ) {
        return;
    }


    if (
        suggestions.length === 0
    ) {

        recommendedActivities.innerHTML = `

            <div class="empty-activities">

                <span>
                    ✅
                </span>

                <p>
                    No new suggestions right now.
                </p>

                <small>
                    Continue monitoring your plantation.
                </small>

            </div>

        `;

        return;
    }


    recommendedActivities.innerHTML =
        "";


    suggestions.forEach(
        function (suggestion) {

            const card =
                document.createElement(
                    "div"
                );


            card.className =
                "recommended-activity-item";


            card.innerHTML = `

                <div class="recommended-activity-info">

                    <div class="recommended-activity-title">
                        🌱 ${escapeHtml(suggestion.name)}
                    </div>

                    <p>
                        ${escapeHtml(suggestion.reason)}
                    </p>

                    <span class="recommended-priority">
                        ${escapeHtml(suggestion.priority)}
                    </span>

                </div>


                <button
                    type="button"
                    class="activity-action-button complete-activity-button"
                    onclick="addSuggestedActivity('${escapeHtml(suggestion.name)}')"
                >
                    + Add to Calendar
                </button>

            `;


            recommendedActivities.appendChild(
                card
            );

        }
    );
}


function addSuggestedActivity(
    activityName
) {

    const activities =
        getActivities();


    /* Prevent duplicate pending activities */

    const alreadyExists =
        activities.some(
            function (activity) {

                return (
                    activity.name ===
                        activityName &&
                    !activity.completed
                );

            }
        );


    if (alreadyExists) {

        alert(
            `"${activityName}" is already in your pending activities.`
        );

        return;
    }


    const today =
        new Date();


    const dateString =
        today.toISOString()
            .split("T")[0];


    const newActivity = {

        id:
            Date.now(),

        name:
            activityName,

        date:
            dateString,

        notes:
            "Suggested by Palm Mitra",

        completed:
            false
    };


    activities.push(
        newActivity
    );


    saveActivities(
        activities
    );


    renderActivities();


    alert(
        `"${activityName}" was added to your activity calendar.`
    );
}


generateFarmSuggestions();


function renderActivities() {

    const activities =
        getActivities();


    updateActivitySummary(
        activities
    );


    if (activities.length === 0) {

        activityList.innerHTML = `

            <div class="empty-activities">

                <span>
                    📅
                </span>

                <p>
                    No activities added yet.
                </p>

                <small>
                    Add your first farm activity above.
                </small>

            </div>

        `;

        return;
    }


    activities.sort(
        function (a, b) {

            return new Date(a.date) -
                new Date(b.date);

        }
    );


    activityList.innerHTML = "";


    activities.forEach(
        function (activity) {

            const item =
                document.createElement(
                    "div"
                );

            item.className =
                "activity-item";


            const status =
                activity.completed
                    ? "completed"
                    : "pending";


            const statusText =
                activity.completed
                    ? "Completed"
                    : "Pending";


            item.innerHTML = `

                <div class="activity-info">

                    <div class="activity-title">
                        ${escapeHtml(activity.name)}
                    </div>

                    <div class="activity-meta">

                        <span>
                            📅 ${formatActivityDate(activity.date)}
                        </span>

                        <span class="activity-status ${status}">
                            ${statusText}
                        </span>

                        ${
                            activity.notes
                                ? `<span>
                                    📝 ${escapeHtml(activity.notes)}
                                   </span>`
                                : ""
                        }

                    </div>

                </div>


                <div class="activity-actions">

                    ${
                        activity.completed
                            ? ""
                            : `
                                <button
                                    type="button"
                                    class="activity-action-button complete-activity-button"
                                    onclick="completeActivity(${activity.id})"
                                >
                                    ✓ Complete
                                </button>
                            `
                    }

                    <button
                        type="button"
                        class="activity-action-button delete-activity-button"
                        onclick="deleteActivity(${activity.id})"
                    >
                        Delete
                    </button>

                </div>

            `;


            activityList.appendChild(
                item
            );
        }
    );
}


function updateActivitySummary(
    activities
) {

    const total =
        activities.length;


    const completed =
        activities.filter(
            function (activity) {
                return activity.completed;
            }
        ).length;


    const pending =
        total - completed;


    const today =
        new Date();

    today.setHours(
        0, 0, 0, 0
    );


    const upcoming =
        activities.filter(
            function (activity) {

                if (activity.completed) {
                    return false;
                }

                const date =
                    new Date(
                        activity.date
                    );

                return date >= today;
            }
        ).length;


    totalActivities.textContent =
        total;

    pendingActivities.textContent =
        pending;

    completedActivities.textContent =
        completed;

    upcomingActivities.textContent =
        upcoming;
}


function completeActivity(
    activityId
) {

    const activities =
        getActivities();


    const activity =
        activities.find(
            function (item) {
                return item.id === activityId;
            }
        );


    if (!activity) return;


    activity.completed =
        true;


    saveActivities(
        activities
    );


    renderActivities();
}


function deleteActivity(
    activityId
) {

    const activities =
        getActivities();


    const updatedActivities =
        activities.filter(
            function (activity) {

                return activity.id !==
                    activityId;

            }
        );


    saveActivities(
        updatedActivities
    );


    renderActivities();
}


function formatActivityDate(
    dateString
) {

    const date =
        new Date(
            dateString + "T00:00:00"
        );


    return date.toLocaleDateString(
        "en-IN",
        {
            day: "numeric",
            month: "short",
            year: "numeric"
        }
    );
}


function escapeHtml(
    value
) {

    const div =
        document.createElement(
            "div"
        );

    div.textContent =
        value;

    return div.innerHTML;
}


renderActivities();

// =========================================================
// PALM MITRA AI CHAT
// =========================================================

const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatMessages = document.getElementById("chatMessages");
const chatSendButton = document.getElementById("chatSendButton");
const chatLoading = document.getElementById("chatLoading");

if (chatForm) {

    chatForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const message = chatInput.value.trim();

        if (!message) {
            return;
        }

        // Show user's message
        const userMessage = document.createElement("div");

        userMessage.className = "chat-message user-message";

        userMessage.innerHTML = `
            <div class="message-content">
                <p>${message}</p>
            </div>
        `;

        chatMessages.appendChild(userMessage);

        // Clear input
        chatInput.value = "";

        // Scroll to latest message
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Disable button while waiting
        chatSendButton.disabled = true;
        chatSendButton.textContent = "Sending...";

        if (chatLoading) {
            chatLoading.classList.remove("hidden");
        }

        try {

            const response = await fetch(
                `${API_URL}/api/chat`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        message: message
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail || "Failed to get response"
                );
            }

            // Show Palm Mitra response
            const assistantMessage =
                document.createElement("div");

            assistantMessage.className =
                "chat-message assistant-message";

            assistantMessage.innerHTML = `
                <div class="message-content">
                    <p>${data.response}</p>
                </div>
            `;

            chatMessages.appendChild(assistantMessage);

            chatMessages.scrollTop =
                chatMessages.scrollHeight;

        } catch (error) {

            console.error("Chat error:", error);

            const errorMessage =
                document.createElement("div");

            errorMessage.className =
                "chat-message assistant-message";

            errorMessage.innerHTML = `
                <div class="message-content">
                    <p>
                        Sorry, I couldn't connect to Palm Mitra.
                        Please make sure the backend server is running.
                    </p>
                </div>
            `;

            chatMessages.appendChild(errorMessage);

        } finally {

            chatSendButton.disabled = false;
            chatSendButton.textContent = "Send";

            if (chatLoading) {
                chatLoading.classList.add("hidden");
            }

            chatInput.focus();

            chatMessages.scrollTop =
                chatMessages.scrollHeight;
        }

    });

}

/* =========================
   USER + LOGOUT
========================= */

async function loadLoggedInUser() {

    const user = await verifyLogin();

    if (!user) {
        return;
    }

}


/* =========================
   LOGOUT
========================= */

const logoutButton =
    document.getElementById("logoutButton");

if (logoutButton) {

    logoutButton.addEventListener(
        "click",
        function () {

            localStorage.removeItem(
                "palmMitraToken"
            );

            localStorage.removeItem(
                "palmMitraUser"
            );

            window.location.href =
                "login.html";
        }
    );
}

/* =========================================================
   MULTILINGUAL SUPPORT
   ========================================================= */

const languageSelect =
    document.getElementById("languageSelect");


async function loadLanguage(language) {

    try {

        const response =
            await 
            fetch(`translations/${language}.json`)

        if (!response.ok) {

            throw new Error(
                `Could not load ${language} translation.`
            );
        }

        const translations =
            await response.json();


        /*
         * Get translated value from nested JSON
         *
         * Example:
         * "farm.placeholders.farmName"
         */
        function getTranslation(key) {

            const keys = key.split(".");

            let value = translations;

            keys.forEach(function (part) {

                if (
                    value !== undefined &&
                    value !== null
                ) {
                    value = value[part];
                }

            });

            return value;
        }


        /*
         * Translate normal text
         */
        document
            .querySelectorAll("[data-i18n]")
            .forEach(function (element) {

                const key =
                    element.getAttribute(
                        "data-i18n"
                    );

                const value =
                    getTranslation(key);

                if (
                    value !== undefined &&
                    value !== null
                ) {

                    element.textContent = value;

                }

            });


        /*
         * Translate input placeholders
         */
        document
            .querySelectorAll(
                "[data-i18n-placeholder]"
            )
            .forEach(function (element) {

                const key =
                    element.getAttribute(
                        "data-i18n-placeholder"
                    );

                const value =
                    getTranslation(key);

                if (
                    value !== undefined &&
                    value !== null
                ) {

                    element.placeholder = value;

                }

            });


        /*
         * Translate alt text
         */
        document
            .querySelectorAll(
                "[data-i18n-alt]"
            )
            .forEach(function (element) {

                const key =
                    element.getAttribute(
                        "data-i18n-alt"
                    );

                const value =
                    getTranslation(key);

                if (
                    value !== undefined &&
                    value !== null
                ) {

                    element.alt = value;

                }

            });


        console.log(
            "Language applied:",
            language
        );

    } catch (error) {

        console.error(
            "Language loading error:",
            error
        );

    }

}

if (languageSelect) {

    languageSelect.addEventListener(
        "change",
        function () {

            loadLanguage(
                languageSelect.value
            );

        }
    );

}



