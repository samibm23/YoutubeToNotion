import google.generativeai as palm
from langchain_community.document_loaders import YoutubeLoader
import config


palm.configure(api_key=config.API_Key)
models = [
    m for m in palm.list_models() if "generateText" in m.supported_generation_methods
]
model = models[0].name

def summarize(text, model):
    prompt = """I will give you a text extracted from a youtube video, 
    i want you to extract key points that text explained.
     please begin each keypoint with a title in this format (## title ) then in another line you put the explenation of the concept in this format(*line1
     *line2) \n"""
    prompt += "\n" + text

    completion = palm.generate_text(
        model=model,
        prompt=prompt,
        # The degree of randomness of the generated text
        temperature=0.2,
        # The maximum length of the response
        max_output_tokens=1000,
    )

    return completion.result


def extract_youtube(video_url):
    loader = YoutubeLoader.from_youtube_url(
        video_url, add_video_info=True,
        language=["en", "id"],
        translation="en",
    )
    text  = loader.load()
    yn_data = {
        "notion_page": summarize(text[0].page_content,model),
        "title": text[0].metadata["title"],
        "author": text[0].metadata["author"]
                    }
    return yn_data

