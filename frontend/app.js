const API_URL = "";

const fileInput = document.getElementById("fileInput");
const uploadButton = document.getElementById("uploadButton");
const uploadStatus = document.getElementById("uploadStatus");

const questionInput = document.getElementById("questionInput");
const topK = document.getElementById("topK");
const askButton = document.getElementById("askButton");
const chatStatus = document.getElementById("chatStatus");

const answerPanel = document.getElementById("answerPanel");
const answerText = document.getElementById("answerText");
const sourcesList = document.getElementById("sourcesList");
const metrics = document.getElementById("metrics");


function showMessage(element, message, type) {
    element.textContent = message;
    element.className = `message ${type}`;
}


async function readResponse(response) {
    const data = await response.json();

    if (!response.ok) {
        const detail = data.detail;
        const message = typeof detail === "string"
            ? detail
            : detail
                ? JSON.stringify(detail)
                : "Ошибка выполнения запроса";

        throw new Error(message);
    }

    return data;
}


// Загрузка документа
uploadButton.addEventListener("click", async () => {
    const file = fileInput.files[0];

    if (!file) {
        showMessage(
            uploadStatus,
            "Выберите файл для загрузки.",
            "error"
        );
        return;
    }

    uploadButton.disabled = true;
    showMessage(uploadStatus, "Документ обрабатывается...", "");

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch(`${API_URL}/documents/upload`, {
            method: "POST",
            body: formData
        });

        const data = await readResponse(response);

        showMessage(
            uploadStatus,
            `Документ ${data.filename} успешно загружен. ` +
            `Фрагментов: ${data.result.chunks_count}.`,
            "success"
        );

        fileInput.value = "";

    } catch (error) {
        showMessage(uploadStatus, error.message, "error");
    } finally {
        uploadButton.disabled = false;
    }
});


// Отправка вопроса в RAG-систему
askButton.addEventListener("click", async () => {
    const question = questionInput.value.trim();

    if (question.length < 3) {
        showMessage(
            chatStatus,
            "Введите вопрос длиной не менее 3 символов.",
            "error"
        );
        return;
    }

    askButton.disabled = true;
    answerPanel.classList.add("hidden");

    showMessage(
        chatStatus,
        "Выполняется поиск и генерация ответа...",
        ""
    );

    try {
        const response = await fetch(`${API_URL}/chat/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question,
                top_k: Number(topK.value)
            })
        });

        const data = await readResponse(response);

        answerText.textContent = data.answer || "";

        sourcesList.replaceChildren();

        (data.sources || []).forEach((source, index) => {
            const sourceBlock = document.createElement("div");
            sourceBlock.className = "source";

            const heading = document.createElement("strong");
            heading.textContent = `Источник ${index + 1}`;

            const documentId = document.createElement("p");
            documentId.textContent =
                `Document ID: ${source.document_id}`;

            const chunkId = document.createElement("p");
            chunkId.textContent =
                `Chunk ID: ${source.chunk_id}`;

            const distance = document.createElement("p");
            distance.textContent =
                `Косинусное расстояние: ` +
                `${Number(source.distance).toFixed(4)}`;

            const text = document.createElement("p");
            text.textContent = source.text || "";

            sourceBlock.append(
                heading,
                documentId,
                chunkId,
                distance,
                text
            );

            sourcesList.appendChild(sourceBlock);
        });

        metrics.textContent =
            `Найдено фрагментов: ${data.retrieved_chunks} | ` +
            `Время выполнения: ${data.response_time_ms} мс | ` +
            `Недостаточно данных: ${data.insufficient_data ? "Да" : "Нет"}`;

        answerPanel.classList.remove("hidden");

        showMessage(
            chatStatus,
            "Ответ успешно сформирован.",
            "success"
        );

    } catch (error) {
        showMessage(chatStatus, error.message, "error");
    } finally {
        askButton.disabled = false;
    }
});
