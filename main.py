from fastapi import FastAPI, UploadFile, File, Form
from brain import get_answer, image_answer

app = FastAPI(title="Rahul AI API")


@app.get("/")
def home():
    return {
        "message": "Rahul AI API chal rahi hai!"
    }


@app.post("/chat")
async def chat(data: dict):

    message = data.get("message", "").strip()

    if not message:
        return {
            "reply": "Dost, apna question likho."
        }

    reply = get_answer(message)

    return {
        "reply": reply
    }


@app.post("/chat-image")
async def chat_image(
    image: UploadFile = File(...),
    message: str = Form("")
):

    try:
        image_bytes = await image.read()

        if not image.content_type or not image.content_type.startswith("image/"):
            return {"reply": "Please ek valid image bhejo."}

        reply = image_answer(
            message,
            image_bytes,
            image.content_type
        )

        return {
            "reply": reply
        }

    except Exception as e:
        return {
            "reply": f"Image AI Error: {str(e)}"
        }
